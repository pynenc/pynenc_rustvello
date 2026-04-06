"""Concrete orchestrator subclasses per backend (mixed and native).

Also hosts ``_RustvelloNativeOrchestrator`` (the base class for native
hot-path subclasses) so that ``orchestrator.py`` stays within the 500-line
hard limit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pynenc.invocation import DistributedInvocation
from pynenc.invocation.status import InvocationStatus

from pynenc_rustvello.orchestrator import _RustvelloOrchestrator

if TYPE_CHECKING:
    from pynenc.app import Pynenc
    from pynenc.identifiers import InvocationId


# ---------------------------------------------------------------------------
# Native orchestrator base — single FFI call for hot-path coordination
# ---------------------------------------------------------------------------


class _RustvelloNativeOrchestrator(_RustvelloOrchestrator):
    """Orchestrator that uses single FFI calls for hot-path coordination.

    When all backends are Rust-native, the 5 hottest operations run as
    composite Rust calls instead of chaining individual backend calls
    through Python.  The shared ``PyRustvello`` instance (created lazily
    via ``from_backends``) ensures that composites and individual
    adapters share the same underlying Rust state.

    .. warning::

        This class **bypasses** ``BaseOrchestrator.set_invocation_status()``
        and the other public methods it overrides.  The Rust composites
        replicate all side-effects (history recording, waiter release,
        auto-purge scheduling, trigger evaluation) internally, so the
        Python-side hook chain in ``BaseOrchestrator`` is intentionally
        skipped.  If ``BaseOrchestrator`` gains new hooks, they must be
        mirrored in the corresponding Rust ``OrchestratorCoordinator``
        methods or the override must be removed.

    .. note::

        ``from_backends()`` accepts any backend variant (mem, sqlite,
        postgres, redis, mongo). All backends expose identical PyO3 APIs.
    """

    _rust_app: Any = None

    def _ensure_rust_app(self) -> None:
        """Lazily create a shared ``PyRustvello`` from pynenc's backend adapters."""
        if self._rust_app is not None:
            return
        from rustvello import Rustvello

        self._rust_app = Rustvello.from_backends(
            self._rust,
            self.app.state_backend._rust,
            self.app.broker._rust,
            self.app.trigger._rust,
            self.app.client_data_store._rust,
        )

    # ------------------------------------------------------------------
    # Hot-path overrides  (1 FFI call each)
    # ------------------------------------------------------------------

    def set_invocation_status(
        self,
        invocation_id: InvocationId,
        status: InvocationStatus,
        runner_ctx: Any,
    ) -> None:
        from pynenc.exceptions import (
            InvocationStatusOwnershipError,
            InvocationStatusTransitionError,
        )
        from rustvello.rustvello import StatusOwnershipError, StatusTransitionError

        self._ensure_rust_app()
        try:
            self._rust_app.set_invocation_status(str(invocation_id), status.name, runner_ctx.runner_id)
        except StatusOwnershipError as e:
            raise InvocationStatusOwnershipError(
                from_status=InvocationStatus[e.from_status],
                to_status=InvocationStatus[e.to_status],
                current_owner=e.current_owner,
                attempted_owner=e.attempted_owner,
                reason=e.reason,
            ) from e
        except StatusTransitionError as e:
            raise InvocationStatusTransitionError(
                from_status=InvocationStatus[e.from_status],
                to_status=InvocationStatus[e.to_status],
                allowed_statuses=frozenset(InvocationStatus[s] for s in e.allowed_statuses),
            ) from e

    def set_invocation_result(
        self,
        invocation: DistributedInvocation,
        result: Any,
        runner_ctx: Any,
    ) -> None:
        self._ensure_rust_app()
        serialized = self.app.client_data_store.serialize(result)
        self._rust_app.set_invocation_result(str(invocation.invocation_id), serialized, runner_ctx.runner_id)

    def set_invocation_exception(
        self,
        invocation: DistributedInvocation,
        exception: Exception,
        runner_ctx: Any,
    ) -> None:
        self._ensure_rust_app()
        serialized = self.app.state_backend.serialize_exception(exception)
        self._rust_app.set_invocation_exception(
            str(invocation.invocation_id),
            "SerializedException",
            serialized,
            runner_ctx.runner_id,
        )

    def set_invocation_retry(
        self,
        invocation_id: InvocationId,
        exception: Exception,
        runner_ctx: Any,
    ) -> None:
        self._ensure_rust_app()
        self._rust_app.set_invocation_retry(str(invocation_id), runner_ctx.runner_id)

    def reroute_invocations(
        self,
        invocations_to_reroute: set[InvocationId],
        runner_ctx: Any,
    ) -> None:
        self._ensure_rust_app()
        inv_ids = [str(inv_id) for inv_id in invocations_to_reroute]
        self._rust_app.reroute_invocations(inv_ids, runner_ctx.runner_id)

    def route_call(self, call: Any) -> Any:
        """Route a call using the Rust composite when possible.

        Falls back to the Python implementation for KEYS concurrency control
        with on_diff_non_key_args_raise (requires Python-side error handling).
        """
        from pynenc import context
        from pynenc.conf.config_task import ConcurrencyControlType
        from pynenc.exceptions import (
            InvocationConcurrencyWithDifferentArgumentsError,
        )
        from pynenc.invocation.dist_invocation import (
            DistributedInvocation,
            ReusedInvocation,
        )

        self._ensure_rust_app()
        runner_ctx = context.get_or_create_runner_context(self.app.app_id)
        runner_id = runner_ctx.runner_id

        task = call.task
        task_id = task.task_id
        reg_cc = task.conf.registration_concurrency
        run_cc = task.conf.running_concurrency
        index_cc = reg_cc != ConcurrencyControlType.DISABLED or run_cc != ConcurrencyControlType.DISABLED

        # Generate new invocation id (same as Python path)
        parent_invocation = context.get_dist_invocation_context(self.app.app_id)
        new_invocation = DistributedInvocation.from_parent(call, parent_invocation)
        new_inv_id = str(new_invocation.invocation_id)

        args = dict(call.serialized_arguments) if hasattr(call, "serialized_arguments") else {}
        cc_args = (
            dict(call.serialized_args_for_concurrency_check)
            if call.serialized_args_for_concurrency_check is not None
            else None
        )

        kind, inv_id_str, extra = self._rust_app.route_call(
            new_inv_id,
            str(task_id.module),
            str(task_id.func_name),
            args,
            cc_args,
            reg_cc.name,
            index_cc,
            runner_id,
        )

        if kind == "new":
            # Rust created the invocation but doesn't know about Python
            # workflow tracking — persist the full DTO with workflow info.
            self.app.state_backend.upsert_invocations([new_invocation])
            self.app.logger.info(f"invocation:{inv_id_str} ROUTED")
            return new_invocation

        # Reused — fetch the existing invocation from state backend
        from pynenc.identifiers.invocation_id import InvocationId as PynencInvId

        existing_inv_id = PynencInvId(inv_id_str)
        existing_inv = self.app.state_backend.get_invocation(existing_inv_id)
        if existing_inv is None:
            # Race: invocation disappeared — fall back to new
            return super().route_call(call)

        if kind == "reused":
            return ReusedInvocation(existing_inv)

        # kind == "reused_diff_call"
        if task.conf.on_diff_non_key_args_raise:
            raise InvocationConcurrencyWithDifferentArgumentsError.from_call_mismatch(
                existing_invocation=existing_inv, new_call=call
            )
        return ReusedInvocation(existing_inv, call.arguments)

    # NOTE: get_invocations_to_run is NOT overridden here.
    # The Rust composite's CC logic requires the task_registry, which is
    # empty in from_backends()-created RustvelloApp instances (tasks are
    # only registered in pynenc's Python app._tasks).  We fall back to
    # pynenc's Python CC logic for now.

    def check_atomic_services(self, runner_id: str) -> list[str] | None:
        """Run full atomic service check via a single Rust composite call.

        Combines heartbeat registration, distributed coordination algorithm,
        trigger loop evaluation, and execution recording into one FFI call.

        Returns ``None`` if this runner is not authorized to run now,
        or a list of created invocation ID strings if the trigger loop ran.
        """
        self._ensure_rust_app()
        conf = self.app.conf
        return self._rust_app.check_atomic_services(
            runner_id,
            conf.atomic_service_interval_minutes,
            conf.atomic_service_spread_margin_minutes,
            conf.runner_considered_dead_after_minutes * 60,
        )


