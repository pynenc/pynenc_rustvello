"""Redis integration test fixtures.

Starts a single Redis 7 container (session-scoped) and provides
``app_instance`` and ``redis_app`` fixtures for all tests in this
directory.
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder

if TYPE_CHECKING:
    from collections.abc import Generator

    from pynenc import Pynenc

pytestmark = pytest.mark.integration

_redis_counter = itertools.count(1)


def _next_app_id() -> str:
    return f"integ_redis_{next(_redis_counter)}"


@pytest.fixture(scope="session")
def redis_url() -> Generator[str, None, None]:
    """Start a Redis 7 container and yield a connection URI."""
    from testcontainers.redis import RedisContainer

    with RedisContainer("redis:7") as r:
        host = r.get_container_host_ip()
        port = r.get_exposed_port(6379)
        yield f"redis://{host}:{port}/"


@pytest.fixture(scope="function")
def redis_app(redis_url: str) -> Generator[Pynenc, None, None]:
    app = (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_redis(redis_url=redis_url)
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass


@pytest.fixture(scope="function")
def app_instance(redis_url: str) -> Generator[Pynenc, None, None]:
    """Single-backend app_instance for standard pynenc test suites."""
    app = (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_redis(redis_url=redis_url)
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass
