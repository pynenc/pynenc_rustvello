"""MongoDB 3.6 (transaction-free) integration test fixtures.

Starts a single MongoDB 3.6 container (session-scoped) and provides
``app_instance`` and ``mongo3_app`` fixtures for all tests in this
directory.  The rustvello-mongo3 backend uses optimistic CAS for status
transitions instead of multi-document transactions.
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

_mongo3_counter = itertools.count(1)


def _next_app_id() -> str:
    return f"integ_mongo3_{next(_mongo3_counter)}"


@pytest.fixture(scope="session")
def mongo3_url() -> Generator[str, None, None]:
    """Start a MongoDB 3.6 container and yield a connection URI."""
    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer("mongo:3.6") as m:
        yield m.get_connection_url()


@pytest.fixture(scope="function")
def mongo3_app(mongo3_url: str) -> Generator[Pynenc, None, None]:
    app = (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_mongo3(mongo_url=mongo3_url, mongo_db_name="pynenc_test")
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass


@pytest.fixture(scope="function")
def app_instance(mongo3_url: str) -> Generator[Pynenc, None, None]:
    """Single-backend app_instance for standard pynenc test suites."""
    app = (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_mongo3(mongo_url=mongo3_url, mongo_db_name="pynenc_test")
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass
