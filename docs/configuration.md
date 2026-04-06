# Configuration

## ConfigRustRunner

`ConfigRustRunner` extends pynenc's `ConfigRunner` with Rust-specific
fields for the Rust task runner. All fields can be set via
`config_values` or environment variables.

### Fields

| Setting                           | Type   | Default           | Description                                                                                                                       |
| --------------------------------- | ------ | ----------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `num_workers`                     | `int`  | `0` (= cpu_count) | Number of worker threads in the Rust runtime. `0` uses all available CPU cores.                                                   |
| `idle_sleep_ms`                   | `int`  | `100`             | Milliseconds to sleep between poll cycles when no work is available. Lower values reduce latency at the cost of CPU usage.        |
| `heartbeat_interval_seconds`      | `int`  | `30`              | How often each runner sends a heartbeat to signal it is alive.                                                                    |
| `runner_dead_after_seconds`       | `int`  | `300`             | A runner is considered dead if no heartbeat is received within this window. Dead runners' invocations are recovered and rerouted. |
| `recovery_check_interval_seconds` | `int`  | `60`              | How often the recovery scan checks for dead runners.                                                                              |
| `max_pending_seconds`             | `int`  | `300`             | Maximum time an invocation can stay in `PENDING` status before being recovered.                                                   |
| `dev_mode_force_sync`             | `bool` | `False`           | When `True`, forces synchronous execution — useful for debugging and testing.                                                     |
| `enable_scheduler`                | `bool` | `True`            | Whether the trigger scheduler is active.                                                                                          |
| `scheduler_interval_seconds`      | `int`  | `60`              | How often the trigger scheduler polls for due triggers.                                                                           |

### Inherited Fields

`ConfigRustRunner` also inherits all fields from pynenc's `ConfigRunner`:

| Setting                                  | Type    | Default | Description                                       |
| ---------------------------------------- | ------- | ------- | ------------------------------------------------- |
| `runner_loop_sleep_time_sec`             | `float` | `0.5`   | Sleep between Python-side runner loop iterations. |
| `invocation_wait_results_sleep_time_sec` | `float` | `0.1`   | Sleep while polling for invocation results.       |

### Example

```python
from pynenc import PynencBuilder

app = (
    PynencBuilder()
    .app_id("my_app")
    .rustvello_redis(redis_url="redis://localhost:6379")
    .rust_runner()
    .build()
)

# Access the runner config
print(app.runner.conf.num_workers)          # 0 (auto)
print(app.runner.conf.idle_sleep_ms)        # 100
print(app.runner.conf.heartbeat_interval_seconds)  # 30
```

### Override via config_values

```python
app = (
    PynencBuilder()
    .app_id("my_app")
    .rustvello_mem()
    .rust_runner()
    .build(config_values={
        "num_workers": 4,
        "idle_sleep_ms": 50,
        "dev_mode_force_sync": True,
    })
)
```

### Override via environment variables

```bash
export PYNENC_NUM_WORKERS=4
export PYNENC_IDLE_SLEEP_MS=50
export PYNENC_DEV_MODE_FORCE_SYNC=true
```

## Backend Connection Settings

Backend-specific connection parameters are passed as keyword arguments
to the builder methods and forwarded to the Rust core:

| Setting           | Backend  | Example                                 |
| ----------------- | -------- | --------------------------------------- |
| `sqlite_db_path`  | SQLite   | `"/tmp/pynenc.db"`                      |
| `redis_url`       | Redis    | `"redis://localhost:6379"`              |
| `postgres_url`    | Postgres | `"postgresql://user:pass@localhost/db"` |
| `mongo_url`       | MongoDB  | `"mongodb://localhost:27017"`           |
| `mongo_db_name`   | MongoDB  | `"pynenc"`                              |
| `rabbitmq_url`    | RabbitMQ | `"amqp://guest:guest@localhost/"`       |
| `rabbitmq_prefix` | RabbitMQ | `"my_app"`                              |
