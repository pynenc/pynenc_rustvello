"""Container fixtures for Docker-backed integration tests.

Session-scoped containers keep start-up cost low; function-scoped app
instances with ``purge()`` ensure test isolation.

Requires Docker and ``pynenc[test-integration]``.

Backend filtering
-----------------
Set ``RUSTVELLO_TEST_BACKEND`` to run only one backend's tests::

    RUSTVELLO_TEST_BACKEND=postgres pytest tests/integration/

When unset (local dev), all backends run.  CI uses a matrix strategy to
run each backend in a separate parallel job.
"""

from __future__ import annotations

import itertools
import os
import tempfile
from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder

if TYPE_CHECKING:
    from collections.abc import Generator

    from pynenc import Pynenc

# ---------------------------------------------------------------------------
# Marker — every test in this package requires Docker
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Backend filtering — read once, used by every sub-conftest
# ---------------------------------------------------------------------------

_SELECTED_BACKEND: str | None = os.environ.get("RUSTVELLO_TEST_BACKEND")


def filter_backends(all_backends: list[str]) -> list[str]:
    """Return *all_backends* filtered by ``RUSTVELLO_TEST_BACKEND``.

    When the env var is unset every backend is returned (local dev).
    When set, only the matching backend is returned; if the requested
    backend is not in the list the result is empty and pytest will
    skip the parametrized tests automatically.
    """
    if _SELECTED_BACKEND is None:
        return all_backends
    return [b for b in all_backends if b == _SELECTED_BACKEND]


# ---------------------------------------------------------------------------
# Unique app_id counter — avoids multiton collisions across tests
# ---------------------------------------------------------------------------

_container_app_counter = itertools.count(1)


def _next_app_id(backend: str) -> str:
    return f"container_{backend}_{next(_container_app_counter)}"


# ---------------------------------------------------------------------------
# Session-scoped containers (skipped when not selected)
# ---------------------------------------------------------------------------


def _skip_unless_selected(name: str) -> None:
    """Skip a container fixture when a different backend is selected."""
    if _SELECTED_BACKEND is not None and _SELECTED_BACKEND != name:
        pytest.skip(f"RUSTVELLO_TEST_BACKEND={_SELECTED_BACKEND}, skipping {name}")


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    """Start a PostgreSQL 16 container and yield a connection URL."""
    _skip_unless_selected("postgres")
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16") as pg:
        url = pg.get_connection_url()
        import urllib.parse

        parsed = urllib.parse.urlparse(url)
        conn = (
            f"host={parsed.hostname} port={parsed.port} "
            f"user={parsed.username} password={parsed.password} "
            f"dbname={parsed.path.lstrip('/')}"
        )
        yield conn


@pytest.fixture(scope="session")
def redis_url() -> Generator[str, None, None]:
    """Start a Redis 7 container and yield a connection URI."""
    _skip_unless_selected("redis")
    from testcontainers.redis import RedisContainer

    with RedisContainer("redis:7") as r:
        host = r.get_container_host_ip()
        port = r.get_exposed_port(6379)
        yield f"redis://{host}:{port}/"


@pytest.fixture(scope="session")
def mongo_url() -> Generator[str, None, None]:
    """Start a MongoDB 7 container and yield a connection URI."""
    _skip_unless_selected("mongo")
    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer("mongo:7") as m:
        yield m.get_connection_url()


@pytest.fixture(scope="session")
def mongo3_url() -> Generator[str, None, None]:
    """Start a MongoDB 3.6 container and yield a connection URI."""
    _skip_unless_selected("mongo3")
    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer("mongo:3.6") as m:
        yield m.get_connection_url()


# ---------------------------------------------------------------------------
# Function-scoped app builders (purge after each test)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def postgres_app(postgres_url: str) -> Generator[Pynenc, None, None]:
    """Pynenc app backed by the session Postgres container."""
    app = (
        PynencBuilder()
        .rustvello(
            backend="postgres",
            postgres_url=postgres_url,
            app_id=_next_app_id("postgres"),
        )
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass  # container may already be stopping


@pytest.fixture(scope="function")
def redis_app(redis_url: str) -> Generator[Pynenc, None, None]:
    """Pynenc app backed by the session Redis container."""
    app = (
        PynencBuilder()
        .rustvello(
            backend="redis",
            redis_url=redis_url,
            app_id=_next_app_id("redis"),
        )
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass


@pytest.fixture(scope="function")
def mongo_app(mongo_url: str) -> Generator[Pynenc, None, None]:
    """Pynenc app backed by the session MongoDB container."""
    app = (
        PynencBuilder()
        .rustvello(
            backend="mongo",
            mongo_url=mongo_url,
            mongo_db_name="pynenc_test",
            app_id=_next_app_id("mongo"),
        )
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass


@pytest.fixture(scope="function")
def mongo3_app(mongo3_url: str) -> Generator[Pynenc, None, None]:
    """Pynenc app backed by the session MongoDB 3.6 container.

    Uses the ``mongo3`` backend which does not require transaction support.
    """
    app = (
        PynencBuilder()
        .rustvello(
            backend="mongo3",
            mongo_url=mongo3_url,
            mongo_db_name="pynenc_test",
            app_id=_next_app_id("mongo3"),
        )
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Parametrized cross-backend fixture
# ---------------------------------------------------------------------------


@pytest.fixture(
    params=filter_backends(["postgres", "redis", "mongo", "mongo3"]),
    scope="function",
)
def container_app(
    request: pytest.FixtureRequest,
    postgres_url: str,
    redis_url: str,
    mongo_url: str,
    mongo3_url: str,
) -> Generator[Pynenc, None, None]:
    """Parametrized fixture providing an app for each container backend."""
    backend: str = request.param
    kwargs: dict = {"app_id": _next_app_id(backend)}

    if backend == "postgres":
        kwargs["postgres_url"] = postgres_url
    elif backend == "redis":
        kwargs["redis_url"] = redis_url
    elif backend == "mongo":
        kwargs["mongo_url"] = mongo_url
        kwargs["mongo_db_name"] = "pynenc_test"
    elif backend == "mongo3":
        kwargs["mongo_url"] = mongo3_url
        kwargs["mongo_db_name"] = "pynenc_test"

    app = PynencBuilder().rustvello(backend=backend, **kwargs).build()
    yield app
    try:
        app.purge()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# RabbitMQ — broker-only container (paired with SQLite for state/orch/etc.)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def rabbitmq_url() -> Generator[str, None, None]:
    """Start a RabbitMQ 3.13 container and yield an AMQP URI."""
    _skip_unless_selected("rabbitmq")
    from testcontainers.rabbitmq import RabbitMqContainer

    with RabbitMqContainer("rabbitmq:3.13-management") as rmq:
        host = rmq.get_container_host_ip()
        port = rmq.get_exposed_port(rmq.port)
        yield f"amqp://{rmq.username}:{rmq.password}@{host}:{port}/{rmq.vhost}"


@pytest.fixture(scope="function")
def rabbitmq_sqlite_db_path() -> Generator[str, None, None]:
    """Temporary SQLite database for use alongside the RabbitMQ broker."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def rabbitmq_app(
    rabbitmq_url: str,
    rabbitmq_sqlite_db_path: str,
) -> Generator[Pynenc, None, None]:
    """Pynenc app using RabbitMQ broker + SQLite for everything else."""
    app = (
        PynencBuilder()
        .rustvello_sqlite(
            sqlite_db_path=rabbitmq_sqlite_db_path, app_id=_next_app_id("rabbitmq")
        )
        .rustvello_rabbitmq_broker(rabbitmq_url=rabbitmq_url)
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass
