"""Pynenc-compatible brokers backed by Rust backends."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from pynenc.broker.base_broker import BaseBroker
from pynenc.conf.config_broker import DEFAULT_PRIORITY, DEFAULT_QUEUE, validate_priority

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


# All pynenc tasks are Python tasks: rows are routed and retrieved on rustvello's Python lane.
PYTHON_LANE = "python"


def _untyped_task_id() -> TaskId:
    """Task identity for ids routed through the bare BaseBroker API, which carries no task.

    Keeping such rows on the Python lane means language-aware retrieval still finds them.
    """
    from pynenc.identifiers.task_id import TaskId as _TaskId

    return _TaskId(module="pynenc_rustvello", func_name="untyped_invocation")


class _RustvelloBroker(BaseBroker):
    """Base broker that delegates to a Rust PyO3 broker object.

    pynenc 0.4 routes every invocation to a logical queue with a priority. The
    orchestrator adapter passes the task identity along (see
    ``_RustvelloOrchestrator.route_invocation``) so rows land on the Python
    lane of that queue; the bare ``BaseBroker`` API resolves the task from the
    state backend and falls back to a plugin-owned sentinel task.
    """

    def __init__(self, app: Pynenc, rust_broker: Any) -> None:
        super().__init__(app)
        self._rust = rust_broker

    # ── pynenc 0.4 contract ────────────────────────────────────────────

    def _route_invocation(
        self, invocation_id: InvocationId, queue_name: str, priority: float
    ) -> None:
        task_id = self._resolve_task_id(invocation_id)
        self._rust.route_invocation_to_queue(
            str(invocation_id),
            queue_name,
            priority,
            task_module=str(task_id.module),
            task_name=str(task_id.func_name),
            language=PYTHON_LANE,
        )

    def _route_invocations(
        self,
        invocation_ids: Sequence[InvocationId],
        queue_name: str,
        priority: float,
    ) -> None:
        by_task: dict[TaskId, list[str]] = {}
        for invocation_id in invocation_ids:
            by_task.setdefault(self._resolve_task_id(invocation_id), []).append(
                str(invocation_id)
            )
        for task_id, ids in by_task.items():
            self._rust.route_invocations_to_queue(
                ids,
                queue_name,
                priority,
                task_module=str(task_id.module),
                task_name=str(task_id.func_name),
                language=PYTHON_LANE,
            )

    def retrieve_invocation(self, queue_name: str | None = None) -> InvocationId | None:
        from pynenc.identifiers.invocation_id import InvocationId

        queue = self.conf.queues[0] if queue_name is None else queue_name
        self._validate_queue_names((queue,))
        result = self._rust.retrieve_invocation_from_queue(queue, language=PYTHON_LANE)
        if result is None:
            return None
        return InvocationId(result)

    def count_invocations(self, queue_names: Sequence[str] | None = None) -> int:
        queues = tuple(self.conf.queues if queue_names is None else queue_names)
        self._validate_queue_names(queues)
        return self._rust.count_invocations_in_queues(list(queues))

    def purge(self) -> None:
        self._rust.purge()

    # ── Task-aware routing (used by the orchestrator adapter) ──────────

    def route_invocation_for_task(
        self,
        invocation_id: InvocationId,
        task_id: TaskId,
        queue_name: str = DEFAULT_QUEUE,
        priority: float = DEFAULT_PRIORITY,
    ) -> None:
        """Route with a known task identity, skipping the state-backend lookup."""
        self._validate_queue_names((queue_name,))
        validate_priority(priority, label="Broker priority")
        self._rust.route_invocation_to_queue(
            str(invocation_id),
            queue_name,
            priority,
            task_module=str(task_id.module),
            task_name=str(task_id.func_name),
            language=PYTHON_LANE,
        )

    def route_invocations_for_task(
        self,
        invocation_ids: Sequence[InvocationId],
        task_id: TaskId,
        queue_name: str = DEFAULT_QUEUE,
        priority: float = DEFAULT_PRIORITY,
    ) -> None:
        """Batch variant of :meth:`route_invocation_for_task`."""
        self._validate_queue_names((queue_name,))
        validate_priority(priority, label="Broker priority")
        self._rust.route_invocations_to_queue(
            [str(i) for i in invocation_ids],
            queue_name,
            priority,
            task_module=str(task_id.module),
            task_name=str(task_id.func_name),
            language=PYTHON_LANE,
        )

    def retrieve_invocation_for_task(
        self, task_id: TaskId, queue_name: str = DEFAULT_QUEUE
    ) -> InvocationId | None:
        from pynenc.identifiers.invocation_id import InvocationId

        result = self._rust.retrieve_invocation_from_queue(
            queue_name,
            task_module=str(task_id.module),
            task_name=str(task_id.func_name),
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

    def count_invocations_for_task(
        self, task_id: TaskId, queue_names: Sequence[str] | None = None
    ) -> int:
        queues = list(self.conf.queues if queue_names is None else queue_names)
        return self._rust.count_invocations_in_queues(
            queues,
            task_module=str(task_id.module),
            task_name=str(task_id.func_name),
        )

    def purge_task(self, task_id: TaskId) -> None:
        self._rust.purge_task(str(task_id.module), str(task_id.func_name))

    # ── helpers ────────────────────────────────────────────────────────

    def _resolve_task_id(self, invocation_id: InvocationId) -> TaskId:
        try:
            invocation = self.app.state_backend.get_invocation(invocation_id)
        except Exception:  # noqa: BLE001 - ids routed through the bare API may be unknown to the state backend
            invocation = None
        if invocation is None:
            return _untyped_task_id()
        return invocation.task.task_id


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
