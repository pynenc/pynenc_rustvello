# {py:mod}`pynenc_rustvello.state_backend`

```{py:module} pynenc_rustvello.state_backend
```

```{autodoc2-docstring} pynenc_rustvello.state_backend
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_RustvelloStateBackend <pynenc_rustvello.state_backend._RustvelloStateBackend>`
  - ```{autodoc2-docstring} pynenc_rustvello.state_backend._RustvelloStateBackend
    :summary:
    ```
* - {py:obj}`RustMemStateBackend <pynenc_rustvello.state_backend.RustMemStateBackend>`
  -
* - {py:obj}`RustSqliteStateBackend <pynenc_rustvello.state_backend.RustSqliteStateBackend>`
  -
* - {py:obj}`RustPostgresStateBackend <pynenc_rustvello.state_backend.RustPostgresStateBackend>`
  -
* - {py:obj}`RustRedisStateBackend <pynenc_rustvello.state_backend.RustRedisStateBackend>`
  -
* - {py:obj}`RustMongoStateBackend <pynenc_rustvello.state_backend.RustMongoStateBackend>`
  -
* - {py:obj}`RustMongo3StateBackend <pynenc_rustvello.state_backend.RustMongo3StateBackend>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_is_rust_not_found <pynenc_rustvello.state_backend._is_rust_not_found>`
  - ```{autodoc2-docstring} pynenc_rustvello.state_backend._is_rust_not_found
    :summary:
    ```
* - {py:obj}`_datetime_to_us <pynenc_rustvello.state_backend._datetime_to_us>`
  - ```{autodoc2-docstring} pynenc_rustvello.state_backend._datetime_to_us
    :summary:
    ```
* - {py:obj}`_pascal_to_upper_snake <pynenc_rustvello.state_backend._pascal_to_upper_snake>`
  - ```{autodoc2-docstring} pynenc_rustvello.state_backend._pascal_to_upper_snake
    :summary:
    ```
* - {py:obj}`_workflow_to_rust_json <pynenc_rustvello.state_backend._workflow_to_rust_json>`
  - ```{autodoc2-docstring} pynenc_rustvello.state_backend._workflow_to_rust_json
    :summary:
    ```
* - {py:obj}`_workflow_from_rust <pynenc_rustvello.state_backend._workflow_from_rust>`
  - ```{autodoc2-docstring} pynenc_rustvello.state_backend._workflow_from_rust
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_PASCAL_TO_SNAKE_RE <pynenc_rustvello.state_backend._PASCAL_TO_SNAKE_RE>`
  - ```{autodoc2-docstring} pynenc_rustvello.state_backend._PASCAL_TO_SNAKE_RE
    :summary:
    ```
* - {py:obj}`_EPOCH <pynenc_rustvello.state_backend._EPOCH>`
  - ```{autodoc2-docstring} pynenc_rustvello.state_backend._EPOCH
    :summary:
    ```
````

### API

````{py:data} _PASCAL_TO_SNAKE_RE
:canonical: pynenc_rustvello.state_backend._PASCAL_TO_SNAKE_RE
:value: >
   'compile(...)'

```{autodoc2-docstring} pynenc_rustvello.state_backend._PASCAL_TO_SNAKE_RE
```

````

````{py:data} _EPOCH
:canonical: pynenc_rustvello.state_backend._EPOCH
:value: >
   'datetime(...)'

```{autodoc2-docstring} pynenc_rustvello.state_backend._EPOCH
```

````

````{py:function} _is_rust_not_found(exc: Exception, kind: str) -> bool
:canonical: pynenc_rustvello.state_backend._is_rust_not_found

```{autodoc2-docstring} pynenc_rustvello.state_backend._is_rust_not_found
```
````

````{py:function} _datetime_to_us(ts: datetime.datetime | None) -> int | None
:canonical: pynenc_rustvello.state_backend._datetime_to_us

```{autodoc2-docstring} pynenc_rustvello.state_backend._datetime_to_us
```
````

````{py:function} _pascal_to_upper_snake(name: str) -> str
:canonical: pynenc_rustvello.state_backend._pascal_to_upper_snake

```{autodoc2-docstring} pynenc_rustvello.state_backend._pascal_to_upper_snake
```
````

````{py:function} _workflow_to_rust_json(wf: pynenc.workflow.WorkflowIdentity) -> str
:canonical: pynenc_rustvello.state_backend._workflow_to_rust_json

```{autodoc2-docstring} pynenc_rustvello.state_backend._workflow_to_rust_json
```
````

````{py:function} _workflow_from_rust(wf_data: dict) -> pynenc.workflow.workflow_identity.WorkflowIdentity
:canonical: pynenc_rustvello.state_backend._workflow_from_rust

```{autodoc2-docstring} pynenc_rustvello.state_backend._workflow_from_rust
```
````

