"""Pynenc-compatible orchestrators backed by Rust backends."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from time import time
from typing import TYPE_CHECKING, Any

from pynenc.invocation.status import InvocationStatus, InvocationStatusRecord
from pynenc.orchestrator.base_orchestrator import BaseBlockingControl, BaseOrchestrator

if TYPE_CHECKING:
    from pynenc.app import Pynenc
    from pynenc.identifiers.call_id import CallId
    from pynenc.identifiers.invocation_id import InvocationId
    from pynenc.identifiers.task_id import TaskId
    from pynenc.invocation.dist_invocation import DistributedInvocation
    from pynenc.orchestrator.atomic_service import ActiveRunnerInfo
    from pynenc.task import Task
    from pynenc.types import Params, Result


def _record_from_rust(status_str: str, runner_id: str | None, ts: float) -> InvocationStatusRecord:
    """Build a pynenc InvocationStatusRecord from Rust return values."""
    return InvocationStatusRecord(
        status=InvocationStatus[status_str],
        runner_id=runner_id,
        timestamp=datetime.fromtimestamp(ts, tz=UTC),
    )


class _RustBlockingControl(BaseBlockingControl):
    """Blocking control backed by a Rust orchestrator's set_waiting_for / release_waiters."""

    def __init__(self, rust_orch: Any) -> None:
        self._rust = rust_orch

    def waiting_for_results(
        self,
        caller_invocation_id: InvocationId,
        result_invocation_ids: list[InvocationId],
    ) -> None:
        for rid in result_invocation_ids:
            self._rust.set_waiting_for(str(caller_invocation_id), str(rid))

    def release_waiters(self, waited_invocation_id: InvocationId) -> None:
        self._rust.release_waiters(str(waited_invocation_id))

    def get_blocking_invocations(self, max_num_invocations: int) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        for inv_id_str in self._rust.get_blocking_invocations(max_num_invocations):
            yield InvocationId(inv_id_str)


