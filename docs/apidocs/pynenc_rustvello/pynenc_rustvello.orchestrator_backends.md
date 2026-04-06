# {py:mod}`pynenc_rustvello.orchestrator_backends`

```{py:module} pynenc_rustvello.orchestrator_backends
```

```{autodoc2-docstring} pynenc_rustvello.orchestrator_backends
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_RustvelloNativeOrchestrator <pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator>`
  - ```{autodoc2-docstring} pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator
    :summary:
    ```
* - {py:obj}`RustMemOrchestrator <pynenc_rustvello.orchestrator_backends.RustMemOrchestrator>`
  -
* - {py:obj}`RustSqliteOrchestrator <pynenc_rustvello.orchestrator_backends.RustSqliteOrchestrator>`
  -
* - {py:obj}`RustPostgresOrchestrator <pynenc_rustvello.orchestrator_backends.RustPostgresOrchestrator>`
  -
* - {py:obj}`RustRedisOrchestrator <pynenc_rustvello.orchestrator_backends.RustRedisOrchestrator>`
  -
* - {py:obj}`RustMongoOrchestrator <pynenc_rustvello.orchestrator_backends.RustMongoOrchestrator>`
  -
* - {py:obj}`RustMemNativeOrchestrator <pynenc_rustvello.orchestrator_backends.RustMemNativeOrchestrator>`
  -
* - {py:obj}`RustSqliteNativeOrchestrator <pynenc_rustvello.orchestrator_backends.RustSqliteNativeOrchestrator>`
  -
* - {py:obj}`RustPostgresNativeOrchestrator <pynenc_rustvello.orchestrator_backends.RustPostgresNativeOrchestrator>`
  -
* - {py:obj}`RustRedisNativeOrchestrator <pynenc_rustvello.orchestrator_backends.RustRedisNativeOrchestrator>`
  -
* - {py:obj}`RustMongoNativeOrchestrator <pynenc_rustvello.orchestrator_backends.RustMongoNativeOrchestrator>`
  -
* - {py:obj}`RustMongo3Orchestrator <pynenc_rustvello.orchestrator_backends.RustMongo3Orchestrator>`
  -
* - {py:obj}`RustMongo3NativeOrchestrator <pynenc_rustvello.orchestrator_backends.RustMongo3NativeOrchestrator>`
  -
````

### API

`````{py:class} _RustvelloNativeOrchestrator(app: pynenc.app.Pynenc, rust_orch: typing.Any)
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator._RustvelloOrchestrator`

```{autodoc2-docstring} pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.__init__
```

````{py:attribute} _rust_app
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator._rust_app
:type: typing.Any
:value: >
   None

```{autodoc2-docstring} pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator._rust_app
```

````

````{py:method} _ensure_rust_app() -> None
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator._ensure_rust_app

```{autodoc2-docstring} pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator._ensure_rust_app
```

````

````{py:method} set_invocation_status(invocation_id: pynenc.identifiers.InvocationId, status: pynenc.invocation.status.InvocationStatus, runner_ctx: typing.Any) -> None
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.set_invocation_status

````

````{py:method} set_invocation_result(invocation: pynenc.invocation.DistributedInvocation, result: typing.Any, runner_ctx: typing.Any) -> None
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.set_invocation_result

````

````{py:method} set_invocation_exception(invocation: pynenc.invocation.DistributedInvocation, exception: Exception, runner_ctx: typing.Any) -> None
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.set_invocation_exception

````

````{py:method} set_invocation_retry(invocation_id: pynenc.identifiers.InvocationId, exception: Exception, runner_ctx: typing.Any) -> None
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.set_invocation_retry

````

````{py:method} reroute_invocations(invocations_to_reroute: set[pynenc.identifiers.InvocationId], runner_ctx: typing.Any) -> None
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.reroute_invocations

````

````{py:method} route_call(call: typing.Any) -> typing.Any
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.route_call

```{autodoc2-docstring} pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.route_call
```

````

````{py:method} check_atomic_services(runner_id: str) -> list[str] | None
:canonical: pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.check_atomic_services

```{autodoc2-docstring} pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator.check_atomic_services
```

````

`````

```{py:class} RustMemOrchestrator(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.orchestrator_backends.RustMemOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator._RustvelloOrchestrator`

```

```{py:class} RustSqliteOrchestrator(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.orchestrator_backends.RustSqliteOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator._RustvelloOrchestrator`

```

```{py:class} RustPostgresOrchestrator(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.orchestrator_backends.RustPostgresOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator._RustvelloOrchestrator`

```

```{py:class} RustRedisOrchestrator(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.orchestrator_backends.RustRedisOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator._RustvelloOrchestrator`

```

```{py:class} RustMongoOrchestrator(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.orchestrator_backends.RustMongoOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator._RustvelloOrchestrator`

```

```{py:class} RustMemNativeOrchestrator(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.orchestrator_backends.RustMemNativeOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator`

```

```{py:class} RustSqliteNativeOrchestrator(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.orchestrator_backends.RustSqliteNativeOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator`

```

```{py:class} RustPostgresNativeOrchestrator(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.orchestrator_backends.RustPostgresNativeOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator`

```

```{py:class} RustRedisNativeOrchestrator(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.orchestrator_backends.RustRedisNativeOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator`

```

```{py:class} RustMongoNativeOrchestrator(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.orchestrator_backends.RustMongoNativeOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator`

```

```{py:class} RustMongo3Orchestrator(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.orchestrator_backends.RustMongo3Orchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator._RustvelloOrchestrator`

```

```{py:class} RustMongo3NativeOrchestrator(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.orchestrator_backends.RustMongo3NativeOrchestrator

Bases: {py:obj}`pynenc_rustvello.orchestrator_backends._RustvelloNativeOrchestrator`

```
