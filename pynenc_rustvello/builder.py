"""Pynenc plugin registration for Rustvello backends.

This module provides the entry point for pynenc's plugin system.
When rustvello is installed, ``PynencBuilder`` automatically discovers
this plugin and makes the ``.rustvello_*()`` builder methods available.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pynenc.builder import PynencBuilder

# Maps backend name → class names for mixed-mode (Python-level coordination).
_BACKEND_CONFIGS: dict[str, dict[str, str]] = {
    "mem": {
        "orchestrator_cls": "RustMemOrchestrator",
        "broker_cls": "RustMemBroker",
        "state_backend_cls": "RustMemStateBackend",
        "client_data_store_cls": "RustMemClientDataStore",
        "trigger_cls": "RustMemTrigger",
    },
    "sqlite": {
        "orchestrator_cls": "RustSqliteOrchestrator",
        "broker_cls": "RustSqliteBroker",
        "state_backend_cls": "RustSqliteStateBackend",
        "client_data_store_cls": "RustSqliteClientDataStore",
        "trigger_cls": "RustSqliteTrigger",
    },
    "postgres": {
        "orchestrator_cls": "RustPostgresOrchestrator",
        "broker_cls": "RustPostgresBroker",
        "state_backend_cls": "RustPostgresStateBackend",
        "client_data_store_cls": "RustPostgresClientDataStore",
        "trigger_cls": "RustPostgresTrigger",
    },
    "redis": {
        "orchestrator_cls": "RustRedisOrchestrator",
        "broker_cls": "RustRedisBroker",
        "state_backend_cls": "RustRedisStateBackend",
        "client_data_store_cls": "RustRedisClientDataStore",
        "trigger_cls": "RustRedisTrigger",
    },
    "mongo": {
        "orchestrator_cls": "RustMongoOrchestrator",
        "broker_cls": "RustMongoBroker",
        "state_backend_cls": "RustMongoStateBackend",
        "client_data_store_cls": "RustMongoClientDataStore",
        "trigger_cls": "RustMongoTrigger",
    },
    "mongo3": {
        "orchestrator_cls": "RustMongo3Orchestrator",
        "broker_cls": "RustMongo3Broker",
        "state_backend_cls": "RustMongo3StateBackend",
        "client_data_store_cls": "RustMongo3ClientDataStore",
        "trigger_cls": "RustMongo3Trigger",
    },
}

# Native orchestrator class names per backend (single FFI call hot-paths).
_NATIVE_ORCHESTRATOR: dict[str, str] = {
    "mem": "RustMemNativeOrchestrator",
    "sqlite": "RustSqliteNativeOrchestrator",
    "postgres": "RustPostgresNativeOrchestrator",
    "redis": "RustRedisNativeOrchestrator",
    "mongo": "RustMongoNativeOrchestrator",
    "mongo3": "RustMongo3NativeOrchestrator",
}


def _is_all_rust_native(config_values: dict[str, Any]) -> bool:
    """Check whether all configured backend classes are Rust-native.

    Returns True when every relevant ``*_cls`` config value starts with
    ``"Rust"`` — meaning all backends are implemented in Rust and the
    native (single-FFI-call) orchestrator can be used.

    This function is intentionally cheap: it only inspects string config
    values and never imports or instantiates any backend.
    """
    cls_keys = (
        "orchestrator_cls",
        "state_backend_cls",
        "broker_cls",
        "trigger_cls",
        "client_data_store_cls",
    )
    for key in cls_keys:
        val = config_values.get(key, "")
        if not val or not val.startswith("Rust"):
            return False
    return True


def _check_backend_available(backend: str) -> None:
    """Validate that the rustvello native module is importable.

    Raises a clear, actionable ``ImportError`` when the wheel is missing.
    """
    try:
        import rustvello.rustvello  # noqa: F401
    except ImportError:
        raise ImportError(
            f"Backend '{backend}' requires the rustvello package. Install it with: pip install pynenc[{backend}]"
        ) from None


def _import_rustvello_adapters() -> None:
    """Import all rustvello adapter modules so pynenc's get_subclass() can find them."""
    import pynenc_rustvello.broker  # noqa: F401
    import pynenc_rustvello.client_data_store  # noqa: F401
    import pynenc_rustvello.orchestrator  # noqa: F401
    import pynenc_rustvello.orchestrator_backends  # noqa: F401
    import pynenc_rustvello.state_backend  # noqa: F401
    import pynenc_rustvello.trigger  # noqa: F401