# ---------------------------------------------------------------------------
# Mixed-mode subclasses (Python-level coordination)
# ---------------------------------------------------------------------------


class RustMemOrchestrator(_RustvelloOrchestrator):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustMemOrchestrator as _Inner

        super().__init__(app, _Inner())


class RustSqliteOrchestrator(_RustvelloOrchestrator):
    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustSqliteOrchestrator as _Inner

        if db is None:
            from pynenc_rustvello.broker import _get_or_create_sqlite_db

            db = _get_or_create_sqlite_db(app)
        super().__init__(app, _Inner(db))


class RustPostgresOrchestrator(_RustvelloOrchestrator):
    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustPostgresOrchestrator as _Inner

        if db is None:
            from pynenc_rustvello.broker import _get_or_create_postgres_db

            db = _get_or_create_postgres_db(app)
        super().__init__(app, _Inner(db))


class RustRedisOrchestrator(_RustvelloOrchestrator):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustRedisOrchestrator as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_redis_pool

            pool = _get_or_create_redis_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongoOrchestrator(_RustvelloOrchestrator):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongoOrchestrator as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_mongo_pool

            pool = _get_or_create_mongo_pool(app)
        super().__init__(app, _Inner(pool))


# ---------------------------------------------------------------------------
# Native subclasses (single FFI call hot-paths)
# ---------------------------------------------------------------------------


class RustMemNativeOrchestrator(_RustvelloNativeOrchestrator):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustMemOrchestrator as _Inner

        super().__init__(app, _Inner())


class RustSqliteNativeOrchestrator(_RustvelloNativeOrchestrator):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustSqliteOrchestrator as _Inner

        from pynenc_rustvello.broker import _get_or_create_sqlite_db

        db = _get_or_create_sqlite_db(app)
        super().__init__(app, _Inner(db))


class RustPostgresNativeOrchestrator(_RustvelloNativeOrchestrator):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustPostgresOrchestrator as _Inner

        from pynenc_rustvello.broker import _get_or_create_postgres_db

        db = _get_or_create_postgres_db(app)
        super().__init__(app, _Inner(db))


class RustRedisNativeOrchestrator(_RustvelloNativeOrchestrator):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustRedisOrchestrator as _Inner

        from pynenc_rustvello.broker import _get_or_create_redis_pool

        pool = _get_or_create_redis_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongoNativeOrchestrator(_RustvelloNativeOrchestrator):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustMongoOrchestrator as _Inner

        from pynenc_rustvello.broker import _get_or_create_mongo_pool

        pool = _get_or_create_mongo_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongo3Orchestrator(_RustvelloOrchestrator):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongo3Orchestrator as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_mongo3_pool

            pool = _get_or_create_mongo3_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongo3NativeOrchestrator(_RustvelloNativeOrchestrator):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustMongo3Orchestrator as _Inner

        from pynenc_rustvello.broker import _get_or_create_mongo3_pool

        pool = _get_or_create_mongo3_pool(app)
        super().__init__(app, _Inner(pool))
