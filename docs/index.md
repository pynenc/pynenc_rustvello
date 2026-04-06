# pynenc-rustvello

**Rust-powered backend plugin for pynenc distributed task orchestration.**

`pynenc-rustvello` brings high-performance Rust implementations of all
pynenc backend interfaces — broker, orchestrator, state backend, trigger
store, client data store, and runner — across **6 storage backends**, with
optional **native Rust orchestration** for maximum throughput.

## Install

```bash
pip install pynenc-rustvello
```

## Quick Start

```python
from pynenc import PynencBuilder

# In-memory Rust backend (fastest for testing)
app = PynencBuilder().app_id("my_app").rustvello_mem().build()

@app.task
def add(x: int, y: int) -> int:
    return x + y

result = add(1, 2).result  # 3
```

```python
# Redis Rust backend (production)
app = (
    PynencBuilder()
    .app_id("my_app")
    .rustvello_redis(redis_url="redis://localhost:6379")
    .rust_runner()
    .build()
)
```

## What's Inside

::::{grid} 1 2 3 3
:gutter: 3

:::{grid-item-card} Installation & Quick Start
:link: installation
:link-type: doc

Install, builder methods, mixing backends, environment variables.
:::

:::{grid-item-card} Configuration Reference
:link: configuration
:link-type: doc

`ConfigRustRunner` fields — worker threads, heartbeats, recovery, scheduler.
:::

:::{grid-item-card} Architecture
:link: architecture
:link-type: doc

Plugin system, PyO3 bridge, native vs delegated orchestration.
:::

:::{grid-item-card} Backend Reference
:link: backends
:link-type: doc

Per-backend details: Mem, SQLite, Redis, Postgres, MongoDB.
:::

:::{grid-item-card} Runner Guide
:link: runners
:link-type: doc

`RustMemRunner` vs `RustPythonRunner`, performance tuning, dev mode.
:::

:::{grid-item-card} API Reference
:link: apidocs/index
:link-type: doc

Auto-generated API documentation.
:::

::::

## Ecosystem

| Package                                                      | Description                      |
| ------------------------------------------------------------ | -------------------------------- |
| [pynenc](https://pynenc.readthedocs.io)                      | Core distributed task framework  |
| [rustvello](https://github.com/pynenc/rustvello)             | Rust engine powering this plugin |
| [pynenc-redis](https://pynenc-redis.readthedocs.io)          | Pure-Python Redis backend        |
| [pynenc-mongo](https://github.com/pynenc/pynenc_mongo)       | Pure-Python MongoDB backend      |
| [pynenc-rabbitmq](https://github.com/pynenc/pynenc_rabbitmq) | Pure-Python RabbitMQ broker      |

```{toctree}
:maxdepth: 2
:hidden:

installation
configuration
architecture
backends
runners
apidocs/index
```