`````{py:class} _RustvelloStateBackend(app: pynenc.app.Pynenc, rust_sb: typing.Any)
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend

Bases: {py:obj}`pynenc.state_backend.base_state_backend.BaseStateBackend`\[{py:obj}`Params`\, {py:obj}`Result`\]

```{autodoc2-docstring} pynenc_rustvello.state_backend._RustvelloStateBackend
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.state_backend._RustvelloStateBackend.__init__
```

````{py:method} purge() -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.purge

````

````{py:method} _upsert_invocations(entries: list[tuple[pynenc.models.invocation_dto.InvocationDTO, pynenc.models.call_dto.CallDTO]]) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._upsert_invocations

````

````{py:method} _get_invocation(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> tuple[pynenc.models.invocation_dto.InvocationDTO, pynenc.models.call_dto.CallDTO] | None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._get_invocation

````

````{py:method} _reconstruct_dtos(inv_json_str: str) -> tuple[pynenc.models.invocation_dto.InvocationDTO, pynenc.models.call_dto.CallDTO]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._reconstruct_dtos

```{autodoc2-docstring} pynenc_rustvello.state_backend._RustvelloStateBackend._reconstruct_dtos
```

````

````{py:method} get_child_invocations(parent_invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_child_invocations

````

````{py:method} _add_histories(invocation_ids: list[pynenc.identifiers.invocation_id.InvocationId], invocation_history: pynenc.state_backend.base_state_backend.InvocationHistory) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._add_histories

````

````{py:method} _get_history(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> list[pynenc.state_backend.base_state_backend.InvocationHistory]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._get_history

````

````{py:method} _set_result(invocation_id: pynenc.identifiers.invocation_id.InvocationId, serialized_result: str) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._set_result

````

````{py:method} _get_result(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> str
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._get_result

````

````{py:method} _set_exception(invocation_id: pynenc.identifiers.invocation_id.InvocationId, serialized_exception: str) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._set_exception

````

````{py:method} _get_exception(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> str
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._get_exception

````

````{py:method} set_workflow_data(workflow_identity: pynenc.workflow.WorkflowIdentity, key: str, value: typing.Any) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.set_workflow_data

````

````{py:method} get_workflow_data(workflow_identity: pynenc.workflow.WorkflowIdentity, key: str, default: typing.Any = None) -> typing.Any
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_workflow_data

````

````{py:method} store_app_info(app_info: pynenc.app_info.AppInfo) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.store_app_info

````

````{py:method} get_app_info() -> pynenc.app_info.AppInfo
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_app_info

````

````{py:method} discover_app_infos() -> dict[str, pynenc.app_info.AppInfo]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.discover_app_infos

````

````{py:method} store_workflow_run(workflow_identity: pynenc.workflow.WorkflowIdentity) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.store_workflow_run

````

````{py:method} get_all_workflow_types() -> collections.abc.Iterator[pynenc.identifiers.task_id.TaskId]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_all_workflow_types

````

````{py:method} get_all_workflow_runs() -> collections.abc.Iterator[pynenc.workflow.WorkflowIdentity]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_all_workflow_runs

````

````{py:method} get_workflow_runs(workflow_type: pynenc.identifiers.task_id.TaskId) -> collections.abc.Iterator[pynenc.workflow.WorkflowIdentity]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_workflow_runs

````

````{py:method} store_workflow_sub_invocation(parent_workflow_id: pynenc.identifiers.invocation_id.InvocationId, sub_invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.store_workflow_sub_invocation

````

````{py:method} get_workflow_sub_invocations(workflow_id: pynenc.identifiers.invocation_id.InvocationId) -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_workflow_sub_invocations

````

````{py:method} iter_invocations_in_timerange(start_time: datetime.datetime, end_time: datetime.datetime, batch_size: int = 100) -> collections.abc.Iterator[list[pynenc.identifiers.invocation_id.InvocationId]]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.iter_invocations_in_timerange

````

````{py:method} iter_history_in_timerange(start_time: datetime.datetime, end_time: datetime.datetime, batch_size: int = 100) -> collections.abc.Iterator[list[pynenc.state_backend.base_state_backend.InvocationHistory]]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.iter_history_in_timerange

````

````{py:method} _store_runner_context(runner_context: pynenc.runner.runner_context.RunnerContext) -> None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._store_runner_context

````

````{py:method} get_matching_runner_contexts(partial_id: str) -> collections.abc.Iterator[pynenc.runner.runner_context.RunnerContext]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_matching_runner_contexts

````

````{py:method} get_invocation_ids_by_workflow(workflow_id: str | None = None, workflow_type_key: str | None = None) -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend.get_invocation_ids_by_workflow

````

````{py:method} _get_runner_context(runner_id: str) -> pynenc.runner.runner_context.RunnerContext | None
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._get_runner_context

````

````{py:method} _get_runner_contexts(runner_ids: list[str]) -> list[pynenc.runner.runner_context.RunnerContext]
:canonical: pynenc_rustvello.state_backend._RustvelloStateBackend._get_runner_contexts

````

`````

```{py:class} RustMemStateBackend(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.state_backend.RustMemStateBackend

Bases: {py:obj}`pynenc_rustvello.state_backend._RustvelloStateBackend`

```

```{py:class} RustSqliteStateBackend(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.state_backend.RustSqliteStateBackend

Bases: {py:obj}`pynenc_rustvello.state_backend._RustvelloStateBackend`

```

```{py:class} RustPostgresStateBackend(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.state_backend.RustPostgresStateBackend

Bases: {py:obj}`pynenc_rustvello.state_backend._RustvelloStateBackend`

```

```{py:class} RustRedisStateBackend(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.state_backend.RustRedisStateBackend

Bases: {py:obj}`pynenc_rustvello.state_backend._RustvelloStateBackend`

```

```{py:class} RustMongoStateBackend(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.state_backend.RustMongoStateBackend

Bases: {py:obj}`pynenc_rustvello.state_backend._RustvelloStateBackend`

```

```{py:class} RustMongo3StateBackend(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.state_backend.RustMongo3StateBackend

Bases: {py:obj}`pynenc_rustvello.state_backend._RustvelloStateBackend`

```
