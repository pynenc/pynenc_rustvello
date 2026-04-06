# {py:mod}`pynenc_rustvello.runner`

```{py:module} pynenc_rustvello.runner
```

```{autodoc2-docstring} pynenc_rustvello.runner
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RustMemRunner <pynenc_rustvello.runner.RustMemRunner>`
  - ```{autodoc2-docstring} pynenc_rustvello.runner.RustMemRunner
    :summary:
    ```
* - {py:obj}`_RustInvocationProxy <pynenc_rustvello.runner._RustInvocationProxy>`
  - ```{autodoc2-docstring} pynenc_rustvello.runner._RustInvocationProxy
    :summary:
    ```
* - {py:obj}`RustPythonRunner <pynenc_rustvello.runner.RustPythonRunner>`
  - ```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_make_task_wrapper <pynenc_rustvello.runner._make_task_wrapper>`
  - ```{autodoc2-docstring} pynenc_rustvello.runner._make_task_wrapper
    :summary:
    ```
````

### API

`````{py:class} RustMemRunner(app: pynenc.app.Pynenc, runner_cache: dict | None = None, runner_context: pynenc.runner.runner_context.RunnerContext | None = None)
:canonical: pynenc_rustvello.runner.RustMemRunner

Bases: {py:obj}`pynenc.runner.base_runner.BaseRunner`

```{autodoc2-docstring} pynenc_rustvello.runner.RustMemRunner
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.runner.RustMemRunner.__init__
```

````{py:method} conf() -> pynenc_rustvello.conf.config_runner.ConfigRustRunner
:canonical: pynenc_rustvello.runner.RustMemRunner.conf

```{autodoc2-docstring} pynenc_rustvello.runner.RustMemRunner.conf
```

````

````{py:method} mem_compatible() -> bool
:canonical: pynenc_rustvello.runner.RustMemRunner.mem_compatible
:staticmethod:

````

````{py:property} max_parallel_slots
:canonical: pynenc_rustvello.runner.RustMemRunner.max_parallel_slots
:type: int

````

````{py:method} get_active_child_runner_ids() -> list[str]
:canonical: pynenc_rustvello.runner.RustMemRunner.get_active_child_runner_ids

````

````{py:method} _on_start() -> None
:canonical: pynenc_rustvello.runner.RustMemRunner._on_start

````

````{py:method} _on_stop() -> None
:canonical: pynenc_rustvello.runner.RustMemRunner._on_stop

````

````{py:method} _on_stop_runner_loop() -> None
:canonical: pynenc_rustvello.runner.RustMemRunner._on_stop_runner_loop

````

````{py:method} _kill_and_reroute_rust_invocations() -> None
:canonical: pynenc_rustvello.runner.RustMemRunner._kill_and_reroute_rust_invocations

```{autodoc2-docstring} pynenc_rustvello.runner.RustMemRunner._kill_and_reroute_rust_invocations
```

````

````{py:method} _signal_aware_run_one() -> None
:canonical: pynenc_rustvello.runner.RustMemRunner._signal_aware_run_one

```{autodoc2-docstring} pynenc_rustvello.runner.RustMemRunner._signal_aware_run_one
```

````

````{py:method} runner_loop_iteration() -> None
:canonical: pynenc_rustvello.runner.RustMemRunner.runner_loop_iteration

````

````{py:method} _waiting_for_results(running_invocation_id: pynenc.identifiers.invocation_id.InvocationId, result_invocation_ids: list[pynenc.identifiers.invocation_id.InvocationId], runner_args: dict[str, typing.Any] | None = None) -> None
:canonical: pynenc_rustvello.runner.RustMemRunner._waiting_for_results

````

````{py:method} _ensure_rust_runner() -> None
:canonical: pynenc_rustvello.runner.RustMemRunner._ensure_rust_runner

```{autodoc2-docstring} pynenc_rustvello.runner.RustMemRunner._ensure_rust_runner
```

````

````{py:method} _build_rust_runner() -> None
:canonical: pynenc_rustvello.runner.RustMemRunner._build_rust_runner

```{autodoc2-docstring} pynenc_rustvello.runner.RustMemRunner._build_rust_runner
```

````

`````

`````{py:class} _RustInvocationProxy(invocation_id_str: str, task: typing.Any, app: typing.Any)
:canonical: pynenc_rustvello.runner._RustInvocationProxy

```{autodoc2-docstring} pynenc_rustvello.runner._RustInvocationProxy
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.runner._RustInvocationProxy.__init__
```

````{py:property} workflow
:canonical: pynenc_rustvello.runner._RustInvocationProxy.workflow
:type: typing.Any

```{autodoc2-docstring} pynenc_rustvello.runner._RustInvocationProxy.workflow
```

````

````{py:property} num_retries
:canonical: pynenc_rustvello.runner._RustInvocationProxy.num_retries
:type: int

```{autodoc2-docstring} pynenc_rustvello.runner._RustInvocationProxy.num_retries
```

````

`````

````{py:function} _make_task_wrapper(task: pynenc.task.Task, app: pynenc.app.Pynenc) -> typing.Any
:canonical: pynenc_rustvello.runner._make_task_wrapper

```{autodoc2-docstring} pynenc_rustvello.runner._make_task_wrapper
```
````

`````{py:class} RustPythonRunner(app: pynenc.app.Pynenc, runner_cache: dict | None = None, runner_context: pynenc.runner.runner_context.RunnerContext | None = None)
:canonical: pynenc_rustvello.runner.RustPythonRunner

Bases: {py:obj}`pynenc.runner.base_runner.BaseRunner`

```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner.__init__
```

````{py:method} conf() -> pynenc_rustvello.conf.config_runner.ConfigRustRunner
:canonical: pynenc_rustvello.runner.RustPythonRunner.conf

```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner.conf
```

````

````{py:method} mem_compatible() -> bool
:canonical: pynenc_rustvello.runner.RustPythonRunner.mem_compatible
:staticmethod:

````

````{py:property} max_parallel_slots
:canonical: pynenc_rustvello.runner.RustPythonRunner.max_parallel_slots
:type: int

````

````{py:property} is_rust_runner
:canonical: pynenc_rustvello.runner.RustPythonRunner.is_rust_runner
:type: bool

```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner.is_rust_runner
```

````

````{py:method} get_active_child_runner_ids() -> list[str]
:canonical: pynenc_rustvello.runner.RustPythonRunner.get_active_child_runner_ids

````

````{py:method} _on_start() -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner._on_start

````

````{py:method} _on_stop() -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner._on_stop

````

````{py:method} _on_stop_runner_loop() -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner._on_stop_runner_loop

````

````{py:method} _kill_and_reroute_rust_invocations() -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner._kill_and_reroute_rust_invocations

```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner._kill_and_reroute_rust_invocations
```

````

````{py:method} _signal_aware_run_one() -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner._signal_aware_run_one

```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner._signal_aware_run_one
```

````

````{py:method} run() -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner.run

```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner.run
```

````

````{py:method} runner_loop_iteration() -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner.runner_loop_iteration

````

````{py:method} _waiting_for_results(running_invocation_id: pynenc.identifiers.invocation_id.InvocationId, result_invocation_ids: list[pynenc.identifiers.invocation_id.InvocationId], runner_args: dict[str, typing.Any] | None = None) -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner._waiting_for_results

````

````{py:method} _build_rust_runner() -> None
:canonical: pynenc_rustvello.runner.RustPythonRunner._build_rust_runner

```{autodoc2-docstring} pynenc_rustvello.runner.RustPythonRunner._build_rust_runner
```

````

`````