def _rustvello_builder_method(
    builder: PynencBuilder, backend: str = "mem", native: bool = True, **kwargs: Any
) -> PynencBuilder:
    """Configure Rust-backed components via py-rustvello.

    :param str backend: Backend type: ``"mem"``, ``"sqlite"``, ``"postgres"``,
        ``"redis"``, ``"mongo"``, ``"mongo3"``, or ``"rabbitmq"``.
    :param bool native: If True (default), use the native orchestrator that
        runs hot-path coordination as single FFI calls.  Set to False to
        use the mixed-mode orchestrator (Python-level coordination).
    :param kwargs: Extra configuration (e.g. ``sqlite_db_path`` for sqlite,
        ``postgres_url`` for postgres, ``redis_url`` for redis,
        ``mongo_url`` / ``mongo_db_name`` for mongo).
    :return: The builder instance for method chaining.
    :raises ImportError: If rustvello native module is not installed.
    :raises ValueError: If *backend* is not recognised.
    """
    # Accept "memory" as an alias for "mem"
    if backend == "memory":
        backend = "mem"

    if backend not in _BACKEND_CONFIGS:
        raise ValueError(
            f"Unknown rustvello backend {backend!r}. Available: {', '.join(sorted(_BACKEND_CONFIGS))}"
        )

    # Pre-flight: ensure the native extension is importable
    _check_backend_available(backend)
    _import_rustvello_adapters()

    builder._config.update(_BACKEND_CONFIGS[backend])
    # Use native orchestrator if requested and available for this backend
    if native and backend in _NATIVE_ORCHESTRATOR:
        builder._config["orchestrator_cls"] = _NATIVE_ORCHESTRATOR[backend]
    builder._using_memory_components = backend == "mem"
    builder._plugin_components.clear()
    builder._plugin_components.add("rustvello")

    # Forward extra kwargs (e.g. sqlite_db_path) to config
    for key, value in kwargs.items():
        builder._config[key] = value

    return builder


def _set_component(
    builder: PynencBuilder,
    component_key: str,
    class_name: str,
    **kwargs: Any,
) -> PynencBuilder:
    """Set a single backend component class for mixing backends.

    Unlike ``_rustvello_builder_method``, this does **not** clear the other
    plugin components — existing per-component selections are preserved.
    """
    _check_backend_available("mem")
    _import_rustvello_adapters()
    builder._config[component_key] = class_name
    for key, value in kwargs.items():
        builder._config[key] = value
    builder._plugin_components.add("rustvello")
    return builder


# ---------------------------------------------------------------------------
# Full-stack named convenience methods
# Names are prefixed with ``rustvello_`` to avoid collision with the
# pynenc-redis, pynenc-mongo, and pynenc-rabbitmq plugin methods
# (``redis()``, ``mongo()``, ``rabbitmq_broker()``).
# ---------------------------------------------------------------------------


def _rustvello_mem_method(builder: PynencBuilder, native: bool = True) -> PynencBuilder:
    """Configure all backends to use the in-memory Rust implementation."""
    return _rustvello_builder_method(builder, backend="mem", native=native)


def _rustvello_sqlite_method(
    builder: PynencBuilder,
    sqlite_db_path: str | None = None,
    native: bool = True,
    **kwargs: Any,
) -> PynencBuilder:
    """Configure all backends to use the SQLite Rust implementation."""
    if sqlite_db_path:
        kwargs["sqlite_db_path"] = sqlite_db_path
    return _rustvello_builder_method(builder, backend="sqlite", native=native, **kwargs)


