"""Pynenc-compatible state backends backed by Rust backends."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from pynenc.app_info import AppInfo
from pynenc.state_backend.base_state_backend import BaseStateBackend, InvocationHistory
from pynenc.types import Params, Result

if TYPE_CHECKING:
    from pynenc.app import Pynenc
    from pynenc.identifiers.invocation_id import InvocationId
    from pynenc.identifiers.task_id import TaskId
    from pynenc.models.call_dto import CallDTO
    from pynenc.models.invocation_dto import InvocationDTO
    from pynenc.runner.runner_context import RunnerContext
    from pynenc.workflow import WorkflowIdentity


_PASCAL_TO_SNAKE_RE = re.compile(r"(?<=[a-z0-9])([A-Z])|([A-Z]+)(?=[A-Z][a-z])")


_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def _is_rust_not_found(exc: Exception, kind: str) -> bool:
    """Best-effort detection for Rust PyO3 not-found errors.

    Rust backends may raise typed exceptions (e.g. ``InvocationNotFoundError``)
    or generic ``ValueError`` depending on backend and mapping layer.
    """
    cls_name = type(exc).__name__
    if cls_name in {"InvocationNotFoundError", "CallNotFoundError", "ValueError"}:
        return True
    return f"{kind} not found" in str(exc).lower()


def _datetime_to_us(ts: datetime | None) -> int | None:
    """Convert a datetime to integer microseconds since epoch (no float precision loss)."""
    if ts is None:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return (ts - _EPOCH) // timedelta(microseconds=1)


def _pascal_to_upper_snake(name: str) -> str:
    """Convert PascalCase to UPPER_SNAKE_CASE for serde ↔ Python enum mapping."""
    return _PASCAL_TO_SNAKE_RE.sub(r"_\1\2", name).upper()


def _workflow_to_rust_json(wf: WorkflowIdentity) -> str:
    """Serialize a pynenc WorkflowIdentity to Rust-compatible JSON."""
    return json.dumps(
        {
            "workflow_id": str(wf.workflow_id),
            "workflow_type": {
                "language": "",
                "module": str(wf.workflow_type.module),
                "name": str(wf.workflow_type.func_name),
            },
            "parent_id": str(wf.parent_workflow_id)
            if getattr(wf, "parent_workflow_id", None)
            else None,
            "depth": 0,
        }
    )


def _workflow_from_rust(wf_data: dict) -> WorkflowIdentity:
    """Reconstruct a pynenc WorkflowIdentity from Rust JSON data."""
    from pynenc.identifiers.task_id import TaskId
    from pynenc.workflow.workflow_identity import WorkflowIdentity

    wf_type = wf_data["workflow_type"]
    return WorkflowIdentity(
        workflow_id=wf_data["workflow_id"],
        workflow_type=TaskId(module=wf_type["module"], func_name=wf_type["name"]),
        parent_workflow_id=wf_data.get("parent_id"),
    )


class _RustvelloStateBackend(BaseStateBackend[Params, Result]):
    """Base state backend backed by any Rust state backend object.

    Delegates all storage to the Rust layer. The adapter holds zero local
    state — it is a pure type-conversion bridge.
    Subclasses only override ``__init__`` to create the appropriate Rust inner.
    """

    def __init__(self, app: Pynenc, rust_sb: Any) -> None:
        super().__init__(app)
        self._rust = rust_sb

    def purge(self) -> None:
        self._rust.purge()

    # --- Invocation storage ---

    def _upsert_invocations(self, entries: list[tuple[InvocationDTO, CallDTO]]) -> None:
        for inv_dto, call_dto in entries:
            inv_id = str(inv_dto.invocation_id)
            task_id = inv_dto.call_id.task_id
            args = (
                dict(call_dto.serialized_arguments)
                if hasattr(call_dto, "serialized_arguments")
                else {}
            )
            parent_id = (
                str(inv_dto.parent_invocation_id)
                if inv_dto.parent_invocation_id
                else None
            )
            workflow_json = (
                _workflow_to_rust_json(inv_dto.workflow) if inv_dto.workflow else None
            )
            self._rust.upsert_invocation(
                inv_id,
                str(task_id.module),
                str(task_id.func_name),
                args,
                parent_id,
                workflow_json,
            )

    def _get_invocation(
        self, invocation_id: InvocationId
    ) -> tuple[InvocationDTO, CallDTO] | None:
        try:
            inv_json_str = self._rust.get_invocation(str(invocation_id))
        except Exception as e:
            if _is_rust_not_found(e, "invocation"):
                return None
            from pynenc.exceptions import StateBackendError

            raise StateBackendError(f"Rust FFI error retrieving invocation: {e}") from e
        return self._reconstruct_dtos(inv_json_str)

    def _reconstruct_dtos(self, inv_json_str: str) -> tuple[InvocationDTO, CallDTO]:
        """Reconstruct pynenc DTOs from Rust's JSON representation."""
        from pynenc.identifiers.call_id import CallId
        from pynenc.identifiers.task_id import TaskId
        from pynenc.models.call_dto import CallDTO
        from pynenc.models.invocation_dto import InvocationDTO
        from pynenc.workflow.workflow_identity import WorkflowIdentity

        inv_data = json.loads(inv_json_str)

        # Reconstruct TaskId and CallId
        call_id_data = inv_data["call_id"]
        task_id_data = call_id_data["task_id"]
        task_id = TaskId(module=task_id_data["module"], func_name=task_id_data["name"])
        args_id = call_id_data["args_id"]
        call_id = CallId(task_id=task_id, args_id=args_id)

        # Reconstruct WorkflowIdentity
        wf_data = inv_data.get("workflow")
        if wf_data:
            workflow = _workflow_from_rust(wf_data)
        else:
            workflow = WorkflowIdentity(
                workflow_id=inv_data["invocation_id"],
                workflow_type=task_id,
            )

        # Get serialized arguments from Rust call
        call_id_str = f"{task_id_data['module']}.{task_id_data['name']}:{args_id}"
        try:
            call_json_str = self._rust.get_call(call_id_str)
            call_data = json.loads(call_json_str)
            args = dict(call_data.get("serialized_arguments", {}))
        except Exception as e:
            if _is_rust_not_found(e, "call"):
                args = {}
            else:
                from pynenc.exceptions import StateBackendError

                raise StateBackendError(f"Rust FFI error retrieving call: {e}") from e

        inv_dto = InvocationDTO(
            invocation_id=inv_data["invocation_id"],
            call_id=call_id,
            workflow=workflow,
            parent_invocation_id=inv_data.get("parent_invocation_id"),
        )
        call_dto = CallDTO(call_id=call_id, serialized_arguments=args)
        return (inv_dto, call_dto)

    def get_child_invocations(
        self, parent_invocation_id: InvocationId
    ) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        for child_id in self._rust.get_child_invocations(str(parent_invocation_id)):
            yield InvocationId(child_id)

    # --- History ---

    def _add_histories(
        self,
        invocation_ids: list[InvocationId],
        invocation_history: InvocationHistory,
    ) -> None:
        sr_timestamp_us = _datetime_to_us(invocation_history.status_record.timestamp)
        history_timestamp_us = _datetime_to_us(
            getattr(invocation_history, "_timestamp", None)
        )

        sr_runner_id = invocation_history.status_record.runner_id or None
        ctx_runner_id = invocation_history.runner_context_id or None
        for inv_id in invocation_ids:
            self._rust.add_history(
                str(inv_id),
                invocation_history.status_record.status.name,
                sr_runner_id,
                ctx_runner_id,
                None,
                sr_timestamp_us,
                history_timestamp_us,
            )

    def _get_history(self, invocation_id: InvocationId) -> list[InvocationHistory]:
        from pynenc.invocation.status import InvocationStatus, InvocationStatusRecord

        history_json_str = self._rust.get_history(str(invocation_id))
        history_list = json.loads(history_json_str)
        result = []
        for h in history_list:
            sr_data = h["status_record"]
            status = InvocationStatus[_pascal_to_upper_snake(sr_data["status"])]
            sr_runner_id = sr_data.get("runner_id")
            if isinstance(sr_runner_id, dict):
                sr_runner_id = next(iter(sr_runner_id.values()), None)
            ctx_runner_id = h.get("runner_id")
            if isinstance(ctx_runner_id, dict):
                ctx_runner_id = next(iter(ctx_runner_id.values()), None)
            ts_str = sr_data.get("timestamp")
            if ts_str:
                sr_ts = datetime.fromisoformat(ts_str)
                if sr_ts.tzinfo is None:
                    sr_ts = sr_ts.replace(tzinfo=UTC)
            else:
                sr_ts = datetime.now(UTC)
            # history_timestamp for time-range filtering
            hist_ts_str = h.get("history_timestamp")
            if hist_ts_str:
                hist_ts = datetime.fromisoformat(hist_ts_str)
                if hist_ts.tzinfo is None:
                    hist_ts = hist_ts.replace(tzinfo=UTC)
            else:
                hist_ts = sr_ts
            sr = InvocationStatusRecord(
                status=status,
                runner_id=sr_runner_id,
                timestamp=sr_ts,
            )
            ih = InvocationHistory(
                invocation_id=str(h["invocation_id"]),
                status_record=sr,
                runner_context_id=ctx_runner_id or "",
                registered_by_inv_id=h.get("registered_by_inv_id"),
            )
            ih._timestamp = hist_ts
            result.append(ih)
        result.sort(key=lambda r: r.timestamp)
        return result

    # --- Results ---

    def _set_result(self, invocation_id: InvocationId, serialized_result: str) -> None:
        self._rust.store_result(str(invocation_id), serialized_result)

    def _get_result(self, invocation_id: InvocationId) -> str:
        result = self._rust.get_result(str(invocation_id))
        if result is None:
            raise KeyError(f"No result for invocation {invocation_id}")
        return result

    # --- Exceptions ---

    def _set_exception(
        self, invocation_id: InvocationId, serialized_exception: str
    ) -> None:
        self._rust.store_error(
            str(invocation_id), "SerializedException", serialized_exception, None
        )

    def _get_exception(self, invocation_id: InvocationId) -> str:
        error_json = self._rust.get_error_json(str(invocation_id))
        if error_json is None:
            raise KeyError(f"No exception for invocation {invocation_id}")
        error = json.loads(error_json)
        message = error.get("message", "")
        # _set_exception stores a pynenc serialized-exception envelope in the
        # message field.  If it parses as one, return it directly.
        try:
            envelope = json.loads(message)
            if isinstance(envelope, dict) and "error_name" in envelope:
                return message
        except (json.JSONDecodeError, TypeError):
            pass
        # Rust runner stored a TaskError directly — reconstruct the pynenc
        # exception envelope so that deserialize_exception() works correctly.
        import builtins

        error_type = error.get("error_type", "Exception")
        cls = getattr(builtins, error_type, None)
        if cls is None or not (
            isinstance(cls, type) and issubclass(cls, BaseException)
        ):
            cls = Exception
        return self.serialize_exception(cls(message))

    # --- Workflow data ---

    def set_workflow_data(
        self, workflow_identity: WorkflowIdentity, key: str, value: Any
    ) -> None:
        serialized = self.app.client_data_store.serialize(value)
        self._rust.set_workflow_data(
            str(workflow_identity.workflow_id), key, serialized
        )

    def get_workflow_data(
        self, workflow_identity: WorkflowIdentity, key: str, default: Any = None
    ) -> Any:
        result = self._rust.get_workflow_data(str(workflow_identity.workflow_id), key)
        if result is None:
            return default
        from pynenc.exceptions import SerializationError

        try:
            return self.app.client_data_store.deserialize(result)
        except SerializationError:
            return result

    # --- App info ---

    def store_app_info(self, app_info: AppInfo) -> None:
        self._rust.store_app_info(app_info.app_id, app_info.to_json())

    def get_app_info(self) -> AppInfo:
        result = self._rust.get_app_info(self.app.app_id)
        if result is None:
            raise KeyError("No app info stored")
        return AppInfo.from_json(result)

    def discover_app_infos(self) -> dict[str, AppInfo]:
        return {
            app_id: AppInfo.from_json(info_json)
            for app_id, info_json in self._rust.get_all_app_infos()
        }

    # --- Workflow runs ---

    def store_workflow_run(self, workflow_identity: WorkflowIdentity) -> None:
        self._rust.store_workflow_run(_workflow_to_rust_json(workflow_identity))

    def get_all_workflow_types(self) -> Iterator[TaskId]:
        from pynenc.identifiers.task_id import TaskId

        for key in self._rust.get_all_workflow_types():
            yield TaskId.from_key(key)

    def get_all_workflow_runs(self) -> Iterator[WorkflowIdentity]:
        for wf_json in self._rust.get_all_workflow_runs():
            yield _workflow_from_rust(json.loads(wf_json))

    def get_workflow_runs(self, workflow_type: TaskId) -> Iterator[WorkflowIdentity]:
        for wf_json in self._rust.get_workflow_runs(
            str(workflow_type.module), str(workflow_type.func_name)
        ):
            yield _workflow_from_rust(json.loads(wf_json))

    def store_workflow_sub_invocation(
        self, parent_workflow_id: InvocationId, sub_invocation_id: InvocationId
    ) -> None:
        self._rust.store_workflow_sub_invocation(
            str(parent_workflow_id), str(sub_invocation_id)
        )

    def get_workflow_sub_invocations(
        self, workflow_id: InvocationId
    ) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        for sub_id in self._rust.get_workflow_sub_invocations(str(workflow_id)):
            yield InvocationId(sub_id)

    # --- Time-range queries ---

    def iter_invocations_in_timerange(
        self,
        start_time: datetime,
        end_time: datetime,
        batch_size: int = 100,
    ) -> Iterator[list[InvocationId]]:
        from pynenc.identifiers.invocation_id import InvocationId

        history_json = self._rust.get_history_in_timerange(
            start_time.timestamp(), end_time.timestamp(), 10000, 0
        )
        history_list = json.loads(history_json)
        seen: set[str] = set()
        matching: list[InvocationId] = []
        for h in history_list:
            inv_id = str(h["invocation_id"])
            if inv_id not in seen:
                seen.add(inv_id)
                matching.append(InvocationId(inv_id))
        for i in range(0, len(matching), batch_size):
            yield matching[i : i + batch_size]

    def iter_history_in_timerange(
        self,
        start_time: datetime,
        end_time: datetime,
        batch_size: int = 100,
    ) -> Iterator[list[InvocationHistory]]:
        from pynenc.invocation.status import InvocationStatus, InvocationStatusRecord

        history_json = self._rust.get_history_in_timerange(
            start_time.timestamp(), end_time.timestamp(), 10000, 0
        )
        history_list = json.loads(history_json)
        matching: list[InvocationHistory] = []
        for h in history_list:
            sr_data = h["status_record"]
            status = InvocationStatus[_pascal_to_upper_snake(sr_data["status"])]
            sr_runner_id = sr_data.get("runner_id")
            if isinstance(sr_runner_id, dict):
                sr_runner_id = next(iter(sr_runner_id.values()), None)
            ctx_runner_id = h.get("runner_id")
            if isinstance(ctx_runner_id, dict):
                ctx_runner_id = next(iter(ctx_runner_id.values()), None)
            ts_str = sr_data.get("timestamp")
            if ts_str:
                sr_ts = datetime.fromisoformat(ts_str)
                if sr_ts.tzinfo is None:
                    sr_ts = sr_ts.replace(tzinfo=UTC)
            else:
                sr_ts = datetime.now(UTC)
            hist_ts_str = h.get("history_timestamp")
            if hist_ts_str:
                hist_ts = datetime.fromisoformat(hist_ts_str)
                if hist_ts.tzinfo is None:
                    hist_ts = hist_ts.replace(tzinfo=UTC)
            else:
                hist_ts = sr_ts
            sr = InvocationStatusRecord(
                status=status,
                runner_id=sr_runner_id,
                timestamp=sr_ts,
            )
            ih = InvocationHistory(
                invocation_id=str(h["invocation_id"]),
                status_record=sr,
                runner_context_id=ctx_runner_id or "",
            )
            ih._timestamp = hist_ts
            matching.append(ih)
        matching.sort(key=lambda x: x.timestamp)
        for i in range(0, len(matching), batch_size):
            yield matching[i : i + batch_size]

    # --- Runner contexts ---

    def _store_runner_context(self, runner_context: RunnerContext) -> None:
        parent_id = (
            runner_context.parent_ctx.runner_id if runner_context.parent_ctx else None
        )
        parent_cls = (
            runner_context.parent_ctx.runner_cls if runner_context.parent_ctx else None
        )
        self._rust.store_runner_context(
            runner_context.runner_id,
            runner_context.runner_cls,
            runner_context.pid,
            runner_context.hostname,
            runner_context.thread_id,
            parent_id,
            parent_cls,
        )

    def get_matching_runner_contexts(self, partial_id: str) -> Iterator[RunnerContext]:
        from pynenc.runner.runner_context import RunnerContext

        for ctx_json in self._rust.get_matching_runner_contexts(partial_id):
            ctx = json.loads(ctx_json)
            yield RunnerContext(
                runner_cls=ctx["runner_cls"],
                runner_id=ctx["runner_id"],
                pid=ctx["pid"],
                hostname=ctx["hostname"],
                thread_id=ctx["thread_id"],
            )

    def get_invocation_ids_by_workflow(
        self,
        workflow_id: str | None = None,
        workflow_type_key: str | None = None,
    ) -> Iterator[InvocationId]:
        from pynenc.identifiers.invocation_id import InvocationId

        if workflow_id:
            for inv_id in self._rust.get_workflow_invocations(workflow_id):
                yield InvocationId(inv_id)
        elif workflow_type_key:
            from pynenc.identifiers.task_id import TaskId

            tid = TaskId.from_key(workflow_type_key)
            for wf_json in self._rust.get_workflow_runs(
                str(tid.module), str(tid.func_name)
            ):
                wf = json.loads(wf_json)
                for inv_id in self._rust.get_workflow_invocations(wf["workflow_id"]):
                    yield InvocationId(inv_id)

    def _get_runner_context(self, runner_id: str) -> RunnerContext | None:
        from pynenc.runner.runner_context import RunnerContext

        ctx_json = self._rust.get_runner_context(runner_id)
        if ctx_json is None:
            return None
        ctx = json.loads(ctx_json)
        return RunnerContext(
            runner_cls=ctx["runner_cls"],
            runner_id=ctx["runner_id"],
            pid=ctx["pid"],
            hostname=ctx["hostname"],
            thread_id=ctx["thread_id"],
        )

    def _get_runner_contexts(self, runner_ids: list[str]) -> list[RunnerContext]:
        return [
            ctx
            for rid in runner_ids
            if (ctx := self._get_runner_context(rid)) is not None
        ]


