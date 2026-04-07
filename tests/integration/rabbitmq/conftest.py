"""RabbitMQ integration test fixtures.

Starts a RabbitMQ 3.13 container (session-scoped) paired with a temporary
SQLite database for state/orchestrator/triggers.  Provides ``app_instance``
and ``rabbitmq_app`` fixtures.
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

pytestmark = pytest.mark.integration

_rmq_counter = itertools.count(1)


def _next_app_id() -> str:
    return f"integ_rmq_{next(_rmq_counter)}"


@pytest.fixture(scope="session")
def rabbitmq_url() -> Generator[str, None, None]:
    """Start a RabbitMQ 3.13 container and yield an AMQP URI."""
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


def _build_rmq_app(rabbitmq_url: str, db_path: str) -> Pynenc:
    return (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_sqlite(sqlite_db_path=db_path)
        .rustvello_rabbitmq_broker(rabbitmq_url=rabbitmq_url)
        .build()
    )


@pytest.fixture(scope="function")
def rabbitmq_app(
    rabbitmq_url: str,
    rabbitmq_sqlite_db_path: str,
) -> Generator[Pynenc, None, None]:
    app = _build_rmq_app(rabbitmq_url, rabbitmq_sqlite_db_path)
    yield app
    try:
        app.purge()
    except Exception:
        pass


@pytest.fixture(scope="function")
def app_instance(rabbitmq_url: str) -> Generator[Pynenc, None, None]:
    """Single-backend app_instance for standard pynenc test suites."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    app = _build_rmq_app(rabbitmq_url, db_path)
    yield app
    try:
        app.purge()
    except Exception:
        pass
    try:
        os.unlink(db_path)
    except OSError:
        pass
