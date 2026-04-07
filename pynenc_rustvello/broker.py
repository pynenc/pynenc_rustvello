"""Pynenc-compatible brokers backed by Rust backends."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pynenc.broker.base_broker import BaseBroker

if TYPE_CHECKING:
    from pynenc.app import Pynenc
    from pynenc.identifiers.invocation_id import InvocationId
    from pynenc.identifiers.task_id import TaskId


def _get_or_create_sqlite_db(app: Any) -> Any:
    """Get or create a shared RustSqliteDatabase from pynenc config.

    Caches the connection on the app instance so all Rust SQLite components
    share the same underlying connection.
    """
    cached = getattr(app, "_rustvello_sqlite_db", None)
    if cached is not None:
        return cached
    from rustvello import RustSqliteDatabase

    # sqlite_db_path lives in config_values (builder dict) and is also
    # available through ConfigSQLite, but not on the main ConfigPynenc.
    db_path = (app.config_values or {}).get("sqlite_db_path", "")
    if not db_path:
        from pynenc.conf.config_sqlite import ConfigSQLite

        conf = ConfigSQLite(
            config_values=app.config_values,
            config_filepath=app.config_filepath,
        )
        db_path = conf.sqlite_db_path
    if not db_path:
        raise ValueError(
            "sqlite_db_path must be configured. Use PynencBuilder().rustvello(backend='sqlite', sqlite_db_path='...')"
        )
    db = RustSqliteDatabase(str(db_path), app.app_id)
    app._rustvello_sqlite_db = db
    return db


def _get_or_create_postgres_db(app: Any) -> Any:
    """Get or create a shared RustPostgresDatabase from pynenc config.

    Caches the connection on the app instance so all Rust Postgres components
    share the same underlying connection.
    """
    cached = getattr(app, "_rustvello_postgres_db", None)
    if cached is not None:
        return cached
    from rustvello import RustPostgresDatabase

    conn_str = (app.config_values or {}).get("postgres_url", "")
    if not conn_str:
        raise ValueError(
            "postgres_url must be configured. Use PynencBuilder().rustvello(backend='postgres', postgres_url='...')"
        )
    db = RustPostgresDatabase(str(conn_str), app.app_id)
    app._rustvello_postgres_db = db
    return db


def _get_or_create_redis_pool(app: Any) -> Any:
    """Get or create a shared RustRedisPool from pynenc config.

    Caches the connection on the app instance so all Rust Redis components
    share the same underlying pool.
    """
    cached = getattr(app, "_rustvello_redis_pool", None)
    if cached is not None:
        return cached
    from rustvello import RustRedisPool

    uri = (app.config_values or {}).get("redis_url", "")
    if not uri:
        raise ValueError(
            "redis_url must be configured. Use PynencBuilder().rustvello(backend='redis', redis_url='...')"
        )
    pool = RustRedisPool(str(uri), app.app_id)
    app._rustvello_redis_pool = pool
    return pool


def _get_or_create_mongo_pool(app: Any) -> Any:
    """Get or create a shared RustMongoPool from pynenc config.

    Caches the connection on the app instance so all Rust Mongo components
    share the same underlying pool.
    """
    cached = getattr(app, "_rustvello_mongo_pool", None)
    if cached is not None:
        return cached
    from rustvello import RustMongoPool

    uri = (app.config_values or {}).get("mongo_url", "")
    if not uri:
        raise ValueError(
            "mongo_url must be configured. Use PynencBuilder().rustvello(backend='mongo', mongo_url='...')"
        )
    db_name = (app.config_values or {}).get("mongo_db_name", "rustvello")
    pool = RustMongoPool(str(uri), str(db_name), app.app_id)
    app._rustvello_mongo_pool = pool
    return pool


class _RustvelloBroker(BaseBroker):
    """Base broker that delegates to a Rust PyO3 broker object."""

    def __init__(self, app: Pynenc, rust_broker: Any) -> None:
        super().__init__(app)
        self._rust = rust_broker

    def route_invocation(self, invocation_id: InvocationId) -> None:
        self._rust.route_invocation(str(invocation_id))

    def route_invocations(self, invocation_ids: list[InvocationId]) -> None:
        self._rust.route_invocations([str(i) for i in invocation_ids])

    def retrieve_invocation(self) -> InvocationId | None:
        from pynenc.identifiers.invocation_id import InvocationId

        result = self._rust.retrieve_invocation()
        if result is None:
            return None
        return InvocationId(result)

    def count_invocations(self) -> int:
        return self._rust.count_invocations()

    def purge(self) -> None:
        self._rust.purge()

    # ── Per-task / language extensions (Rust-only, not in pynenc ABC) ──

    def route_invocation_for_task(
        self, invocation_id: InvocationId, task_id: TaskId
    ) -> None:
        self._rust.route_invocation_for_task(
            str(invocation_id), str(task_id.module), str(task_id.func_name)
        )

    def retrieve_invocation_for_task(self, task_id: TaskId) -> InvocationId | None:
        from pynenc.identifiers.invocation_id import InvocationId

        result = self._rust.retrieve_invocation_for_task(
            str(task_id.module), str(task_id.func_name)
        )
        if result is None:
            return None
        return InvocationId(result)

    def retrieve_invocation_for_language(self, language: str) -> InvocationId | None:
        from pynenc.identifiers.invocation_id import InvocationId

        result = self._rust.retrieve_invocation_for_language(language)
        if result is None:
            return None
        return InvocationId(result)

    def count_invocations_for_task(self, task_id: TaskId) -> int:
        return self._rust.count_invocations_for_task(
            str(task_id.module), str(task_id.func_name)
        )

    def purge_task(self, task_id: TaskId) -> None:
        self._rust.purge_task(str(task_id.module), str(task_id.func_name))


class RustMemBroker(_RustvelloBroker):
    """In-memory broker backed by Rust's ``MemBroker`` (VecDeque FIFO)."""

    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustMemBroker as _RustMemBroker

        super().__init__(app, _RustMemBroker())


