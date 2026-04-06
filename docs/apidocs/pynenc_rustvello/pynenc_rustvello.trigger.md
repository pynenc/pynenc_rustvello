# {py:mod}`pynenc_rustvello.trigger`

```{py:module} pynenc_rustvello.trigger

```

```{autodoc2-docstring} pynenc_rustvello.trigger
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_RustTriggerBase <pynenc_rustvello.trigger._RustTriggerBase>`
  - ```{autodoc2-docstring} pynenc_rustvello.trigger._RustTriggerBase
    :summary:
    ```
* - {py:obj}`RustMemTrigger <pynenc_rustvello.trigger.RustMemTrigger>`
  -
* - {py:obj}`RustSqliteTrigger <pynenc_rustvello.trigger.RustSqliteTrigger>`
  -
* - {py:obj}`RustPostgresTrigger <pynenc_rustvello.trigger.RustPostgresTrigger>`
  -
* - {py:obj}`RustRedisTrigger <pynenc_rustvello.trigger.RustRedisTrigger>`
  -
* - {py:obj}`RustMongoTrigger <pynenc_rustvello.trigger.RustMongoTrigger>`
  -
* - {py:obj}`RustMongo3Trigger <pynenc_rustvello.trigger.RustMongo3Trigger>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_reconstruct_condition <pynenc_rustvello.trigger._reconstruct_condition>`
  - ```{autodoc2-docstring} pynenc_rustvello.trigger._reconstruct_condition
    :summary:
    ```
* - {py:obj}`_context_to_rust_json <pynenc_rustvello.trigger._context_to_rust_json>`
  - ```{autodoc2-docstring} pynenc_rustvello.trigger._context_to_rust_json
    :summary:
    ```
* - {py:obj}`_reconstruct_trigger_dto <pynenc_rustvello.trigger._reconstruct_trigger_dto>`
  - ```{autodoc2-docstring} pynenc_rustvello.trigger._reconstruct_trigger_dto
    :summary:
    ```
````

### API

````{py:function} _reconstruct_condition(condition_json: str) -> pynenc.trigger.conditions.TriggerCondition
:canonical: pynenc_rustvello.trigger._reconstruct_condition

```{autodoc2-docstring} pynenc_rustvello.trigger._reconstruct_condition
```
````

````{py:function} _context_to_rust_json(ctx: pynenc.trigger.conditions.ConditionContext) -> dict
:canonical: pynenc_rustvello.trigger._context_to_rust_json

```{autodoc2-docstring} pynenc_rustvello.trigger._context_to_rust_json
```
````

````{py:function} _reconstruct_trigger_dto(trigger_json_str: str) -> pynenc.models.trigger_definition_dto.TriggerDefinitionDTO
:canonical: pynenc_rustvello.trigger._reconstruct_trigger_dto

```{autodoc2-docstring} pynenc_rustvello.trigger._reconstruct_trigger_dto
```
````

