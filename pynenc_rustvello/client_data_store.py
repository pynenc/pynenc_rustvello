"""Pynenc-compatible client data stores backed by Rust backends."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pynenc.client_data_store.base_client_data_store import BaseClientDataStore

if TYPE_CHECKING:
    from pynenc.app import Pynenc


class _RustClientDataStoreBase(BaseClientDataStore):
    """Base client data store backed by any Rust client data store object.

    Delegates SHA-256 content-hash storage and retrieval to the Rust layer.
    Subclasses only override ``__init__`` to create the appropriate Rust inner.
    """

    def __init__(self, app: Pynenc, rust_cds: Any) -> None:
        super().__init__(app)
        self._rust = rust_cds

    def _store(self, key: str, value: str) -> None:
        self._rust.store(key, value)

    def _retrieve(self, key: str) -> str:
        try:
            return self._rust.retrieve(key)
        except (OSError, Exception) as exc:
            # Rust raises StateBackendError for missing keys
            if "key not found" in str(exc):
                raise KeyError(key) from exc
            raise

    def _purge(self) -> None:
        self._rust.purge()

    @property
    def backend_name(self) -> str:
        return self._rust.backend_name()


# ---------------------------------------------------------------------------
# Concrete subclasses per backend
# ---------------------------------------------------------------------------


class RustMemClientDataStore(_RustClientDataStoreBase):
    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustMemClientDataStore as _Inner

        # conf is set by BaseClientDataStore.__init__ via super().__init__
        # so we must call super first, then replace _rust with the configured inner
        super().__init__(app, None)  # type: ignore[arg-type]
        self._rust = _Inner(
            min_size_to_cache=self.conf.min_size_to_cache,
            max_size_to_cache=self.conf.max_size_to_cache,
            local_cache_size=self.conf.local_cache_size,
        )


class RustSqliteClientDataStore(_RustClientDataStoreBase):
    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustSqliteClientDataStore as _Inner

        if db is None:
            from pynenc_rustvello.broker import _get_or_create_sqlite_db

            db = _get_or_create_sqlite_db(app)
        super().__init__(app, _Inner(db))


class RustPostgresClientDataStore(_RustClientDataStoreBase):
    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustPostgresClientDataStore as _Inner

        if db is None:
            from pynenc_rustvello.broker import _get_or_create_postgres_db

            db = _get_or_create_postgres_db(app)
        super().__init__(app, _Inner(db))


class RustRedisClientDataStore(_RustClientDataStoreBase):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustRedisClientDataStore as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_redis_pool

            pool = _get_or_create_redis_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongoClientDataStore(_RustClientDataStoreBase):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongoClientDataStore as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_mongo_pool

            pool = _get_or_create_mongo_pool(app)
        super().__init__(app, _Inner(pool))


class RustMongo3ClientDataStore(_RustClientDataStoreBase):
    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongo3ClientDataStore as _Inner

        if pool is None:
            from pynenc_rustvello.broker import _get_or_create_mongo3_pool

            pool = _get_or_create_mongo3_pool(app)
        super().__init__(app, _Inner(pool))
