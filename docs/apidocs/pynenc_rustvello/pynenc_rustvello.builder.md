# {py:mod}`pynenc_rustvello.builder`

```{py:module} pynenc_rustvello.builder
```

```{autodoc2-docstring} pynenc_rustvello.builder
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RustvelloBuilderPlugin <pynenc_rustvello.builder.RustvelloBuilderPlugin>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder.RustvelloBuilderPlugin
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_is_all_rust_native <pynenc_rustvello.builder._is_all_rust_native>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._is_all_rust_native
    :summary:
    ```
* - {py:obj}`_check_backend_available <pynenc_rustvello.builder._check_backend_available>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._check_backend_available
    :summary:
    ```
* - {py:obj}`_import_rustvello_adapters <pynenc_rustvello.builder._import_rustvello_adapters>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._import_rustvello_adapters
    :summary:
    ```
* - {py:obj}`_rustvello_builder_method <pynenc_rustvello.builder._rustvello_builder_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_builder_method
    :summary:
    ```
* - {py:obj}`_set_component <pynenc_rustvello.builder._set_component>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._set_component
    :summary:
    ```
* - {py:obj}`_rustvello_mem_method <pynenc_rustvello.builder._rustvello_mem_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_mem_method
    :summary:
    ```
* - {py:obj}`_rustvello_sqlite_method <pynenc_rustvello.builder._rustvello_sqlite_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_sqlite_method
    :summary:
    ```
* - {py:obj}`_rustvello_redis_method <pynenc_rustvello.builder._rustvello_redis_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_method
    :summary:
    ```
* - {py:obj}`_rustvello_postgres_method <pynenc_rustvello.builder._rustvello_postgres_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_postgres_method
    :summary:
    ```
* - {py:obj}`_rustvello_mongo_method <pynenc_rustvello.builder._rustvello_mongo_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_mongo_method
    :summary:
    ```
* - {py:obj}`_rustvello_mongo3_method <pynenc_rustvello.builder._rustvello_mongo3_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_mongo3_method
    :summary:
    ```
* - {py:obj}`_rustvello_rabbitmq_broker_method <pynenc_rustvello.builder._rustvello_rabbitmq_broker_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_rabbitmq_broker_method
    :summary:
    ```
* - {py:obj}`_rustvello_redis_broker_method <pynenc_rustvello.builder._rustvello_redis_broker_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_broker_method
    :summary:
    ```
* - {py:obj}`_rustvello_redis_orchestrator_method <pynenc_rustvello.builder._rustvello_redis_orchestrator_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_orchestrator_method
    :summary:
    ```
* - {py:obj}`_rustvello_redis_state_method <pynenc_rustvello.builder._rustvello_redis_state_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_state_method
    :summary:
    ```
* - {py:obj}`_rustvello_redis_trigger_method <pynenc_rustvello.builder._rustvello_redis_trigger_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_trigger_method
    :summary:
    ```
* - {py:obj}`_rustvello_redis_cds_method <pynenc_rustvello.builder._rustvello_redis_cds_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_cds_method
    :summary:
    ```
* - {py:obj}`_rustvello_postgres_state_method <pynenc_rustvello.builder._rustvello_postgres_state_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_postgres_state_method
    :summary:
    ```
* - {py:obj}`_rustvello_postgres_orchestrator_method <pynenc_rustvello.builder._rustvello_postgres_orchestrator_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_postgres_orchestrator_method
    :summary:
    ```
* - {py:obj}`_rust_runner_builder_method <pynenc_rustvello.builder._rust_runner_builder_method>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._rust_runner_builder_method
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_BACKEND_CONFIGS <pynenc_rustvello.builder._BACKEND_CONFIGS>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._BACKEND_CONFIGS
    :summary:
    ```
* - {py:obj}`_NATIVE_ORCHESTRATOR <pynenc_rustvello.builder._NATIVE_ORCHESTRATOR>`
  - ```{autodoc2-docstring} pynenc_rustvello.builder._NATIVE_ORCHESTRATOR
    :summary:
    ```
````

### API

````{py:data} _BACKEND_CONFIGS
:canonical: pynenc_rustvello.builder._BACKEND_CONFIGS
:type: dict[str, dict[str, str]]
:value: >
   None

```{autodoc2-docstring} pynenc_rustvello.builder._BACKEND_CONFIGS
```

````

````{py:data} _NATIVE_ORCHESTRATOR
:canonical: pynenc_rustvello.builder._NATIVE_ORCHESTRATOR
:type: dict[str, str]
:value: >
   None

```{autodoc2-docstring} pynenc_rustvello.builder._NATIVE_ORCHESTRATOR
```

````

````{py:function} _is_all_rust_native(config_values: dict[str, typing.Any]) -> bool
:canonical: pynenc_rustvello.builder._is_all_rust_native