# ---------------------------------------------------------------------------
# Concrete subclasses per backend
# ---------------------------------------------------------------------------


class RustMemStateBackend(_RustvelloStateBackend):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustMemStateBackend as _Inner

        super().__init__(app, _Inner())


class RustSqliteStateBackend(_RustvelloStateBackend):
    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustSqliteStateBackend as _Inner

        if db is None:
            from pynenc_rustvello.broker import _get_or_create_sqlite_db

            db = _get_or_create_sqlite_db(app)
        super().__init__(app, _Inner(db))


class RustPostgresStateBackend(_RustvelloStateBackend):
    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustPostgresStateBackend as _Inner

        if db is None:
            from pynenc_rustvello.broker import _get_or_create_postgres_db

            db = _get_or_create_postgres_db(app)
        super().__init__(app, _Inner(db))


class RustRedisStateBackend(_RustvelloStateBackend):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustRedisStateBackend as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_redis_pool

            pool = _get_or_create_redis_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongoStateBackend(_RustvelloStateBackend):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongoStateBackend as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_mongo_pool

            pool = _get_or_create_mongo_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongo3StateBackend(_RustvelloStateBackend):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongo3StateBackend as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_mongo3_pool

            pool = _get_or_create_mongo3_pool(app)
        super().__init__(app, _Inner(pool))
