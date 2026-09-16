# pynenc-rustvello

[![CombinedTests](https://github.com/pynenc/pynenc_rustvello/actions/workflows/combined_tests.yml/badge.svg)](https://github.com/pynenc/pynenc_rustvello/actions/workflows/combined_tests.yml)
[![Pre-commit](https://github.com/pynenc/pynenc_rustvello/actions/workflows/pre_commit.yml/badge.svg)](https://github.com/pynenc/pynenc_rustvello/actions/workflows/pre_commit.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Rust-powered backend plugin for [pynenc](https://github.com/pynenc/pynenc)
distributed task orchestration — via the
[rustvello](https://github.com/pynenc/rustvello) engine.

`pynenc-rustvello` provides high-performance Rust implementations of all
pynenc storage interfaces (broker, orchestrator, state backend, trigger
store, and client data store) across **6 storage backends**, with optional
**native Rust orchestration** for maximum throughput.

pynenc tasks remain Python code executed by pynenc's own runners
(`ThreadRunner`, `ProcessRunner`, etc.). This plugin replaces only the
storage layer — giving you Rust-level performance for state management,
message queuing, and orchestration coordination without changing how your
tasks run.

For full Rust task execution, use
[rustvello](https://github.com/pynenc/rustvello) directly.

## Components

| Component             | Backends                                                 | Role                                  |
| --------------------- | -------------------------------------------------------- | ------------------------------------- |
| **Broker**            | Mem, SQLite, Redis, Postgres, Mongo, RabbitMQ            | Task queue / message delivery         |
| **Orchestrator**      | Mem, SQLite, Redis, Postgres, Mongo (native + delegated) | Status tracking, blocking, recovery   |
| **State Backend**     | Mem, SQLite, Redis, Postgres, Mongo                      | Invocation state, results, exceptions |
| **Client Data Store** | Mem, SQLite, Redis, Postgres, Mongo                      | Argument caching for large payloads   |
| **Trigger**           | Mem, SQLite, Redis, Postgres, Mongo                      | Event-driven & cron-based scheduling  |

## Installation

```bash
pip install pynenc-rustvello
```

Requires Python ≥ 3.12, [pynenc](https://github.com/pynenc/pynenc) ≥ 0.1.0,
and [rustvello](https://github.com/pynenc/rustvello) ≥ 0.1.0.

## Quick Start

`pynenc-rustvello` registers itself as a pynenc plugin via entry points.
Once installed, Rust backends are available through pynenc's builder:

```python
from pynenc import PynencBuilder

# In-memory Rust backend (fastest for testing)
app = PynencBuilder().app_id("my_app").rustvello_mem().build()

# SQLite Rust backend (persistent, zero-config)
app = PynencBuilder().app_id("my_app").rustvello_sqlite().build()

# Redis Rust backend (production)
app = (
    PynencBuilder()
    .app_id("my_app")
    .rustvello_redis(redis_url="redis://localhost:6379")
    .build()
)

@app.task
def add(x: int, y: int) -> int:
    return x + y

result = add(1, 2).result  # 3
```

### Mixing Backends

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
    .build()
)
```

## Named queues (pynenc ≥ 0.4)

pynenc 0.4 routes every invocation to a logical queue with a priority. The Rust
brokers honour that end to end:

```python
app = (
    PynencBuilder()
    .app_id("calculation")
    .rustvello_mongo3(host="mongo", username="u", password="p", auth_source="admin", db="pynenc")
    .rustvello_rabbitmq_broker(host="rabbitmq-service")     # same keywords as pynenc-mongo / pynenc-rabbitmq
    .custom_config(queues=("default", "hpa", "hyper"))   # declared on the broker
    .build()
)

@app.task(queue="hyper", priority=5.0)
def fast_path() -> None: ...
```

A worker picks its queues through pynenc's runner config, for example
``PYNENC__CONFIGRUNNER__QUEUES=hpa,hyper``. Invocations are routed on
rustvello's Python lane with their task identity, so a runner only ever
retrieves work of its own language and queue; priorities are kept per queue
(RabbitMQ maps them onto message priorities).

Requires a rustvello build that exposes the queue-aware broker bindings
(``route_invocation_to_queue``, ``retrieve_invocation_from_queue``,
``count_invocations_in_queues``), i.e. newer than the 0.5.0 wheel on PyPI.

### Current limitations

- Trigger monitoring evidence (event records, trigger runs, retention) and
  atomic-service execution records are kept in-process (pynenc's in-memory
  implementations) because rustvello exposes no bindings for them yet;
  conditions, claims and heartbeats stay in Rust. Finalized atomic-service
  windows are mirrored into rustvello's timeline for its dashboard.
- ``route_call`` is not composited in native mode: pynenc persists the new
  invocation before routing, which rustvello's durable-submission rule treats
  as a legacy id. Status, result, exception, retry and reroute stay single
  FFI calls; retry and reroute register the task's routing in the Rust catalog
  first so they re-queue on the right queue.
- ``parent_event_id`` lookups use an in-process index (rustvello's invocation
  row has no such field yet).

## Architecture

`pynenc-rustvello` is a **storage plugin** — it replaces pynenc's storage
layer with Rust-backed implementations while keeping task execution in Python.

```
┌────────────────────────────────────────────────┐
│                   pynenc app                   │
│                                                │
│  Tasks (Python)  ←→  Runner (Python)           │
│       │                    │                   │
│       ▼                    ▼                   │
│  ┌─────────────────────────────────────────┐   │
│  │     pynenc-rustvello (storage layer)    │   │
│  │  Broker · Orchestrator · State Backend  │   │
│  │  Trigger · Client Data Store            │   │
│  │         (all backed by Rust FFI)        │   │
│  └─────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

For users who want full Rust task execution (not just storage), use
[rustvello](https://github.com/pynenc/rustvello) directly.

## Documentation

Full documentation: [pynenc-rustvello.readthedocs.io](https://pynenc-rustvello.readthedocs.io)

## Ecosystem

| Package                                                      | Description                      |
| ------------------------------------------------------------ | -------------------------------- |
| [pynenc](https://github.com/pynenc/pynenc)                   | Core distributed task framework  |
| [rustvello](https://github.com/pynenc/rustvello)             | Rust engine powering this plugin |
| [pynenc-redis](https://github.com/pynenc/pynenc_redis)       | Pure-Python Redis backend        |
| [pynenc-mongo](https://github.com/pynenc/pynenc_mongo)       | Pure-Python MongoDB backend      |
| [pynenc-rabbitmq](https://github.com/pynenc/pynenc_rabbitmq) | Pure-Python RabbitMQ broker      |

## Development

```bash
# Clone the repository
git clone https://github.com/pynenc/pynenc_rustvello.git
cd pynenc_rustvello

# Install in dev mode
uv sync --all-extras

# Run tests
uv run python -m pytest tests/unit/ -q

# Lint
uv run ruff check pynenc_rustvello/ tests/
uv run ruff format --check pynenc_rustvello/ tests/
```

## License

MIT
