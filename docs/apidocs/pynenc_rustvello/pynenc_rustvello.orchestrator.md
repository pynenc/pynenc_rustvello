# {py:mod}`pynenc_rustvello.orchestrator`

```{py:module} pynenc_rustvello.orchestrator
```

```{autodoc2-docstring} pynenc_rustvello.orchestrator
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_RustBlockingControl <pynenc_rustvello.orchestrator._RustBlockingControl>`
  - ```{autodoc2-docstring} pynenc_rustvello.orchestrator._RustBlockingControl
    :summary:
    ```
* - {py:obj}`_RustvelloOrchestrator <pynenc_rustvello.orchestrator._RustvelloOrchestrator>`
  - ```{autodoc2-docstring} pynenc_rustvello.orchestrator._RustvelloOrchestrator
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_record_from_rust <pynenc_rustvello.orchestrator._record_from_rust>`
  - ```{autodoc2-docstring} pynenc_rustvello.orchestrator._record_from_rust
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pynenc_rustvello.orchestrator.__all__>`
  - ```{autodoc2-docstring} pynenc_rustvello.orchestrator.__all__
    :summary:
    ```
````

### API

````{py:function} _record_from_rust(status_str: str, runner_id: str | None, ts: float) -> pynenc.invocation.status.InvocationStatusRecord
:canonical: pynenc_rustvello.orchestrator._record_from_rust

```{autodoc2-docstring} pynenc_rustvello.orchestrator._record_from_rust
```
````

`````{py:class} _RustBlockingControl(rust_orch: typing.Any)
:canonical: pynenc_rustvello.orchestrator._RustBlockingControl

Bases: {py:obj}`pynenc.orchestrator.base_orchestrator.BaseBlockingControl`

```{autodoc2-docstring} pynenc_rustvello.orchestrator._RustBlockingControl
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.orchestrator._RustBlockingControl.__init__
```

````{py:method} waiting_for_results(caller_invocation_id: pynenc.identifiers.invocation_id.InvocationId, result_invocation_ids: list[pynenc.identifiers.invocation_id.InvocationId]) -> None
:canonical: pynenc_rustvello.orchestrator._RustBlockingControl.waiting_for_results

````

````{py:method} release_waiters(waited_invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> None
:canonical: pynenc_rustvello.orchestrator._RustBlockingControl.release_waiters

````

````{py:method} get_blocking_invocations(max_num_invocations: int) -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.orchestrator._RustBlockingControl.get_blocking_invocations

````

`````

`````{py:class} _RustvelloOrchestrator(app: pynenc.app.Pynenc, rust_orch: typing.Any)
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator

Bases: {py:obj}`pynenc.orchestrator.base_orchestrator.BaseOrchestrator`

```{autodoc2-docstring} pynenc_rustvello.orchestrator._RustvelloOrchestrator
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.orchestrator._RustvelloOrchestrator.__init__
```

````{py:method} _register_new_invocations(invocations: list[pynenc.invocation.dist_invocation.DistributedInvocation[pynenc.types.Params, pynenc.types.Result]], runner_id: str | None = None) -> pynenc.invocation.status.InvocationStatusRecord
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator._register_new_invocations

````

````{py:method} get_invocation_status_record(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> pynenc.invocation.status.InvocationStatusRecord
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_invocation_status_record

````

````{py:method} _atomic_status_transition(invocation_id: pynenc.identifiers.invocation_id.InvocationId, status: pynenc.invocation.status.InvocationStatus, runner_id: str | None = None) -> pynenc.invocation.status.InvocationStatusRecord
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator._atomic_status_transition

````

````{py:method} get_existing_invocations(task: pynenc.task.Task[pynenc.types.Params, pynenc.types.Result], key_serialized_arguments: dict[str, str] | None = None, statuses: list[pynenc.invocation.status.InvocationStatus] | None = None) -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_existing_invocations

````

````{py:method} get_task_invocation_ids(task_id: pynenc.identifiers.task_id.TaskId) -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_task_invocation_ids

````

````{py:method} get_invocation_ids_paginated(task_id: pynenc.identifiers.task_id.TaskId | None = None, statuses: list[pynenc.invocation.status.InvocationStatus] | None = None, limit: int = 100, offset: int = 0) -> list[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_invocation_ids_paginated

````

````{py:method} count_invocations(task_id: pynenc.identifiers.task_id.TaskId | None = None, statuses: list[pynenc.invocation.status.InvocationStatus] | None = None) -> int
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.count_invocations

````

````{py:method} get_call_invocation_ids(call_id: pynenc.identifiers.call_id.CallId) -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_call_invocation_ids

````

````{py:method} index_arguments_for_concurrency_control(invocation: pynenc.invocation.dist_invocation.DistributedInvocation[pynenc.types.Params, pynenc.types.Result]) -> None
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.index_arguments_for_concurrency_control

````

````{py:method} set_up_invocation_auto_purge(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> None
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.set_up_invocation_auto_purge

````

````{py:method} auto_purge() -> None
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.auto_purge

````

````{py:method} increment_invocation_retries(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> None
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.increment_invocation_retries

````

````{py:method} get_invocation_retries(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> int
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_invocation_retries

````

````{py:method} filter_by_status(invocation_ids: list[pynenc.identifiers.invocation_id.InvocationId], status_filter: frozenset[pynenc.invocation.status.InvocationStatus]) -> list[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.filter_by_status

````

````{py:method} purge() -> None
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.purge

````

````{py:property} blocking_control
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.blocking_control
:type: pynenc.orchestrator.base_orchestrator.BaseBlockingControl

````

````{py:method} register_runner_heartbeats(runner_ids: list[str], can_run_atomic_service: bool = False) -> None
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.register_runner_heartbeats

````

````{py:method} record_atomic_service_execution(runner_id: str, start_time: typing.Any, end_time: typing.Any) -> None
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.record_atomic_service_execution

````

````{py:method} get_atomic_service_timeline() -> list[dict]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_atomic_service_timeline

```{autodoc2-docstring} pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_atomic_service_timeline
```

````

````{py:method} _get_active_runners(timeout_seconds: float, can_run_atomic_service: bool | None = None) -> list[pynenc.orchestrator.atomic_service.ActiveRunnerInfo]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator._get_active_runners

````

````{py:method} get_pending_invocations_for_recovery() -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator.get_pending_invocations_for_recovery

````

````{py:method} _get_running_invocations_for_recovery(timeout_seconds: float) -> collections.abc.Iterator[pynenc.identifiers.invocation_id.InvocationId]
:canonical: pynenc_rustvello.orchestrator._RustvelloOrchestrator._get_running_invocations_for_recovery

````

`````

````{py:data} __all__
:canonical: pynenc_rustvello.orchestrator.__all__
:value: >
   ['_RustvelloOrchestrator', '_RustvelloNativeOrchestrator', 'RustMemOrchestrator', 'RustSqliteOrchest...

```{autodoc2-docstring} pynenc_rustvello.orchestrator.__all__
```

````