```{autodoc2-docstring} pynenc_rustvello.builder._is_all_rust_native
```
````

````{py:function} _check_backend_available(backend: str) -> None
:canonical: pynenc_rustvello.builder._check_backend_available

```{autodoc2-docstring} pynenc_rustvello.builder._check_backend_available
```
````

````{py:function} _import_rustvello_adapters() -> None
:canonical: pynenc_rustvello.builder._import_rustvello_adapters

```{autodoc2-docstring} pynenc_rustvello.builder._import_rustvello_adapters
```
````

````{py:function} _rustvello_builder_method(builder: pynenc.builder.PynencBuilder, backend: str = 'mem', native: bool = True, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_builder_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_builder_method
```
````

````{py:function} _set_component(builder: pynenc.builder.PynencBuilder, component_key: str, class_name: str, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._set_component

```{autodoc2-docstring} pynenc_rustvello.builder._set_component
```
````

````{py:function} _rustvello_mem_method(builder: pynenc.builder.PynencBuilder, native: bool = True) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_mem_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_mem_method
```
````

````{py:function} _rustvello_sqlite_method(builder: pynenc.builder.PynencBuilder, sqlite_db_path: str | None = None, native: bool = True, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_sqlite_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_sqlite_method
```
````

````{py:function} _rustvello_redis_method(builder: pynenc.builder.PynencBuilder, redis_url: str | None = None, native: bool = True, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_redis_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_method
```
````

````{py:function} _rustvello_postgres_method(builder: pynenc.builder.PynencBuilder, postgres_url: str | None = None, native: bool = True, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_postgres_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_postgres_method
```
````

````{py:function} _rustvello_mongo_method(builder: pynenc.builder.PynencBuilder, mongo_url: str | None = None, mongo_db_name: str | None = None, native: bool = True, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_mongo_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_mongo_method
```
````

````{py:function} _rustvello_mongo3_method(builder: pynenc.builder.PynencBuilder, mongo_url: str | None = None, mongo_db_name: str | None = None, native: bool = True, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_mongo3_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_mongo3_method
```
````

````{py:function} _rustvello_rabbitmq_broker_method(builder: pynenc.builder.PynencBuilder, rabbitmq_url: str, rabbitmq_prefix: str | None = None, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_rabbitmq_broker_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_rabbitmq_broker_method
```
````

````{py:function} _rustvello_redis_broker_method(builder: pynenc.builder.PynencBuilder, redis_url: str | None = None, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_redis_broker_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_broker_method
```
````

````{py:function} _rustvello_redis_orchestrator_method(builder: pynenc.builder.PynencBuilder, redis_url: str | None = None, native: bool = True, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_redis_orchestrator_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_orchestrator_method
```
````

````{py:function} _rustvello_redis_state_method(builder: pynenc.builder.PynencBuilder, redis_url: str | None = None, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_redis_state_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_state_method
```
````

````{py:function} _rustvello_redis_trigger_method(builder: pynenc.builder.PynencBuilder, redis_url: str | None = None, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_redis_trigger_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_trigger_method
```
````

````{py:function} _rustvello_redis_cds_method(builder: pynenc.builder.PynencBuilder, redis_url: str | None = None, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_redis_cds_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_redis_cds_method
```
````

````{py:function} _rustvello_postgres_state_method(builder: pynenc.builder.PynencBuilder, postgres_url: str | None = None, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_postgres_state_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_postgres_state_method
```
````

````{py:function} _rustvello_postgres_orchestrator_method(builder: pynenc.builder.PynencBuilder, postgres_url: str | None = None, native: bool = True, **kwargs: typing.Any) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rustvello_postgres_orchestrator_method

```{autodoc2-docstring} pynenc_rustvello.builder._rustvello_postgres_orchestrator_method
```
````

````{py:function} _rust_runner_builder_method(builder: pynenc.builder.PynencBuilder) -> pynenc.builder.PynencBuilder
:canonical: pynenc_rustvello.builder._rust_runner_builder_method

```{autodoc2-docstring} pynenc_rustvello.builder._rust_runner_builder_method
```
````

`````{py:class} RustvelloBuilderPlugin
:canonical: pynenc_rustvello.builder.RustvelloBuilderPlugin

```{autodoc2-docstring} pynenc_rustvello.builder.RustvelloBuilderPlugin
```

````{py:method} register_builder_methods(builder_cls: type[pynenc.builder.PynencBuilder]) -> None
:canonical: pynenc_rustvello.builder.RustvelloBuilderPlugin.register_builder_methods
:classmethod:

```{autodoc2-docstring} pynenc_rustvello.builder.RustvelloBuilderPlugin.register_builder_methods
```

````

`````
