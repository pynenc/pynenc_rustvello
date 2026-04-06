# Backend Reference

`pynenc-rustvello` supports 6 storage backends. Each backend provides
implementations of all 5 pynenc component interfaces (broker, orchestrator,
state backend, client data store, trigger) plus optional native
orchestration.

## Memory (Mem)

In-memory storage — no external dependencies, zero config, fastest for
unit tests and development.

**Builder:**
```python
app = PynencBuilder().app_id("app").rustvello_mem().build()
```

**Classes:**

| Component | Class |
| --------- | ----- |
| Broker | `RustMemBroker` |
| Orchestrator | `RustMemOrchestrator` / `RustMemNativeOrchestrator` |
| State Backend | `RustMemStateBackend` |
| Client Data Store | `RustMemClientDataStore` |
| Trigger | `RustMemTrigger` |

**Limitations:**
- Data is lost when the process exits.
- Single-process only (no cross-process sharing).

---

## SQLite

File-based persistent storage. Zero external services required.

**Builder:**
```python
app = PynencBuilder().app_id("app").rustvello_sqlite(sqlite_db_path="/tmp/pynenc.db").build()
```

**Classes:**

| Component | Class |
| --------- | ----- |
| Broker | `RustSqliteBroker` |
| Orchestrator | `RustSqliteOrchestrator` / `RustSqliteNativeOrchestrator` |
| State Backend | `RustSqliteStateBackend` |
| Client Data Store | `RustSqliteClientDataStore` |
| Trigger | `RustSqliteTrigger` |

**Connection:** `sqlite_db_path` — path to the SQLite database file.
If omitted, a temporary in-memory SQLite database is used.

---

## Redis

Production-ready, high-throughput backend using Redis as the storage/queue engine.

**Builder:**
```python
app = (
    PynencBuilder()
    .app_id("app")
    .rustvello_redis(redis_url="redis://localhost:6379")
    .rust_runner()
    .build()
)
```

**Classes:**

| Component | Class |
| --------- | ----- |
| Broker | `RustRedisBroker` |
| Orchestrator | `RustRedisOrchestrator` / `RustRedisNativeOrchestrator` |
| State Backend | `RustRedisStateBackend` |
| Client Data Store | `RustRedisClientDataStore` |
| Trigger | `RustRedisTrigger` |

**Connection:** `redis_url` — standard Redis URL (e.g. `redis://localhost:6379/0`).

---

## PostgreSQL

Relational storage with ACID guarantees. Good for workloads that need
strong consistency and transactional safety.

**Builder:**
```python
app = (
    PynencBuilder()
    .app_id("app")
    .rustvello_postgres(postgres_url="postgresql://user:pass@localhost/pynenc")
    .rust_runner()
    .build()
)
```

**Classes:**

| Component | Class |
| --------- | ----- |
| Broker | `RustPostgresBroker` |
| Orchestrator | `RustPostgresOrchestrator` / `RustPostgresNativeOrchestrator` |
| State Backend | `RustPostgresStateBackend` |
| Client Data Store | `RustPostgresClientDataStore` |
| Trigger | `RustPostgresTrigger` |

**Connection:** `postgres_url` — standard PostgreSQL connection string.

---

## MongoDB

Document-oriented storage. Two variants are available:

### MongoDB (modern)

For MongoDB 4.0+ with modern driver features.

**Builder:**
```python
app = (
    PynencBuilder()
    .app_id("app")
    .rustvello_mongo(mongo_url="mongodb://localhost:27017", mongo_db_name="pynenc")
    .rust_runner()
    .build()
)
```

**Classes:**

| Component | Class |
| --------- | ----- |
| Broker | `RustMongoBroker` |
| Orchestrator | `RustMongoOrchestrator` / `RustMongoNativeOrchestrator` |
| State Backend | `RustMongoStateBackend` |
| Client Data Store | `RustMongoClientDataStore` |
| Trigger | `RustMongoTrigger` |

### MongoDB 3.6+ (legacy)

For MongoDB 3.6+ deployments using legacy wire protocol features.

**Builder:**
```python
app = (
    PynencBuilder()
    .app_id("app")
    .rustvello_mongo3(mongo_url="mongodb://localhost:27017", mongo_db_name="pynenc")
    .build()
)
```

**Connection:** `mongo_url` + `mongo_db_name`.

---

## RabbitMQ (Broker Only)

RabbitMQ is available **only as a broker** — it does not provide
orchestrator, state backend, trigger, or client data store implementations.
Combine it with another backend for the remaining components.

**Builder:**
```python
app = (
    PynencBuilder()
    .app_id("app")
    .rustvello_redis()               # all components on Redis
    .rustvello_rabbitmq_broker(       # override broker to RabbitMQ
        rabbitmq_url="amqp://guest:guest@localhost/",
        rabbitmq_prefix="my_app",
    )
    .rust_runner()
    .build()
)
```

**Class:** `RustRabbitmqBroker`

**Connection:** `rabbitmq_url` (AMQP URI) + optional `rabbitmq_prefix`.
