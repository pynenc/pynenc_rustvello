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