class _RustvelloOrchestrator(BaseOrchestrator):
    """Base orchestrator backed by any Rust orchestrator object.

    Delegates all state — status tracking, invocation indexing, retry
    counters, heartbeat management, call-id mapping, concurrency-control
    argument indexing, and auto-purge — entirely to the Rust core.
    The adapter holds zero local state.
    """

    def __init__(self, app: Pynenc, rust_orch: Any) -> None:
        super().__init__(app)
        self._rust = rust_orch
        self._blocking = _RustBlockingControl(self._rust)

    # ------------------------------------------------------------------
    # Registration — delegated to Rust
    # ------------------------------------------------------------------

    def _register_new_invocations(
        self,
        invocations: list[DistributedInvocation[Params, Result]],
        runner_id: str | None = None,
    ) -> InvocationStatusRecord:
        record: InvocationStatusRecord | None = None
        for inv in invocations:
            inv_id = str(inv.invocation_id)
            task_id = inv.call.task.task_id
            args = dict(inv.call.serialized_arguments) if hasattr(inv.call, "serialized_arguments") else {}
            status_str, rid, ts = self._rust.register_invocation_with_id(
                inv_id,
                str(task_id.module),
                str(task_id.func_name),
                args,
                runner_id,
            )
            if record is None:
                record = _record_from_rust(status_str, rid, ts)
        assert record is not None
        return record

    # ------------------------------------------------------------------
    # Status management — delegated to Rust
    # ------------------------------------------------------------------

    def get_invocation_status_record(self, invocation_id: InvocationId) -> InvocationStatusRecord:
        status_str, runner_id, ts = self._rust.get_invocation_status(str(invocation_id))
        return _record_from_rust(status_str, runner_id, ts)

    def _atomic_status_transition(
        self,
        invocation_id: InvocationId,
        status: InvocationStatus,
        runner_id: str | None = None,
    ) -> InvocationStatusRecord:
        from pynenc.exceptions import (
            InvocationStatusOwnershipError,
            InvocationStatusTransitionError,
        )
        from rustvello.rustvello import StatusOwnershipError, StatusTransitionError

        inv_id = str(invocation_id)
        try:
            status_str, rid, ts = self._rust.set_invocation_status(inv_id, status.name, runner_id)
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
        return _record_from_rust(status_str, rid, ts)

    # ------------------------------------------------------------------
    # Query operations — delegated to Rust
    # ------------------------------------------------------------------

    def get_existing_invocations(
        self,
        task: Task[Params, Result],
        key_serialized_arguments: dict[str, str] | None = None,
        statuses: list[InvocationStatus] | None = None,
    ) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        task_id = task.task_id
        status_names = [s.name for s in statuses] if statuses else []
        cc_args = key_serialized_arguments  # None for task-level CC
        inv_ids: list[str] = self._rust.get_existing_invocations(
            str(task_id.module),
            str(task_id.func_name),
            status_names,
            cc_args=cc_args,
        )
        for inv_id in inv_ids:
            yield InvocationId(inv_id)

    def get_task_invocation_ids(self, task_id: TaskId) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        for inv_id in self._rust.get_invocations_by_task(str(task_id.module), str(task_id.func_name)):
            yield InvocationId(inv_id)

    def get_invocation_ids_paginated(
        self,
        task_id: TaskId | None = None,
        statuses: list[InvocationStatus] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        task_module = str(task_id.module) if task_id else None
        task_name = str(task_id.func_name) if task_id else None
        status_strs = [s.name for s in statuses] if statuses else None
        ids = self._rust.get_invocation_ids_paginated(task_module, task_name, status_strs, limit, offset)
        return [InvocationId(i) for i in ids]

    def count_invocations(
        self,
        task_id: TaskId | None = None,
        statuses: list[InvocationStatus] | None = None,
    ) -> int:
        task_module = str(task_id.module) if task_id else None
        task_name = str(task_id.func_name) if task_id else None
        status_strs = [s.name for s in statuses] if statuses else None
        return self._rust.count_invocations(task_module, task_name, status_strs)

    def get_call_invocation_ids(self, call_id: CallId) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        for inv_id in self._rust.get_invocations_by_call(str(call_id)):
            yield InvocationId(inv_id)

    # ------------------------------------------------------------------
    # Concurrency control — delegated to Rust
    # ------------------------------------------------------------------

    def index_arguments_for_concurrency_control(self, invocation: DistributedInvocation[Params, Result]) -> None:
        inv_id = str(invocation.invocation_id)
        task_id = invocation.call.task.task_id
        # Index ALL serialized arguments (not just CC key args) so that
        # get_existing_invocations can filter by any argument, matching
        # pynenc's MemOrchestrator behaviour.
        args = invocation.call.serialized_arguments
        cc_args = dict(args) if args else None
        self._rust.index_for_concurrency_control(inv_id, str(task_id.module), str(task_id.func_name), cc_args)

    # ------------------------------------------------------------------
    # Auto purge — delegated to Rust
    # ------------------------------------------------------------------

    def set_up_invocation_auto_purge(self, invocation_id: InvocationId) -> None:
        self._rust.schedule_auto_purge(str(invocation_id))

    def auto_purge(self) -> None:
        max_age_secs = int(self.app.orchestrator.conf.auto_final_invocation_purge_hours * 3600)
        purged_ids = self._rust.run_auto_purge(max_age_secs)
        for inv_id in purged_ids:
            from pynenc.identifiers.invocation_id import InvocationId

            self.release_waiters(InvocationId(inv_id))

    # ------------------------------------------------------------------
    # Retries — delegated to Rust
    # ------------------------------------------------------------------

    def increment_invocation_retries(self, invocation_id: InvocationId) -> None:
        self._rust.increment_invocation_retries(str(invocation_id))

    def get_invocation_retries(self, invocation_id: InvocationId) -> int:
        import rustvello as _rustvello

        # Fast path: read from Rust thread-local when called from inside a
        # spawn_blocking task to avoid nested block_on deadlocks.
        num_retries = _rustvello.get_current_num_retries()
        if num_retries is not None:
            return num_retries
        return self._rust.get_invocation_retries(str(invocation_id))

    # ------------------------------------------------------------------
    # Status filtering — delegated to Rust
    # ------------------------------------------------------------------

    def filter_by_status(
        self,
        invocation_ids: list[InvocationId],
        status_filter: frozenset[InvocationStatus],
    ) -> list[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        inv_strs = [str(inv_id) for inv_id in invocation_ids]
        status_strs = [s.name for s in status_filter]
        filtered = self._rust.filter_by_status(inv_strs, status_strs)
        return [InvocationId(s) for s in filtered]

    # ------------------------------------------------------------------
    # Purge
    # ------------------------------------------------------------------

    def purge(self) -> None:
        self._rust.purge()

    # ------------------------------------------------------------------
    # Blocking control
    # ------------------------------------------------------------------

    @property
    def blocking_control(self) -> BaseBlockingControl:
        return self._blocking

    # ------------------------------------------------------------------
    # Runner heartbeats — delegated to Rust
    # ------------------------------------------------------------------

    def register_runner_heartbeats(
        self,
        runner_ids: list[str],
        can_run_atomic_service: bool = False,
    ) -> None:
        for runner_id in runner_ids:
            self._rust.register_heartbeat(runner_id, can_run_atomic_service)

    def record_atomic_service_execution(self, runner_id: str, start_time: Any, end_time: Any) -> None:
        start_ts = start_time.timestamp() if hasattr(start_time, "timestamp") else float(start_time)
        end_ts = end_time.timestamp() if hasattr(end_time, "timestamp") else float(end_time)
        self._rust.record_atomic_service_execution(runner_id, start_ts, end_ts)

    def get_atomic_service_timeline(self) -> list[dict]:
        """Return the atomic service execution timeline from Rust.

        Each entry is a dict with keys: runner_id, start_time, end_time.
        """
        return self._rust.get_atomic_service_timeline()

    def _get_active_runners(
        self,
        timeout_seconds: float,
        can_run_atomic_service: bool | None = None,
    ) -> list[ActiveRunnerInfo]:
        from pynenc.orchestrator.atomic_service import ActiveRunnerInfo

        rust_runners = self._rust.get_active_runners(86400, can_run_atomic_service)
        now = datetime.now(tz=UTC)
        result = []
        for r in rust_runners:
            last_hb = datetime.fromisoformat(r["last_heartbeat"])
            if (now - last_hb).total_seconds() > timeout_seconds:
                continue
            creation = datetime.fromisoformat(r["creation_time"])
            last_start = None
            last_end = None
            if r.get("last_service_start"):
                last_start = datetime.fromisoformat(r["last_service_start"])
            if r.get("last_service_end"):
                last_end = datetime.fromisoformat(r["last_service_end"])
            result.append(
                ActiveRunnerInfo(
                    runner_id=r["runner_id"],
                    creation_time=creation,
                    last_heartbeat=last_hb,
                    allow_to_run_atomic_service=r["can_run_atomic_service"],
                    last_service_start=last_start,
                    last_service_end=last_end,
                )
            )
        result.sort(key=lambda info: info.creation_time)
        return result

    def get_pending_invocations_for_recovery(self) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        max_pending = self.app.conf.max_pending_seconds
        pending_inv_ids = self._rust.get_invocations_by_status("PENDING")
        cutoff = time() - max_pending
        for inv_id in pending_inv_ids:
            _, _, ts = self._rust.get_invocation_status(inv_id)
            if ts <= cutoff:
                yield InvocationId(inv_id)

    def _get_running_invocations_for_recovery(self, timeout_seconds: float) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        rust_runners = self._rust.get_active_runners(86400)
        now = datetime.now(tz=UTC)
        active_runner_ids: set[str] = set()
        for r in rust_runners:
            last_hb = datetime.fromisoformat(r["last_heartbeat"])
            if (now - last_hb).total_seconds() <= timeout_seconds:
                active_runner_ids.add(r["runner_id"])

        running_inv_ids = self._rust.get_invocations_by_status("RUNNING")
        for inv_id in running_inv_ids:
            _, runner_id, _ = self._rust.get_invocation_status(inv_id)
            if runner_id and runner_id not in active_runner_ids:
                yield InvocationId(inv_id)

    # NOTE: get_invocations_to_run is NOT overridden in
    # _RustvelloNativeOrchestrator. The Rust composite's CC logic requires
    # the task_registry, which is empty in from_backends()-created
    # RustvelloApp instances (tasks are only registered in pynenc's Python
    # app._tasks). We fall back to pynenc's Python CC logic for now.


# ---------------------------------------------------------------------------
# Concrete and native subclasses — defined in orchestrator_backends.py,
# re-exported here for backward compatibility.
# ---------------------------------------------------------------------------

from pynenc_rustvello.orchestrator_backends import (  # noqa: E402, F401
    RustMemNativeOrchestrator,
    RustMemOrchestrator,
    RustMongo3NativeOrchestrator,
    RustMongo3Orchestrator,
    RustMongoNativeOrchestrator,
    RustMongoOrchestrator,
    RustPostgresNativeOrchestrator,
    RustPostgresOrchestrator,
    RustRedisNativeOrchestrator,
    RustRedisOrchestrator,
    RustSqliteNativeOrchestrator,
    RustSqliteOrchestrator,
    _RustvelloNativeOrchestrator,
)

__all__ = [
    "_RustvelloOrchestrator",
    "_RustvelloNativeOrchestrator",
    "RustMemOrchestrator",
    "RustSqliteOrchestrator",
    "RustPostgresOrchestrator",
    "RustRedisOrchestrator",
    "RustMongoOrchestrator",
    "RustMongo3Orchestrator",
    "RustMemNativeOrchestrator",
    "RustSqliteNativeOrchestrator",
    "RustPostgresNativeOrchestrator",
    "RustRedisNativeOrchestrator",
    "RustMongoNativeOrchestrator",
    "RustMongo3NativeOrchestrator",
]
