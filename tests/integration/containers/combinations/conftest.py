"""Combination test fixtures for Docker-backed container backends.

Overrides ``app_combination_instance`` so that the standard pynenc
combination tests (runner × serializer) run against each container
backend (postgres, redis, mongo, mongo3).
"""

from __future__ import annotations

import multiprocessing
import os
import tempfile
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pynenc import PynencBuilder
from pynenc.serializer.base_serializer import BaseSerializer
from pynenc.util.subclasses import get_all_subclasses
from pynenc_tests import util
from pynenc_tests.integration.combinations import tasks, tasks_async
from pynenc_tests.util.subclasses import get_runner_subclasses

if TYPE_CHECKING:
    from collections.abc import Generator

    from _pytest.fixtures import FixtureRequest
    from pynenc import Pynenc
    from pynenc.task import Task

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Component combinations (runner × serializer only — backend is container)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContainerAppComponents:
    """Runner / serializer pair for container-backed combination tests."""

    serializer: type
    runner: type

    @property
    def combination_id(self) -> str:
        return f"{self.runner.__name__}({self.serializer.__name__})"


def _build_combinations() -> list[ContainerAppComponents]:
    runners = sorted(get_runner_subclasses(), key=lambda cls: cls.__name__)
    serializers = sorted(
        get_all_subclasses(BaseSerializer),  # type: ignore
        key=lambda cls: cls.__name__,
    )
    combinations: list[ContainerAppComponents] = []
    for i, runner_cls in enumerate(runners):
        serializer_cls = serializers[i % len(serializers)]
        combinations.append(ContainerAppComponents(serializer_cls, runner_cls))
    return combinations


# ---------------------------------------------------------------------------
# Core fixture override — builds the app against the container backend
# ---------------------------------------------------------------------------

_BACKEND_PARAMS = ["postgres", "redis", "mongo", "mongo3", "rabbitmq"]


@pytest.fixture(
    params=_build_combinations(),
    ids=lambda comp: comp.combination_id,
)
def app_combination_instance(
    request: FixtureRequest,
    monkeypatch: MonkeyPatch,
    postgres_url: str,
    redis_url: str,
    mongo_url: str,
    mongo3_url: str,
    rabbitmq_url: str,
    container_backend: str,
) -> Pynenc:
    """Build a Pynenc instance for each runner×serializer combination
    using the container backend provided by ``container_backend``."""
    components: ContainerAppComponents = request.param
    test_module, test_name = util.get_module_name(request)
    app_id = f"{test_module}.{test_name}.{container_backend}"

    kwargs: dict = {
        "app_id": app_id,
    }
    if container_backend == "postgres":
        kwargs["postgres_url"] = postgres_url
    elif container_backend == "redis":
        kwargs["redis_url"] = redis_url
    elif container_backend == "mongo":
        kwargs["mongo_url"] = mongo_url
        kwargs["mongo_db_name"] = "pynenc_test"
    elif container_backend == "mongo3":
        kwargs["mongo_url"] = mongo3_url
        kwargs["mongo_db_name"] = "pynenc_test"

    if container_backend == "rabbitmq":
        # RabbitMQ is broker-only; pair with a temp SQLite for everything else
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        kwargs["sqlite_db_path"] = db_path
        builder = (
            PynencBuilder()
            .rustvello_sqlite(sqlite_db_path=db_path, app_id=app_id)
            .rustvello_rabbitmq_broker(rabbitmq_url=rabbitmq_url)
        )
    else:
        builder = PynencBuilder().rustvello(backend=container_backend, **kwargs)
    builder._config["serializer_cls"] = components.serializer.__name__
    builder._config["runner_cls"] = components.runner.__name__
    builder._config["logging_level"] = "debug"

    # Environment variables for subprocess-spawning runners
    monkeypatch.setenv("PYNENC__APP_ID", app_id)
    monkeypatch.setenv("PYNENC__SERIALIZER_CLS", components.serializer.__name__)
    monkeypatch.setenv("PYNENC__RUNNER_CLS", components.runner.__name__)
    monkeypatch.setenv("PYNENC__PRINT_ARGUMENTS", "False")
    monkeypatch.setenv("PYNENC__RUNNER_LOOP_SLEEP_TIME_SEC", "0.01")
    monkeypatch.setenv("PYNENC__INVOCATION_WAIT_RESULTS_SLEEP_TIME_SEC", "0.01")
    if container_backend == "postgres":
        monkeypatch.setenv("PYNENC__POSTGRES_URL", postgres_url)
    elif container_backend == "redis":
        monkeypatch.setenv("PYNENC__REDIS_URL", redis_url)
    elif container_backend in ("mongo", "mongo3"):
        url = mongo_url if container_backend == "mongo" else mongo3_url
        monkeypatch.setenv("PYNENC__MONGO_URL", url)
    elif container_backend == "rabbitmq":
        monkeypatch.setenv("PYNENC__RABBITMQ_URL", rabbitmq_url)
        monkeypatch.setenv("PYNENC__SQLITE_DB_PATH", kwargs.get("sqlite_db_path", ""))

    app = builder.build()

    # Propagate resolved class names for subprocess runners
    monkeypatch.setenv(
        "PYNENC__CLIENT_DATA_STORE_CLS",
        app.client_data_store.__class__.__name__,
    )
    monkeypatch.setenv(
        "PYNENC__ORCHESTRATOR_CLS",
        app.orchestrator.__class__.__name__,
    )
    monkeypatch.setenv("PYNENC__BROKER_CLS", app.broker.__class__.__name__)
    monkeypatch.setenv(
        "PYNENC__STATE_BACKEND_CLS",
        app.state_backend.__class__.__name__,
    )
    monkeypatch.setenv("PYNENC__LOGGING_LEVEL", "debug")

    return app


@pytest.fixture(
    params=_BACKEND_PARAMS,
    scope="session",
)
def container_backend(request: FixtureRequest) -> str:
    """Session-scoped parametrized backend name."""
    return request.param


# ---------------------------------------------------------------------------
# Standard combination fixtures (same as combinations/conftest.py)
# ---------------------------------------------------------------------------


def _replace_tasks_app(app: Pynenc) -> None:
    for mod in [tasks, tasks_async]:
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if hasattr(obj, "app"):
                obj.app = app
                obj._conf = None


@pytest.fixture
def app(app_combination_instance: Pynenc) -> Generator[Pynenc, None, None]:
    yield app_combination_instance
    try:
        app_combination_instance.runner.stop_runner_loop()
    except Exception:
        pass
    for child in multiprocessing.active_children():
        try:
            child.kill()
        except Exception:
            pass


@pytest.fixture(scope="function")
def task_raise_exception(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks.raise_exception


@pytest.fixture(scope="function")
def task_sum(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks.sum_task


@pytest.fixture(scope="function")
def task_get_text(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks.get_text


@pytest.fixture(scope="function")
def task_get_upper(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks.get_upper


@pytest.fixture(scope="function")
def task_retry_once(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks.retry_once


@pytest.fixture(scope="function")
def task_sleep(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks.sleep_seconds


@pytest.fixture(scope="function")
def task_cpu_intensive_no_conc(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks.cpu_intensive_no_conc


@pytest.fixture(scope="function")
def task_distribute_cpu_work(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks.distribute_cpu_work


@pytest.fixture(scope="function")
def task_async_add(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks_async.async_add


@pytest.fixture(scope="function")
def task_async_get_text(app: Pynenc) -> Task:
    _replace_tasks_app(app)
    return tasks_async.async_get_text