`````{py:class} _RustTriggerBase(app: pynenc.app.Pynenc, rust_trigger: typing.Any)
:canonical: pynenc_rustvello.trigger._RustTriggerBase

Bases: {py:obj}`pynenc.trigger.base_trigger.BaseTrigger`

```{autodoc2-docstring} pynenc_rustvello.trigger._RustTriggerBase
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.trigger._RustTriggerBase.__init__
```

````{py:method} _register_condition(condition: pynenc.trigger.conditions.TriggerCondition) -> None
:canonical: pynenc_rustvello.trigger._RustTriggerBase._register_condition

````

````{py:method} _register_source_task_condition(task_id: pynenc.identifiers.task_id.TaskId, condition_id: pynenc.trigger.types.ConditionId) -> None
:canonical: pynenc_rustvello.trigger._RustTriggerBase._register_source_task_condition

````

````{py:method} get_condition(condition_id: str) -> pynenc.trigger.conditions.TriggerCondition | None
:canonical: pynenc_rustvello.trigger._RustTriggerBase.get_condition

````

````{py:method} register_trigger(trigger: pynenc.models.trigger_definition_dto.TriggerDefinitionDTO) -> None
:canonical: pynenc_rustvello.trigger._RustTriggerBase.register_trigger

````

````{py:method} _get_trigger(trigger_id: str) -> pynenc.models.trigger_definition_dto.TriggerDefinitionDTO | None
:canonical: pynenc_rustvello.trigger._RustTriggerBase._get_trigger

````

````{py:method} get_triggers_for_condition(condition_id: str) -> list[pynenc.models.trigger_definition_dto.TriggerDefinitionDTO]
:canonical: pynenc_rustvello.trigger._RustTriggerBase.get_triggers_for_condition

````

````{py:method} get_conditions_sourced_from_task(task_id: pynenc.identifiers.task_id.TaskId, context_type: type[pynenc.trigger.conditions.ConditionContext] | None = None) -> list[pynenc.trigger.conditions.TriggerCondition]
:canonical: pynenc_rustvello.trigger._RustTriggerBase.get_conditions_sourced_from_task

````

````{py:method} record_valid_condition(valid_condition: pynenc.trigger.conditions.ValidCondition) -> None
:canonical: pynenc_rustvello.trigger._RustTriggerBase.record_valid_condition

````

````{py:method} record_valid_conditions(valid_conditions: list[pynenc.trigger.conditions.ValidCondition]) -> None
:canonical: pynenc_rustvello.trigger._RustTriggerBase.record_valid_conditions

````

````{py:method} get_valid_conditions() -> dict[str, pynenc.trigger.conditions.ValidCondition]
:canonical: pynenc_rustvello.trigger._RustTriggerBase.get_valid_conditions

````

````{py:method} clear_valid_conditions(conditions: typing.Any) -> None
:canonical: pynenc_rustvello.trigger._RustTriggerBase.clear_valid_conditions

````

````{py:method} _get_all_conditions() -> list[pynenc.trigger.conditions.TriggerCondition]
:canonical: pynenc_rustvello.trigger._RustTriggerBase._get_all_conditions

````

````{py:method} get_last_cron_execution(condition_id: pynenc.trigger.types.ConditionId) -> datetime.datetime | None
:canonical: pynenc_rustvello.trigger._RustTriggerBase.get_last_cron_execution

````

````{py:method} store_last_cron_execution(condition_id: pynenc.trigger.types.ConditionId, execution_time: datetime.datetime, expected_last_execution: datetime.datetime | None = None) -> bool
:canonical: pynenc_rustvello.trigger._RustTriggerBase.store_last_cron_execution

````

````{py:method} claim_trigger_run(trigger_run_id: str, expiration_seconds: int = 60) -> bool
:canonical: pynenc_rustvello.trigger._RustTriggerBase.claim_trigger_run

````

````{py:method} clean_task_trigger_definitions(task_id: pynenc.identifiers.task_id.TaskId) -> None
:canonical: pynenc_rustvello.trigger._RustTriggerBase.clean_task_trigger_definitions

````

````{py:method} _purge() -> None
:canonical: pynenc_rustvello.trigger._RustTriggerBase._purge

````

`````

```{py:class} RustMemTrigger(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.trigger.RustMemTrigger

Bases: {py:obj}`pynenc_rustvello.trigger._RustTriggerBase`

```

```{py:class} RustSqliteTrigger(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.trigger.RustSqliteTrigger

Bases: {py:obj}`pynenc_rustvello.trigger._RustTriggerBase`

```

```{py:class} RustPostgresTrigger(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.trigger.RustPostgresTrigger

Bases: {py:obj}`pynenc_rustvello.trigger._RustTriggerBase`

```

```{py:class} RustRedisTrigger(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.trigger.RustRedisTrigger

Bases: {py:obj}`pynenc_rustvello.trigger._RustTriggerBase`

```

```{py:class} RustMongoTrigger(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.trigger.RustMongoTrigger

Bases: {py:obj}`pynenc_rustvello.trigger._RustTriggerBase`

```

```{py:class} RustMongo3Trigger(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.trigger.RustMongo3Trigger

Bases: {py:obj}`pynenc_rustvello.trigger._RustTriggerBase`

```
