# Runners

`pynenc-rustvello` provides two runner types that execute tasks using the
Rust core. Both share the same `ConfigRustRunner` configuration.

## Runner Types

### RustMemRunner

Single-threaded in-memory runner backed by Rust's `TaskRunner`.

- Rust polls for work, executes the Python task callable, stores results.
- The Python main thread delegates to Rust via `run_one()` per iteration.
- Requires **all** backends to be Rust-backed (`RustMem*`, `RustSqlite*`,
  etc.) — the Rust runner shares the same backend handles as the Python
  app via the `_rust` attribute on each adapter.

```python
from pynenc import PynencBuilder

app = PynencBuilder().app_id("app").rustvello_mem().build()
# RustMemRunner is NOT set automatically — the default runner is used.
# RustMemRunner is primarily for internal use and testing.
```

### RustPythonRunner

Hybrid runner selected via `.rust_runner()`. Uses a Python runner loop
with Rust `run_one()` calls for each invocation.

- Best for **production** workloads.
- Supports signal-aware shutdown (SIGTERM/SIGINT).
- Runs `run_one()` in a background thread to keep the main thread
  responsive to POSIX signals.

```python
app = (
    PynencBuilder()
    .app_id("app")
    .rustvello_redis(redis_url="redis://localhost:6379")
    .rust_runner()    # selects RustPythonRunner
    .build()
)
```

## Backend Compatibility

Both runners require Rust-backed adapters. Attempting to use a Rust
runner with pure-Python backends raises `IncompatibleBackendError`:

```python
from pynenc import PynencBuilder

# This will raise IncompatibleBackendError at runner start:
app = (
    PynencBuilder()
    .app_id("app")
    .mem()            # pure-Python memory backend
    .rust_runner()    # Rust runner can't share state with Python backend
    .build()
)
```

The error message lists the incompatible backend class names so you can
identify which components need to be switched to Rust implementations.

## Configuration

Both runners use `ConfigRustRunner`. See {doc}`configuration` for the
full field reference.

### Performance Tuning

**Worker threads** — `num_workers` controls the tokio runtime thread pool.
`0` (default) uses all available CPU cores. For I/O-bound workloads,
you may benefit from more threads than cores.

```python
app = PynencBuilder().app_id("app").rustvello_redis(
    redis_url="redis://localhost:6379"
).rust_runner().build(config_values={"num_workers": 8})
```

**Poll interval** — `idle_sleep_ms` sets the sleep duration when no work
is available. Lower values reduce latency; higher values reduce CPU usage.

```python
# Low-latency polling (10ms)
app = PynencBuilder().app_id("app").rustvello_mem().build(
    config_values={"idle_sleep_ms": 10}
)
```

### Heartbeats & Recovery

- `heartbeat_interval_seconds` — How often each runner announces it's
  alive. Default: 30s.
- `runner_dead_after_seconds` — If no heartbeat arrives within this
  window, the runner is declared dead. Default: 300s (5 min).
- `recovery_check_interval_seconds` — How often to scan for dead runners
  and reroute their invocations. Default: 60s.
- `max_pending_seconds` — Max time an invocation stays `PENDING`.
  Default: 300s.

### Dev Mode

`dev_mode_force_sync=True` forces synchronous task execution — tasks run
in the calling thread instead of the Rust worker pool. Useful for
debugging with breakpoints:

```python
app = PynencBuilder().app_id("app").rustvello_mem().build(
    config_values={"dev_mode_force_sync": True}
)
```

### Trigger Scheduler

- `enable_scheduler` — Enable/disable the trigger scheduler. Default: `True`.
- `scheduler_interval_seconds` — Poll interval for due triggers. Default: 60s.
