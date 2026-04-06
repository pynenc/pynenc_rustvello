# Architecture

## Plugin System

`pynenc-rustvello` is a pynenc plugin discovered via Python entry points.
When the package is installed, pynenc's builder automatically gains
Rust-backed builder methods:

```
pip install pynenc-rustvello
        ↓ entry points
pynenc discovers RustvelloBuilderPlugin → registers builder methods
        ↓
PynencBuilder().rustvello_redis(...)  → sets Rust-backed component classes
        ↓
app.build() → instantiates Rust components (via PyO3)
```

The plugin registers a `RustvelloBuilderPlugin` class that provides:

- **6 full-stack methods** (`.rustvello_mem()`, `.rustvello_sqlite()`, etc.)
- **8 per-component methods** (`.rustvello_redis_broker()`, etc.)
- **1 runner method** (`.rust_runner()`)

## PyO3 Bridge

The `rustvello` wheel (built with [maturin](https://github.com/PyO3/maturin))
exposes Rust structs as Python classes via [PyO3](https://pyo3.rs).

`pynenc-rustvello` adapters wrap these PyO3 classes to satisfy pynenc's
abstract base class contracts:

```
                  pynenc (Python)
                       │
               abstract base classes
          (BaseBroker, BaseOrchestrator, ...)
                       │
              pynenc-rustvello (Python)
                       │
              adapter classes bridge
         (RustRedisBroker, RustMemOrchestrator, ...)
                       │
                  rustvello (PyO3)
                       │
                  Rust core logic
         (rustvello-core, rustvello-mem, rustvello-redis, ...)
```

### Design Principles

- **Adapters are stateless bridges** — all state lives in the Rust core.
  The Python adapter layer performs type conversion and error translation
  only.
- **No parallel data structures** — adapters never maintain Python-side
  dicts or lists that duplicate what Rust stores.
- **Missing functionality goes into Rust first** — if an adapter needs
  something the core doesn't expose, the Rust core is extended before
  the Python side works around it.

## Native vs Delegated Orchestration

Each backend offers two orchestrator modes:

| Mode                 | Class Pattern             | How It Works                                                                                                                               |
| -------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Native** (default) | `Rust*NativeOrchestrator` | Hot-path orchestration (routing, blocking control, recovery) is executed as a single FFI call into the Rust core. Minimal Python overhead. |
| **Delegated**        | `Rust*Orchestrator`       | Rust handles storage only. Orchestration logic (status transitions, blocking decisions) runs in Python via pynenc's `BaseOrchestrator`.    |

### When to Use Each Mode

- **Native** (`native=True`, the default): Best for production. Maximum
  throughput because all coordination happens in compiled Rust code.
- **Delegated** (`native=False`): Useful for debugging or when you need
  to customize orchestration behaviour at the Python level.

```python
# Native orchestration (default)
app = PynencBuilder().app_id("app").rustvello_redis(native=True).build()

# Delegated orchestration
app = PynencBuilder().app_id("app").rustvello_redis(native=False).build()
```

### Auto-Detection

The builder automatically selects the native orchestrator when **all**
configured `*_cls` values start with `Rust`. If any component is a
pure-Python backend, delegated mode is used to ensure compatibility.

## Runner Architecture

Two runner types are available:

| Runner             | Use Case                 | How It Works                                                                   |
| ------------------ | ------------------------ | ------------------------------------------------------------------------------ |
| `RustMemRunner`    | Pure-Rust task execution | Rust polls, executes, and stores — no Python in the hot path. Single-threaded. |
| `RustPythonRunner` | Hybrid execution         | Python loop + Rust `run_one()` per invocation. Supports any Python task.       |

Both runners share a `RustTaskRunnerBuilder` that wires the Rust backends
from the app's existing component instances — the Python adapters expose
their inner `_rust` handle so the runner can attach to the same backend
without creating duplicate connections.

See {doc}`runners` for detailed runner documentation.

## Cross-System Hash Compatibility

`compute_args_id` produces **identical hashes** in both Python and Rust.
The wire format is `JSON(key)=JSON(value);` with sorted keys, ensuring
that invocation deduplication works correctly regardless of which language
created the invocation.
