# {py:mod}`pynenc_rustvello.broker`

```{py:module} pynenc_rustvello.broker
```

```{autodoc2-docstring} pynenc_rustvello.broker
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_RustvelloBroker <pynenc_rustvello.broker._RustvelloBroker>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker._RustvelloBroker
    :summary:
    ```
* - {py:obj}`RustMemBroker <pynenc_rustvello.broker.RustMemBroker>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker.RustMemBroker
    :summary:
    ```
* - {py:obj}`RustSqliteBroker <pynenc_rustvello.broker.RustSqliteBroker>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker.RustSqliteBroker
    :summary:
    ```
* - {py:obj}`RustPostgresBroker <pynenc_rustvello.broker.RustPostgresBroker>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker.RustPostgresBroker
    :summary:
    ```
* - {py:obj}`RustRedisBroker <pynenc_rustvello.broker.RustRedisBroker>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker.RustRedisBroker
    :summary:
    ```
* - {py:obj}`RustMongoBroker <pynenc_rustvello.broker.RustMongoBroker>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker.RustMongoBroker
    :summary:
    ```
* - {py:obj}`RustMongo3Broker <pynenc_rustvello.broker.RustMongo3Broker>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker.RustMongo3Broker
    :summary:
    ```
* - {py:obj}`RustRabbitmqBroker <pynenc_rustvello.broker.RustRabbitmqBroker>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker.RustRabbitmqBroker
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_get_or_create_sqlite_db <pynenc_rustvello.broker._get_or_create_sqlite_db>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_sqlite_db
    :summary:
    ```
* - {py:obj}`_get_or_create_postgres_db <pynenc_rustvello.broker._get_or_create_postgres_db>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_postgres_db
    :summary:
    ```
* - {py:obj}`_get_or_create_redis_pool <pynenc_rustvello.broker._get_or_create_redis_pool>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_redis_pool
    :summary:
    ```
* - {py:obj}`_get_or_create_mongo_pool <pynenc_rustvello.broker._get_or_create_mongo_pool>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_mongo_pool
    :summary:
    ```
* - {py:obj}`_get_or_create_mongo3_pool <pynenc_rustvello.broker._get_or_create_mongo3_pool>`
  - ```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_mongo3_pool
    :summary:
    ```
````

### API

````{py:function} _get_or_create_sqlite_db(app: typing.Any) -> typing.Any
:canonical: pynenc_rustvello.broker._get_or_create_sqlite_db

```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_sqlite_db
```
````

````{py:function} _get_or_create_postgres_db(app: typing.Any) -> typing.Any
:canonical: pynenc_rustvello.broker._get_or_create_postgres_db

```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_postgres_db
```
````

````{py:function} _get_or_create_redis_pool(app: typing.Any) -> typing.Any
:canonical: pynenc_rustvello.broker._get_or_create_redis_pool

```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_redis_pool
```
````

````{py:function} _get_or_create_mongo_pool(app: typing.Any) -> typing.Any
:canonical: pynenc_rustvello.broker._get_or_create_mongo_pool

```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_mongo_pool
```
````