def _rustvello_redis_method(
    builder: PynencBuilder,
    redis_url: str | None = None,
    native: bool = True,
    **kwargs: Any,
) -> PynencBuilder:
    """Configure all backends to use the Redis Rust implementation."""
    if redis_url:
        kwargs["redis_url"] = redis_url
    return _rustvello_builder_method(builder, backend="redis", native=native, **kwargs)


def _rustvello_postgres_method(
    builder: PynencBuilder,
    postgres_url: str | None = None,
    native: bool = True,
    **kwargs: Any,
) -> PynencBuilder:
    """Configure all backends to use the PostgreSQL Rust implementation."""
    if postgres_url:
        kwargs["postgres_url"] = postgres_url
    return _rustvello_builder_method(
        builder, backend="postgres", native=native, **kwargs
    )


def _rustvello_mongo_method(
    builder: PynencBuilder,
    mongo_url: str | None = None,
    mongo_db_name: str | None = None,
    native: bool = True,
    **kwargs: Any,
) -> PynencBuilder:
    """Configure all backends to use the MongoDB (motor) Rust implementation."""
    if mongo_url:
        kwargs["mongo_url"] = mongo_url
    if mongo_db_name:
        kwargs["mongo_db_name"] = mongo_db_name
    return _rustvello_builder_method(builder, backend="mongo", native=native, **kwargs)


def _rustvello_mongo3_method(
    builder: PynencBuilder,
    mongo_url: str | None = None,
    mongo_db_name: str | None = None,
    native: bool = True,
    **kwargs: Any,
) -> PynencBuilder:
    """Configure all backends to use the MongoDB 3.6+ legacy Rust implementation."""
    if mongo_url:
        kwargs["mongo_url"] = mongo_url
    if mongo_db_name:
        kwargs["mongo_db_name"] = mongo_db_name
    return _rustvello_builder_method(builder, backend="mongo3", native=native, **kwargs)


# ---------------------------------------------------------------------------
# Per-component methods — for mixing rustvello backends with each other or
# with pynenc's pure-Python plugins (e.g. RabbitMQ broker + Redis state).
# ---------------------------------------------------------------------------


def _rustvello_rabbitmq_broker_method(
    builder: PynencBuilder,
    rabbitmq_url: str,
    rabbitmq_prefix: str | None = None,
    **kwargs: Any,
) -> PynencBuilder:
    """Set only the broker to RabbitMQ via rustvello.

    Combine with other ``rustvello_*`` methods to build a mixed-backend app.
    ``rabbitmq_url`` must be a valid AMQP URI (e.g. ``amqp://guest:guest@localhost/``).
    """
    kwargs["rabbitmq_url"] = rabbitmq_url
    if rabbitmq_prefix:
        kwargs["rabbitmq_prefix"] = rabbitmq_prefix
    return _set_component(builder, "broker_cls", "RustRabbitmqBroker", **kwargs)


def _rustvello_redis_broker_method(
    builder: PynencBuilder, redis_url: str | None = None, **kwargs: Any
) -> PynencBuilder:
    """Set only the broker to Redis via rustvello."""
    if redis_url:
        kwargs["redis_url"] = redis_url
    return _set_component(builder, "broker_cls", "RustRedisBroker", **kwargs)


def _rustvello_redis_orchestrator_method(
    builder: PynencBuilder,
    redis_url: str | None = None,
    native: bool = True,
    **kwargs: Any,
) -> PynencBuilder:
    """Set only the orchestrator to Redis via rustvello."""
    if redis_url:
        kwargs["redis_url"] = redis_url
    cls = "RustRedisNativeOrchestrator" if native else "RustRedisOrchestrator"
    return _set_component(builder, "orchestrator_cls", cls, **kwargs)


def _rustvello_redis_state_method(
    builder: PynencBuilder, redis_url: str | None = None, **kwargs: Any
) -> PynencBuilder:
    """Set only the state backend to Redis via rustvello."""
    if redis_url:
        kwargs["redis_url"] = redis_url
    return _set_component(
        builder, "state_backend_cls", "RustRedisStateBackend", **kwargs
    )


