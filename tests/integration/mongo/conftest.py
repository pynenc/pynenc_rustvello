"""MongoDB 7 integration test fixtures.

Starts a single MongoDB 7 container (session-scoped) and provides
``app_instance`` and ``mongo_app`` fixtures for all tests in this
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

_mongo_counter = itertools.count(1)


def _next_app_id() -> str:
    return f"integ_mongo_{next(_mongo_counter)}"


@pytest.fixture(scope="session")
def mongo_url() -> Generator[str, None, None]:
    """Start a MongoDB 7 container and yield a connection URI."""
    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer("mongo:7") as m:
        yield m.get_connection_url()


@pytest.fixture(scope="function")
def mongo_app(mongo_url: str) -> Generator[Pynenc, None, None]:
    app = (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_mongo(mongo_url=mongo_url, mongo_db_name="pynenc_test")
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass


@pytest.fixture(scope="function")
def app_instance(mongo_url: str) -> Generator[Pynenc, None, None]:
    """Single-backend app_instance for standard pynenc test suites."""
    app = (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_mongo(mongo_url=mongo_url, mongo_db_name="pynenc_test")
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass
