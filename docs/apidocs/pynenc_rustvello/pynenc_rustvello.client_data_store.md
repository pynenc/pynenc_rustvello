# {py:mod}`pynenc_rustvello.client_data_store`

```{py:module} pynenc_rustvello.client_data_store

```

```{autodoc2-docstring} pynenc_rustvello.client_data_store
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_RustClientDataStoreBase <pynenc_rustvello.client_data_store._RustClientDataStoreBase>`
  - ```{autodoc2-docstring} pynenc_rustvello.client_data_store._RustClientDataStoreBase
    :summary:
    ```
* - {py:obj}`RustMemClientDataStore <pynenc_rustvello.client_data_store.RustMemClientDataStore>`
  -
* - {py:obj}`RustSqliteClientDataStore <pynenc_rustvello.client_data_store.RustSqliteClientDataStore>`
  -
* - {py:obj}`RustPostgresClientDataStore <pynenc_rustvello.client_data_store.RustPostgresClientDataStore>`
  -
* - {py:obj}`RustRedisClientDataStore <pynenc_rustvello.client_data_store.RustRedisClientDataStore>`
  -
* - {py:obj}`RustMongoClientDataStore <pynenc_rustvello.client_data_store.RustMongoClientDataStore>`
  -
* - {py:obj}`RustMongo3ClientDataStore <pynenc_rustvello.client_data_store.RustMongo3ClientDataStore>`
  -
````

### API

`````{py:class} _RustClientDataStoreBase(app: pynenc.app.Pynenc, rust_cds: typing.Any)
:canonical: pynenc_rustvello.client_data_store._RustClientDataStoreBase

Bases: {py:obj}`pynenc.client_data_store.base_client_data_store.BaseClientDataStore`

```{autodoc2-docstring} pynenc_rustvello.client_data_store._RustClientDataStoreBase
```

```{rubric} Initialization
```

```{autodoc2-docstring} pynenc_rustvello.client_data_store._RustClientDataStoreBase.__init__
```

````{py:method} _store(key: str, value: str) -> None
:canonical: pynenc_rustvello.client_data_store._RustClientDataStoreBase._store

````

````{py:method} _retrieve(key: str) -> str
:canonical: pynenc_rustvello.client_data_store._RustClientDataStoreBase._retrieve

````

````{py:method} _purge() -> None
:canonical: pynenc_rustvello.client_data_store._RustClientDataStoreBase._purge

````

````{py:property} backend_name
:canonical: pynenc_rustvello.client_data_store._RustClientDataStoreBase.backend_name
:type: str

```{autodoc2-docstring} pynenc_rustvello.client_data_store._RustClientDataStoreBase.backend_name
```

````

`````

```{py:class} RustMemClientDataStore(app: pynenc.app.Pynenc)
:canonical: pynenc_rustvello.client_data_store.RustMemClientDataStore

Bases: {py:obj}`pynenc_rustvello.client_data_store._RustClientDataStoreBase`

```

```{py:class} RustSqliteClientDataStore(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.client_data_store.RustSqliteClientDataStore

Bases: {py:obj}`pynenc_rustvello.client_data_store._RustClientDataStoreBase`

```

```{py:class} RustPostgresClientDataStore(app: pynenc.app.Pynenc, db: typing.Any = None)
:canonical: pynenc_rustvello.client_data_store.RustPostgresClientDataStore

Bases: {py:obj}`pynenc_rustvello.client_data_store._RustClientDataStoreBase`

```

```{py:class} RustRedisClientDataStore(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.client_data_store.RustRedisClientDataStore

Bases: {py:obj}`pynenc_rustvello.client_data_store._RustClientDataStoreBase`

```

```{py:class} RustMongoClientDataStore(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.client_data_store.RustMongoClientDataStore

Bases: {py:obj}`pynenc_rustvello.client_data_store._RustClientDataStoreBase`

```

```{py:class} RustMongo3ClientDataStore(app: pynenc.app.Pynenc, pool: typing.Any = None)
:canonical: pynenc_rustvello.client_data_store.RustMongo3ClientDataStore

Bases: {py:obj}`pynenc_rustvello.client_data_store._RustClientDataStoreBase`

```