class RustSqliteBroker(_RustvelloBroker):
    """SQLite-backed broker for persistent single-node deployments."""

    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustSqliteBroker as _RustSqliteBroker

        if db is None:
            db = _get_or_create_sqlite_db(app)
        super().__init__(app, _RustSqliteBroker(db))


class RustPostgresBroker(_RustvelloBroker):
    """PostgreSQL-backed broker for distributed deployments."""

    def __init__(self, app: Pynenc, db: Any = None) -> None:
        from rustvello import RustPostgresBroker as _RustPostgresBroker

        if db is None:
            db = _get_or_create_postgres_db(app)
        super().__init__(app, _RustPostgresBroker(db))


class RustRedisBroker(_RustvelloBroker):
    """Redis-backed broker for high-throughput distributed deployments."""

    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustRedisBroker as _RustRedisBroker

        if pool is None:
            pool = _get_or_create_redis_pool(app)
        super().__init__(app, _RustRedisBroker(pool))


class RustMongoBroker(_RustvelloBroker):
    """MongoDB-backed broker for distributed deployments."""

    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongoBroker as _RustMongoBroker

        if pool is None:
            pool = _get_or_create_mongo_pool(app)
        super().__init__(app, _RustMongoBroker(pool))


def _get_or_create_mongo3_pool(app: Any) -> Any:
    """Get or create a shared RustMongo3Pool from pynenc config.

    Caches the connection on the app instance so all Rust Mongo3 components
    share the same underlying pool.
    """
    cached = getattr(app, "_rustvello_mongo3_pool", None)
    if cached is not None:
        return cached
    from rustvello import RustMongo3Pool

    uri = (app.config_values or {}).get("mongo_url", "")
    if not uri:
        raise ValueError(
            "mongo_url must be configured. Use PynencBuilder().rustvello(backend='mongo3', mongo_url='...')"
        )
    db_name = (app.config_values or {}).get("mongo_db_name", "rustvello")
    pool = RustMongo3Pool(str(uri), str(db_name), app.app_id)
    app._rustvello_mongo3_pool = pool
    return pool


class RustMongo3Broker(_RustvelloBroker):
    """MongoDB 3.6+ backed broker using legacy driver."""

    def __init__(self, app: Pynenc, pool: Any = None) -> None:
        from rustvello import RustMongo3Broker as _RustMongo3Broker

        if pool is None:
            pool = _get_or_create_mongo3_pool(app)
        super().__init__(app, _RustMongo3Broker(pool))


class RustRabbitmqBroker(_RustvelloBroker):
    """RabbitMQ broker for durable distributed task queuing.

    Reads connection settings from ``app.config_values``:

    * ``rabbitmq_url`` — AMQP connection URI (required)
    * ``rabbitmq_prefix`` — queue name prefix; defaults to ``app.app_id``
    """

    def __init__(self, app: Pynenc) -> None:
        from rustvello import RustRabbitmqBroker as _RustRabbitmqBroker

        config = app.config_values or {}
        uri = config.get("rabbitmq_url", "")
        if not uri:
            raise ValueError(
                "rabbitmq_url must be set in config or the RUSTVELLO_RABBITMQ_URL "
                "environment variable to use RustRabbitmqBroker."
            )
        prefix = config.get("rabbitmq_prefix", app.app_id)
        super().__init__(app, _RustRabbitmqBroker(str(uri), str(prefix)))