`````{py:class} _RustvelloBroker(app: pynenc.app.Pynenc, rust_broker: typing.Any)
:canonical: pynenc_rustvello.broker._RustvelloBroker

Bases: {py:obj}`pynenc.broker.base_broker.BaseBroker`

```{autodoc2-docstring} pynenc_rustvello.broker._RustvelloBroker
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.broker._RustvelloBroker.__init__
```

````{py:method} route_invocation(invocation_id: pynenc.identifiers.invocation_id.InvocationId) -> None
:canonical: pynenc_rustvello.broker._RustvelloBroker.route_invocation

````

````{py:method} route_invocations(invocation_ids: list[pynenc.identifiers.invocation_id.InvocationId]) -> None
:canonical: pynenc_rustvello.broker._RustvelloBroker.route_invocations

````

````{py:method} retrieve_invocation() -> pynenc.identifiers.invocation_id.InvocationId | None
:canonical: pynenc_rustvello.broker._RustvelloBroker.retrieve_invocation

````

````{py:method} count_invocations() -> int
:canonical: pynenc_rustvello.broker._RustvelloBroker.count_invocations

````

````{py:method} purge() -> None
:canonical: pynenc_rustvello.broker._RustvelloBroker.purge

````

````{py:method} route_invocation_for_task(invocation_id: pynenc.identifiers.invocation_id.InvocationId, task_id: pynenc.identifiers.task_id.TaskId) -> None
:canonical: pynenc_rustvello.broker._RustvelloBroker.route_invocation_for_task

```{autodoc2-docstring} pynenc_rustvello.broker._RustvelloBroker.route_invocation_for_task
```

````

````{py:method} retrieve_invocation_for_task(task_id: pynenc.identifiers.task_id.TaskId) -> pynenc.identifiers.invocation_id.InvocationId | None
:canonical: pynenc_rustvello.broker._RustvelloBroker.retrieve_invocation_for_task

```{autodoc2-docstring} pynenc_rustvello.broker._RustvelloBroker.retrieve_invocation_for_task
```

````

````{py:method} retrieve_invocation_for_language(language: str) -> pynenc.identifiers.invocation_id.InvocationId | None
:canonical: pynenc_rustvello.broker._RustvelloBroker.retrieve_invocation_for_language

```{autodoc2-docstring} pynenc_rustvello.broker._RustvelloBroker.retrieve_invocation_for_language
```

````

````{py:method} count_invocations_for_task(task_id: pynenc.identifiers.task_id.TaskId) -> int
:canonical: pynenc_rustvello.broker._RustvelloBroker.count_invocations_for_task

```{autodoc2-docstring} pynenc_rustvello.broker._RustvelloBroker.count_invocations_for_task
```

````

````{py:method} purge_task(task_id: pynenc.identifiers.task_id.TaskId) -> None
:canonical: pynenc_rustvello.broker._RustvelloBroker.purge_task

```{autodoc2-docstring} pynenc_rustvello.broker._RustvelloBroker.purge_task
```

````

`````

````{py:class} RustMemBroker(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.broker.RustMemBroker

Bases: {py:obj}`pynenc_rustvello.broker._RustvelloBroker`

```{autodoc2-docstring} pynenc_rustvello.broker.RustMemBroker
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.broker.RustMemBroker.__init__
```

````

````{py:class} RustSqliteBroker(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.broker.RustSqliteBroker

Bases: {py:obj}`pynenc_rustvello.broker._RustvelloBroker`

```{autodoc2-docstring} pynenc_rustvello.broker.RustSqliteBroker
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.broker.RustSqliteBroker.__init__
```

````

````{py:class} RustPostgresBroker(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.broker.RustPostgresBroker

Bases: {py:obj}`pynenc_rustvello.broker._RustvelloBroker`

```{autodoc2-docstring} pynenc_rustvello.broker.RustPostgresBroker
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.broker.RustPostgresBroker.__init__
```

````

````{py:class} RustRedisBroker(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.broker.RustRedisBroker

Bases: {py:obj}`pynenc_rustvello.broker._RustvelloBroker`

```{autodoc2-docstring} pynenc_rustvello.broker.RustRedisBroker
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.broker.RustRedisBroker.__init__
```

````

````{py:class} RustMongoBroker(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.broker.RustMongoBroker

Bases: {py:obj}`pynenc_rustvello.broker._RustvelloBroker`

```{autodoc2-docstring} pynenc_rustvello.broker.RustMongoBroker
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.broker.RustMongoBroker.__init__
```

````

````{py:function} _get_or_create_mongo3_pool(app: typing.Any) -> typing.Any
:canonical: pynenc_rustvello.broker._get_or_create_mongo3_pool

```{autodoc2-docstring} pynenc_rustvello.broker._get_or_create_mongo3_pool
```
````

````{py:class} RustMongo3Broker(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.broker.RustMongo3Broker

Bases: {py:obj}`pynenc_rustvello.broker._RustvelloBroker`

```{autodoc2-docstring} pynenc_rustvello.broker.RustMongo3Broker
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.broker.RustMongo3Broker.__init__
```

````

````{py:class} RustRabbitmqBroker(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.broker.RustRabbitmqBroker

Bases: {py:obj}`pynenc_rustvello.broker._RustvelloBroker`

```{autodoc2-docstring} pynenc_rustvello.broker.RustRabbitmqBroker
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.broker.RustRabbitmqBroker.__init__
```

````
