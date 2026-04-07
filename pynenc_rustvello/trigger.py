"""Pynenc-compatible triggers backed by Rust backends."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pynenc.invocation.status import InvocationStatus
from pynenc.trigger.arguments.argument_filters import StaticArgumentFilter
from pynenc.trigger.arguments.result_filter import NoResultFilter
from pynenc.trigger.base_trigger import BaseTrigger
from pynenc.trigger.conditions import (
    CronCondition,
    CronContext,
    EventCondition,
    EventContext,
    ExceptionCondition,
    ExceptionContext,
    ResultCondition,
    ResultContext,
    StatusCondition,
    StatusContext,
    ValidCondition,
)
from rustvello import status_from_serde, status_to_serde

if TYPE_CHECKING:
    from pynenc.app import Pynenc
    from pynenc.identifiers.task_id import TaskId
    from pynenc.models.trigger_definition_dto import TriggerDefinitionDTO
    from pynenc.trigger.conditions import ConditionContext, TriggerCondition
    from pynenc.trigger.types import ConditionId


def _reconstruct_condition(condition_json: str) -> TriggerCondition:
    """Reconstruct a pynenc TriggerCondition from Rust's JSON representation.

    Creates the appropriate Python condition subclass, using the argument filter
    data stored in Rust when available.
    """
    from pynenc.identifiers.task_id import TaskId

    data = json.loads(condition_json)

    if "Status" in data:
        s = data["Status"]
        task_id = TaskId(module=s["task_id"]["module"], func_name=s["task_id"]["name"])
        statuses = [InvocationStatus[status_from_serde(st)] for st in s["statuses"]]
        arg_filter = StaticArgumentFilter(s.get("argument_filter") or {})
        return StatusCondition(task_id, statuses, arg_filter)

    if "Result" in data:
        r = data["Result"]
        task_id = TaskId(module=r["task_id"]["module"], func_name=r["task_id"]["name"])
        arg_filter = StaticArgumentFilter(r.get("argument_filter") or {})
        return ResultCondition(task_id, arg_filter, NoResultFilter())

    if "Exception" in data:
        e = data["Exception"]
        task_id = TaskId(module=e["task_id"]["module"], func_name=e["task_id"]["name"])
        arg_filter = StaticArgumentFilter(e.get("argument_filter") or {})
        return ExceptionCondition(task_id, arg_filter, e.get("exception_types", []))

    if "Cron" in data:
        c = data["Cron"]
        return CronCondition(
            cron_expression=c["cron_expression"],
            min_interval_seconds=c.get("min_interval_seconds", 0),
        )

    if "Event" in data:
        ev = data["Event"]
        payload_filter = StaticArgumentFilter(ev.get("payload_filter") or {})
        return EventCondition(ev["event_code"], payload_filter)

    raise ValueError(f"Unknown Rust condition format: {condition_json}")


# status_to_serde() and status_from_serde() are imported from rustvello
# (Rust is the single source of truth for its own serialization format)


def _context_to_rust_json(ctx: ConditionContext) -> dict:
    """Convert a pynenc ConditionContext to Rust ConditionContext JSON."""

    if isinstance(ctx, ResultContext):
        return {
            "Result": {
                "invocation_id": str(ctx.invocation_id),
                "task_id": {
                    "language": "",
                    "module": str(ctx.call_id.task_id.module),
                    "name": str(ctx.call_id.task_id.func_name),
                },
                "result": ctx.result
                if isinstance(ctx.result, (str, int, float, bool, type(None)))
                else str(ctx.result),
                "arguments": {},
            }
        }
    if isinstance(ctx, ExceptionContext):
        return {
            "Exception": {
                "invocation_id": str(ctx.invocation_id),
                "task_id": {
                    "language": "",
                    "module": str(ctx.call_id.task_id.module),
                    "name": str(ctx.call_id.task_id.func_name),
                },
                "error_type": ctx.exception_type,
                "error_message": ctx.exception_message,
                "arguments": {},
            }
        }
    if isinstance(ctx, StatusContext):
        return {
            "Status": {
                "invocation_id": str(ctx.invocation_id),
                "task_id": {
                    "language": "",
                    "module": str(ctx.call_id.task_id.module),
                    "name": str(ctx.call_id.task_id.func_name),
                },
                "status": status_to_serde(ctx.status.name),
                "arguments": {},
            }
        }
    if isinstance(ctx, CronContext):
        ts = ctx.timestamp.isoformat()
        if ctx.timestamp.tzinfo is None:
            ts += "+00:00"
        result: dict[str, Any] = {
            "Cron": {
                "timestamp": ts,
                "last_execution": None,
            }
        }
        return result
    if isinstance(ctx, EventContext):
        return {
            "Event": {
                "event_code": ctx.event_code,
                "event_id": ctx.event_id,
                "payload": ctx.payload if ctx.payload else {},
            }
        }
    raise TypeError(f"Unknown context type: {type(ctx)}")


def _reconstruct_trigger_dto(trigger_json_str: str) -> TriggerDefinitionDTO:
    """Reconstruct a pynenc TriggerDefinitionDTO from Rust JSON."""
    from pynenc.identifiers.task_id import TaskId
    from pynenc.models.trigger_definition_dto import TriggerDefinitionDTO
    from pynenc.trigger.conditions import CompositeLogic

    data = json.loads(trigger_json_str)
    task_data = data["task_id"]
    task_id = TaskId(module=task_data["module"], func_name=task_data["name"])
    logic = CompositeLogic.AND if data["logic"] in ("And", "AND") else CompositeLogic.OR
    arg_json = (
        json.dumps(data["argument_template"]) if data.get("argument_template") else None
    )
    return TriggerDefinitionDTO(
        trigger_id=data["trigger_id"],
        task_id=task_id,
        condition_ids=data["condition_ids"],
        logic=logic,
        argument_provider_json=arg_json,
    )


class _RustTriggerBase(BaseTrigger):
    """Base trigger backed by any Rust trigger store object.

    Delegates condition registration, trigger storage, valid condition
    tracking, and event processing to Rust.  Rust is the single source
    of truth for all stored data; the only local state is ``_vc_cache``,
    a write-through cache for ``ValidCondition`` objects that carry
    Python-specific data (CallId, Arguments, filter objects) which Rust's
    JSON representation does not preserve.

    Subclasses only override ``__init__`` to create the appropriate Rust inner.
    """

    def __init__(self, app: Pynenc, rust_trigger: Any) -> None:
        super().__init__(app)
        self._rust = rust_trigger
        # Write-through cache: Python ValidCondition objects contain rich data
        # (CallId, Arguments, filter objects) that Rust JSON doesn't preserve.
        # Writes go to both Rust and the cache; reads come from the cache.
        self._vc_cache: dict[str, ValidCondition] = {}

    # ── Registration ───────────────────────────────────────────────

    def _register_condition(self, condition: TriggerCondition) -> None:
        from pynenc.trigger.conditions import (
            CronCondition,
            EventCondition,
            ExceptionCondition,
            ResultCondition,
            StatusCondition,
        )

        def _filter_json(arg_filter: Any) -> str | None:
            """Serialize a pynenc argument filter to JSON for Rust, or None if empty."""
            if hasattr(arg_filter, "filter_args") and arg_filter.filter_args:
                return json.dumps(arg_filter.filter_args)
            return None

        if isinstance(condition, ResultCondition):
            self._rust.register_result_condition(
                str(condition.task_id.module),
                str(condition.task_id.func_name),
                _filter_json(condition.arguments_filter),
            )
        elif isinstance(condition, ExceptionCondition):
            self._rust.register_exception_condition(
                str(condition.task_id.module),
                str(condition.task_id.func_name),
                condition.exception_types or None,
                _filter_json(condition.arguments_filter),
            )
        elif isinstance(condition, StatusCondition):
            self._rust.register_status_condition(
                str(condition.task_id.module),
                str(condition.task_id.func_name),
                [s.name for s in condition.statuses],
                _filter_json(condition.arguments_filter),
            )
        elif isinstance(condition, CronCondition):
            self._rust.register_cron_condition(
                condition.cron_expression,
                condition.min_interval_seconds,
            )
        elif isinstance(condition, EventCondition):
            filter_json = None
            if (
                hasattr(condition, "payload_filter")
                and hasattr(condition.payload_filter, "filter_args")
                and condition.payload_filter.filter_args
            ):
                filter_json = json.dumps(condition.payload_filter.filter_args)
            self._rust.register_event_condition(condition.event_code, filter_json)

    def _register_source_task_condition(
        self, task_id: TaskId, condition_id: ConditionId
    ) -> None:
        # Rust's register_condition() automatically indexes by source task IDs,
        # so no additional registration is needed here.
        pass

    def get_condition(self, condition_id: str) -> TriggerCondition | None:
        cond_json = self._rust.get_condition(condition_id)
        if cond_json is None:
            return None
        return _reconstruct_condition(cond_json)

    # ── Trigger definitions ────────────────────────────────────────

    def register_trigger(self, trigger: TriggerDefinitionDTO) -> None:
        logic_str = "And" if trigger.logic.name == "AND" else "Or"
        trigger_json = json.dumps(
            {
                "trigger_id": trigger.trigger_id,
                "task_id": {
                    "language": "",
                    "module": str(trigger.task_id.module),
                    "name": str(trigger.task_id.func_name),
                },
                "condition_ids": trigger.condition_ids,
                "logic": logic_str,
                "argument_template": json.loads(trigger.argument_provider_json)
                if trigger.argument_provider_json
                else None,
            }
        )
        self._rust.register_trigger(trigger_json)

    def _get_trigger(self, trigger_id: str) -> TriggerDefinitionDTO | None:
        trigger_json = self._rust.get_trigger(trigger_id)
        if trigger_json is None:
            return None
        return _reconstruct_trigger_dto(trigger_json)

    def get_triggers_for_condition(
        self, condition_id: str
    ) -> list[TriggerDefinitionDTO]:
        trigger_jsons = self._rust.get_triggers_for_condition(condition_id)
        return [_reconstruct_trigger_dto(j) for j in trigger_jsons]

    def get_conditions_sourced_from_task(
        self, task_id: TaskId, context_type: type[ConditionContext] | None = None
    ) -> list[TriggerCondition]:
        pairs = self._rust.get_conditions_for_task(
            str(task_id.module), str(task_id.func_name)
        )
        conditions: list[TriggerCondition] = []
        for _cid, cond_json in pairs:
            cond = _reconstruct_condition(cond_json)
            if context_type is None or cond.context_type == context_type:
                conditions.append(cond)
        return conditions

    # ── Valid conditions ───────────────────────────────────────────

    def record_valid_condition(self, valid_condition: ValidCondition) -> None:
        vc_json = json.dumps(
            {
                "valid_condition_id": valid_condition.valid_condition_id,
                "condition_id": valid_condition.condition.condition_id,
                "context": _context_to_rust_json(valid_condition.context),
            }
        )
        self._rust.record_valid_condition(vc_json)
        self._vc_cache[valid_condition.valid_condition_id] = valid_condition

    def record_valid_conditions(self, valid_conditions: list[ValidCondition]) -> None:
        for vc in valid_conditions:
            self.record_valid_condition(vc)

    def get_valid_conditions(self) -> dict[str, ValidCondition]:
        return self._vc_cache.copy()

    def clear_valid_conditions(self, conditions: Any) -> None:
        ids = [vc.valid_condition_id for vc in conditions]
        if ids:
            self._rust.clear_valid_conditions(ids)
            for vc_id in ids:
                self._vc_cache.pop(vc_id, None)

    # ── Condition retrieval ────────────────────────────────────────

    def _get_all_conditions(self) -> list[TriggerCondition]:
        pairs = self._rust.get_all_conditions()
        return [_reconstruct_condition(cond_json) for _cid, cond_json in pairs]

    # ── Cron ───────────────────────────────────────────────────────

    def get_last_cron_execution(self, condition_id: ConditionId) -> datetime | None:
        ts = self._rust.get_last_cron_execution(str(condition_id))
        if ts is None:
            return None
        return datetime.fromtimestamp(ts, tz=UTC)

    def store_last_cron_execution(
        self,
        condition_id: ConditionId,
        execution_time: datetime,
        expected_last_execution: datetime | None = None,
    ) -> bool:
        exec_ts = execution_time.timestamp()
        expected_ts = (
            expected_last_execution.timestamp() if expected_last_execution else None
        )
        return self._rust.store_cron_execution(str(condition_id), exec_ts, expected_ts)

    # ── Trigger claim ──────────────────────────────────────────────

    def claim_trigger_run(
        self, trigger_run_id: str, expiration_seconds: int = 60
    ) -> bool:
        return self._rust.claim_trigger_run(trigger_run_id)

    # ── Cleanup ────────────────────────────────────────────────────

    def clean_task_trigger_definitions(self, task_id: TaskId) -> None:
        self._rust.remove_triggers_for_task(str(task_id.module), str(task_id.func_name))

    def _purge(self) -> None:
        self._rust.purge()
        self._vc_cache.clear()


# ---------------------------------------------------------------------------
# Concrete subclasses per backend
# ---------------------------------------------------------------------------


class RustMemTrigger(_RustTriggerBase):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustMemTriggerStore as _Inner

        super().__init__(app, _Inner())


class RustSqliteTrigger(_RustTriggerBase):
    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustSqliteTriggerStore as _Inner

        if db is None:
            from pynenc_rustvello.broker import _get_or_create_sqlite_db

            db = _get_or_create_sqlite_db(app)
        super().__init__(app, _Inner(db))


class RustPostgresTrigger(_RustTriggerBase):
    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustPostgresTriggerStore as _Inner

        if db is None:
            from pynenc_rustvello.broker import _get_or_create_postgres_db

            db = _get_or_create_postgres_db(app)
        super().__init__(app, _Inner(db))


class RustRedisTrigger(_RustTriggerBase):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustRedisTriggerStore as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_redis_pool

            pool = _get_or_create_redis_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongoTrigger(_RustTriggerBase):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongoTriggerStore as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_mongo_pool

            pool = _get_or_create_mongo_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongo3Trigger(_RustTriggerBase):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongo3TriggerStore as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_mongo3_pool

            pool = _get_or_create_mongo3_pool(app)
        super().__init__(app, _Inner(pool))