def _rustvello_redis_trigger_method(
    builder: PynencBuilder, redis_url: str | None = None, **kwargs: Any
) -> PynencBuilder:
    """Set only the trigger store to Redis via rustvello."""
    if redis_url:
        kwargs["redis_url"] = redis_url
    return _set_component(builder, "trigger_cls", "RustRedisTrigger", **kwargs)


def _rustvello_redis_cds_method(
    builder: PynencBuilder, redis_url: str | None = None, **kwargs: Any
) -> PynencBuilder:
    """Set only the client data store to Redis via rustvello."""
    if redis_url:
        kwargs["redis_url"] = redis_url
    return _set_component(
        builder, "client_data_store_cls", "RustRedisClientDataStore", **kwargs
    )


def _rustvello_postgres_state_method(
    builder: PynencBuilder, postgres_url: str | None = None, **kwargs: Any
) -> PynencBuilder:
    """Set only the state backend to PostgreSQL via rustvello."""
    if postgres_url:
        kwargs["postgres_url"] = postgres_url
    return _set_component(
        builder, "state_backend_cls", "RustPostgresStateBackend", **kwargs
    )


def _rustvello_postgres_orchestrator_method(
    builder: PynencBuilder,
    postgres_url: str | None = None,
    native: bool = True,
    **kwargs: Any,
) -> PynencBuilder:
    """Set only the orchestrator to PostgreSQL via rustvello."""
    if postgres_url:
        kwargs["postgres_url"] = postgres_url
    cls = "RustPostgresNativeOrchestrator" if native else "RustPostgresOrchestrator"
    return _set_component(builder, "orchestrator_cls", cls, **kwargs)


class RustvelloBuilderPlugin:
    """Pynenc plugin that registers all ``.rustvello_*()`` builder methods."""

    @classmethod
    def register_builder_methods(cls, builder_cls: type[PynencBuilder]) -> None:
        # Generic all-in-one method (kept for backward compatibility)
        builder_cls.register_plugin_method("rustvello", _rustvello_builder_method)

        # Full-stack named convenience methods.
        # Prefixed with ``rustvello_`` to avoid clash with pynenc-redis/mongo/rabbitmq
        # plugin methods (``redis()``, ``mongo()``, ``rabbitmq_broker()``).
        builder_cls.register_plugin_method("rustvello_mem", _rustvello_mem_method)
        builder_cls.register_plugin_method("rustvello_sqlite", _rustvello_sqlite_method)
        builder_cls.register_plugin_method("rustvello_redis", _rustvello_redis_method)
        builder_cls.register_plugin_method(
            "rustvello_postgres", _rustvello_postgres_method
        )
        builder_cls.register_plugin_method("rustvello_mongo", _rustvello_mongo_method)
        builder_cls.register_plugin_method("rustvello_mongo3", _rustvello_mongo3_method)

        # Per-component methods for mixing backends.
        # Example: .rustvello_redis().rustvello_rabbitmq_broker(url=...)
        builder_cls.register_plugin_method(
            "rustvello_rabbitmq_broker", _rustvello_rabbitmq_broker_method
        )
        builder_cls.register_plugin_method(
            "rustvello_redis_broker", _rustvello_redis_broker_method
        )
        builder_cls.register_plugin_method(
            "rustvello_redis_orchestrator", _rustvello_redis_orchestrator_method
        )
        builder_cls.register_plugin_method(
            "rustvello_redis_state", _rustvello_redis_state_method
        )
        builder_cls.register_plugin_method(
            "rustvello_redis_trigger", _rustvello_redis_trigger_method
        )
        builder_cls.register_plugin_method(
            "rustvello_redis_cds", _rustvello_redis_cds_method
        )
        builder_cls.register_plugin_method(
            "rustvello_postgres_state", _rustvello_postgres_state_method
        )
        builder_cls.register_plugin_method(
            "rustvello_postgres_orchestrator", _rustvello_postgres_orchestrator_method
        )
