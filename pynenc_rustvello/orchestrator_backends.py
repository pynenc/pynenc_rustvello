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


def _routing_only_task(args_json: str) -> str:
    """Placeholder body for catalog registrations; pynenc's own runner executes the task."""
    raise RuntimeError(
        "pynenc-rustvello registers tasks in the Rust catalog for routing only; "
        f"execution belongs to pynenc (args: {args_json[:80]})"
    )


def _catalog_errors() -> tuple[type[BaseException], ...]:
    """Rust errors meaning the catalog cannot route this task; pynenc's Python path takes over."""
    import rustvello.rustvello as _rv

    names = ("TaskError", "TaskNotRegisteredError", "TaskNotFoundError")
    return tuple(getattr(_rv, name) for name in names if hasattr(_rv, name))


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
    _native_unavailable: bool = False
    _registered_task_keys: set[str] | None = None

    def _ensure_rust_app(self) -> bool:
        """Lazily create a shared ``PyRustvello`` from pynenc's backend adapters.

        Returns False when rustvello cannot compose these backends (for example a
        broker class its ``from_backends`` extractor does not know); the hot paths
        then run pynenc's Python-coordinated implementation instead of failing.

        Every pynenc task known to the app is registered in the Rust task catalog
        with its effective queue and priority: the retry and reroute composites
        resolve routing from that catalog, so without it hyper-queue retries would
        fall back to the default queue.
        """
        if self._rust_app is not None:
            return True
        if self._native_unavailable:
            return False
        from rustvello import Rustvello

        try:
            rust_app = Rustvello.from_backends(
                self._rust,
                self.app.state_backend._rust,
                self.app.broker._rust,
                self.app.trigger._rust,
                self.app.client_data_store._rust,
            )
        except TypeError as exc:
            self._native_unavailable = True
            self.app.logger.warning(
                "rustvello native composites disabled, using Python coordination: %s",
                exc,
            )
            return False
        self._rust_app = rust_app
        self._registered_task_keys = set()
        for task in list(self.app.tasks.values()):
            self._ensure_task_registered(task)
        return True

    def _disable_native(self, exc: BaseException) -> None:
        """Stop using composites for this app; pynenc's Python coordination takes over."""
        self._native_unavailable = True
        self._rust_app = None
        self.app.logger.warning(
            "rustvello native composites disabled, using Python coordination: %s", exc
        )

    def _ensure_task_registered(self, task: Any) -> None:
        """Mirror one pynenc task's routing (queue, priority) into the Rust catalog."""
        from rustvello import TaskConfig

        keys = self._registered_task_keys
        assert keys is not None
        key = task.task_id.key
        if key in keys:
            return
        try:
            self._rust_app.register_task(
                str(task.task_id.module),
                str(task.task_id.func_name),
                _routing_only_task,
                TaskConfig(queue=task.broker_queue, priority=task.broker_priority),
            )
        except ValueError:
            # Already present in the catalog (e.g. another adapter instance registered it).
            pass
        keys.add(key)

    def _ensure_invocation_task_registered(self, invocation_id: InvocationId) -> None:
        """Register the task behind ``invocation_id`` when only the id is known (retry, reroute)."""
        try:
            invocation = self.app.state_backend.get_invocation(invocation_id)
        except Exception:  # noqa: BLE001 - missing invocation: the composite reports it itself
            return
        if invocation is not None:
            self._ensure_task_registered(invocation.task)

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
        from rustvello.rustvello import (
            ConfigurationError,
            StatusOwnershipError,
            StatusTransitionError,
        )

        if not self._ensure_rust_app():
            super().set_invocation_status(invocation_id, status, runner_ctx)
            return
        try:
            self._rust_app.set_invocation_status(
                str(invocation_id), status.name, runner_ctx.runner_id
            )
        except ConfigurationError as e:
            # e.g. "mixed backends are not qualified" for durable publication: fall back for good
            self._disable_native(e)
            super().set_invocation_status(invocation_id, status, runner_ctx)
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
                allowed_statuses=frozenset(
                    InvocationStatus[s] for s in e.allowed_statuses
                ),
            ) from e

    def set_invocation_result(
        self,
        invocation: DistributedInvocation,
        result: Any,
        runner_ctx: Any,
    ) -> None:
        if not self._ensure_rust_app():
            super().set_invocation_result(invocation, result, runner_ctx)
            return
        from rustvello.rustvello import ConfigurationError

        serialized = self.app.client_data_store.serialize(result)
        try:
            self._rust_app.set_invocation_result(
                str(invocation.invocation_id), serialized, runner_ctx.runner_id
            )
        except ConfigurationError as e:
            self._disable_native(e)
            super().set_invocation_result(invocation, result, runner_ctx)

    def set_invocation_exception(
        self,
        invocation: DistributedInvocation,
        exception: Exception,
        runner_ctx: Any,
    ) -> None:
        if not self._ensure_rust_app():
            super().set_invocation_exception(invocation, exception, runner_ctx)
            return
        from rustvello.rustvello import ConfigurationError

        serialized = self.app.state_backend.serialize_exception(exception)
        try:
            self._rust_app.set_invocation_exception(
                str(invocation.invocation_id),
                "SerializedException",
                serialized,
                runner_ctx.runner_id,
            )
        except ConfigurationError as e:
            self._disable_native(e)
            super().set_invocation_exception(invocation, exception, runner_ctx)

    def set_invocation_retry(
        self,
        invocation: DistributedInvocation,
        exception: Exception,
        runner_ctx: Any,
    ) -> None:
        if not self._ensure_rust_app():
            super().set_invocation_retry(invocation, exception, runner_ctx)
            return
        from rustvello.rustvello import ConfigurationError

        self._ensure_task_registered(invocation.task)
        try:
            self._rust_app.set_invocation_retry(
                str(invocation.invocation_id), runner_ctx.runner_id
            )
        except ConfigurationError as e:
            self._disable_native(e)
            super().set_invocation_retry(invocation, exception, runner_ctx)
        except _catalog_errors():
            # Task unknown to the Rust catalog: let pynenc route the retry with its own queue lookup.
            super().set_invocation_retry(invocation, exception, runner_ctx)

    def reroute_invocations(
        self,
        invocations_to_reroute: set[InvocationId],
        runner_ctx: Any,
    ) -> None:
        if not self._ensure_rust_app():
            super().reroute_invocations(invocations_to_reroute, runner_ctx)
            return
        for inv_id in invocations_to_reroute:
            self._ensure_invocation_task_registered(inv_id)
        from rustvello.rustvello import ConfigurationError

        inv_ids = [str(inv_id) for inv_id in invocations_to_reroute]
        try:
            self._rust_app.reroute_invocations(inv_ids, runner_ctx.runner_id)
        except ConfigurationError as e:
            self._disable_native(e)
            super().reroute_invocations(invocations_to_reroute, runner_ctx)
        except _catalog_errors():
            super().reroute_invocations(invocations_to_reroute, runner_ctx)

    # route_call is intentionally NOT overridden: pynenc 0.4 persists the new invocation before
    # routing, which rustvello's durable-submission check rejects as a "legacy" id. pynenc's
    # route_call routes through the queue-aware broker adapter, so nothing is lost but one FFI hop.


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
