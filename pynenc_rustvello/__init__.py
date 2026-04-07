"""pynenc-rustvello: Rust-powered backend plugin for pynenc.

These classes subclass pynenc's base components and delegate to Rust
implementations via PyO3 bindings. They can be used as drop-in replacements
in pynenc's plugin system.

Usage:
    Configure pynenc to use Rust backends:

        app = Pynenc(config_values={
            "broker_cls": "RustMemBroker",
            "orchestrator_cls": "RustMemOrchestrator",
            "state_backend_cls": "RustMemStateBackend",
        })

    Or import and set directly:

        from pynenc_rustvello import RustMemBroker, RustMemOrchestrator, RustMemStateBackend

Note:
----
    These classes require both `pynenc` and `rustvello` (Rust native module)
    to be installed.

"""

import rustvello as _rv

_MIN_RUSTVELLO = (0, 1, 0)
_ver = tuple(int(x) for x in _rv.__version__.split(".")[:3])
if _ver < _MIN_RUSTVELLO:
    raise ImportError(
        f"pynenc requires rustvello >= {'.'.join(str(v) for v in _MIN_RUSTVELLO)}, got {_rv.__version__}"
    )
del _rv, _ver, _MIN_RUSTVELLO

from pynenc_rustvello.broker import (
    RustMemBroker,
    RustMongo3Broker,
    RustMongoBroker,
    RustPostgresBroker,
    RustRabbitmqBroker,
    RustRedisBroker,
    RustSqliteBroker,
)
from pynenc_rustvello.client_data_store import (
    RustMemClientDataStore,
    RustMongo3ClientDataStore,
    RustMongoClientDataStore,
    RustPostgresClientDataStore,
    RustRedisClientDataStore,
    RustSqliteClientDataStore,
)
from pynenc_rustvello.orchestrator import (
    RustMemNativeOrchestrator,
    RustMemOrchestrator,
    RustMongo3NativeOrchestrator,
    RustMongo3Orchestrator,
    RustMongoNativeOrchestrator,
    RustMongoOrchestrator,
    RustPostgresNativeOrchestrator,
    RustPostgresOrchestrator,
    RustRedisNativeOrchestrator,
    RustRedisOrchestrator,
    RustSqliteNativeOrchestrator,
    RustSqliteOrchestrator,
)
from pynenc_rustvello.state_backend import (
    RustMemStateBackend,
    RustMongo3StateBackend,
    RustMongoStateBackend,
    RustPostgresStateBackend,
    RustRedisStateBackend,
    RustSqliteStateBackend,
)
from pynenc_rustvello.trigger import (
    RustMemTrigger,
    RustMongo3Trigger,
    RustMongoTrigger,
    RustPostgresTrigger,
    RustRedisTrigger,
    RustSqliteTrigger,
)

__all__ = [
    # Mem
    "RustMemBroker",
    "RustMemClientDataStore",
    "RustMemNativeOrchestrator",
    "RustMemOrchestrator",
    "RustMemStateBackend",
    "RustMemTrigger",
    # SQLite
    "RustSqliteBroker",
    "RustSqliteClientDataStore",
    "RustSqliteNativeOrchestrator",
    "RustSqliteOrchestrator",
    "RustSqliteStateBackend",
    "RustSqliteTrigger",
    # PostgreSQL
    "RustPostgresBroker",
    "RustPostgresClientDataStore",
    "RustPostgresNativeOrchestrator",
    "RustPostgresOrchestrator",
    "RustPostgresStateBackend",
    "RustPostgresTrigger",
    # Redis
    "RustRedisBroker",
    "RustRedisClientDataStore",
    "RustRedisNativeOrchestrator",
    "RustRedisOrchestrator",
    "RustRedisStateBackend",
    "RustRedisTrigger",
    # MongoDB
    "RustMongoBroker",
    "RustMongoClientDataStore",
    "RustMongoNativeOrchestrator",
    "RustMongoOrchestrator",
    "RustMongoStateBackend",
    "RustMongoTrigger",
    # MongoDB 3.6+ (legacy)
    "RustMongo3Broker",
    "RustMongo3ClientDataStore",
    "RustMongo3NativeOrchestrator",
    "RustMongo3Orchestrator",
    "RustMongo3StateBackend",
    "RustMongo3Trigger",
    # RabbitMQ
    "RustRabbitmqBroker",
]
