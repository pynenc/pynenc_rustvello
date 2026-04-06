# Installation

## Requirements

- Python ≥ 3.12
- [pynenc](https://github.com/pynenc/pynenc) ≥ 0.1.0
- [rustvello](https://github.com/pynenc/rustvello) ≥ 0.1.0

## Install

```bash
pip install pynenc-rustvello
```

On most platforms a pre-built `rustvello` wheel is available. For source
builds a Rust toolchain (via [rustup](https://rustup.rs)) is required.

## Quick Start

```python
from pynenc import PynencBuilder

# All-in-memory Rust backend (fastest for testing)
app = PynencBuilder().app_id("my_app").rustvello_mem().build()

# SQLite Rust backend (persistent, zero-config)
app = PynencBuilder().app_id("my_app").rustvello_sqlite().build()

# Redis Rust backend (production)
app = (
    PynencBuilder()
    .app_id("my_app")
    .rustvello_redis(redis_url="redis://localhost:6379")
    .rust_runner()
    .build()
)
```

## Builder Methods

### Full-Stack Methods

Set **all** backend components to the same storage engine in one call.

| Method                                                      | Parameters                                                                    | Description                                |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------ |
| `.rustvello(backend, native, **kw)`                         | `backend`: str, `native`: bool = True                                         | Generic entry point                        |
| `.rustvello_mem(native)`                                    | `native`: bool = True                                                         | All components in-memory                   |
| `.rustvello_sqlite(sqlite_db_path, native, **kw)`           | `sqlite_db_path`: str \| None, `native`: bool = True                          | All components on SQLite                   |
| `.rustvello_redis(redis_url, native, **kw)`                 | `redis_url`: str \| None, `native`: bool = True                               | All components on Redis                    |
| `.rustvello_postgres(postgres_url, native, **kw)`           | `postgres_url`: str \| None, `native`: bool = True                            | All components on Postgres                 |
| `.rustvello_mongo(mongo_url, mongo_db_name, native, **kw)`  | `mongo_url`: str \| None, `mongo_db_name`: str \| None, `native`: bool = True | All on MongoDB                             |
| `.rustvello_mongo3(mongo_url, mongo_db_name, native, **kw)` | same as `.rustvello_mongo`                                                    | All on MongoDB 3.6+ legacy                 |
| `.rust_runner()`                                            | —                                                                             | Switch runner to Rust (`RustPythonRunner`) |

The `native` parameter controls orchestrator mode. See
{doc}`architecture` for details on native vs delegated orchestration.

### Per-Component Methods

Set individual backend components for **mixing backends** across storage
engines. Existing per-component selections are preserved.

| Method                                                            | Description                    |
| ----------------------------------------------------------------- | ------------------------------ |
| `.rustvello_redis_broker(redis_url, **kw)`                        | Redis-backed broker only       |
| `.rustvello_redis_orchestrator(redis_url, native, **kw)`          | Redis-backed orchestrator      |
| `.rustvello_redis_state(redis_url, **kw)`                         | Redis-backed state backend     |
| `.rustvello_redis_trigger(redis_url, **kw)`                       | Redis-backed trigger           |
| `.rustvello_redis_cds(redis_url, **kw)`                           | Redis-backed client data store |
| `.rustvello_postgres_state(postgres_url, **kw)`                   | Postgres-backed state backend  |
| `.rustvello_postgres_orchestrator(postgres_url, native, **kw)`    | Postgres-backed orchestrator   |
| `.rustvello_rabbitmq_broker(rabbitmq_url, rabbitmq_prefix, **kw)` | RabbitMQ-backed broker         |

## Mixing Backends

Combine different storage backends per component:

```python
app = (
    PynencBuilder()
    .app_id("my_app")
    .rustvello_redis_broker(redis_url="redis://localhost:6379")
    .rustvello_postgres_state(postgres_url="postgresql://localhost/mydb")
    .rustvello_postgres_orchestrator(postgres_url="postgresql://localhost/mydb")
    .rustvello_redis_trigger(redis_url="redis://localhost:6379")
    .rustvello_redis_cds(redis_url="redis://localhost:6379")
    .rust_runner()
    .build()
)
```

:::{note}
When mixing backends, the native orchestrator auto-detection still works.
If **all** configured `*_cls` values start with `Rust`, the native
orchestrator is selected automatically.
:::

## Environment Variables

All pynenc settings can be overridden with environment variables using
the `PYNENC_{SETTING_UPPERCASE}` pattern:

```bash
export PYNENC_REDIS_URL="redis://localhost:6379"
export PYNENC_POSTGRES_URL="postgresql://localhost/mydb"
export PYNENC_NUM_WORKERS=4
export PYNENC_IDLE_SLEEP_MS=50
```

## Docker Compose Example

A multi-service setup with Redis broker and Postgres storage:

```yaml
services:
  app:
    build: .
    environment:
      - PYNENC_REDIS_URL=redis://redis:6379
      - PYNENC_POSTGRES_URL=postgresql://postgres:5432/pynenc
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: pynenc
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
```
