"""PostgreSQL integration test fixtures.

Starts a single PostgreSQL 16 container (session-scoped) and provides
``app_instance`` and ``postgres_app`` fixtures for all tests in this
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

_pg_counter = itertools.count(1)


def _next_app_id() -> str:
    return f"integ_pg_{next(_pg_counter)}"


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    """Start a PostgreSQL 16 container and yield a libpq connection string."""
    import urllib.parse

    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16") as pg:
        url = pg.get_connection_url()
        parsed = urllib.parse.urlparse(url)
        conn = (
            f"host={parsed.hostname} port={parsed.port} "
            f"user={parsed.username} password={parsed.password} "
            f"dbname={parsed.path.lstrip('/')}"
        )
        yield conn


@pytest.fixture(scope="function")
def postgres_app(postgres_url: str) -> Generator[Pynenc, None, None]:
    app = (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_postgres(postgres_url=postgres_url)
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass


@pytest.fixture(scope="function")
def app_instance(postgres_url: str) -> Generator[Pynenc, None, None]:
    """Single-backend app_instance for standard pynenc test suites."""
    app = (
        PynencBuilder()
        .app_id(_next_app_id())
        .rustvello_postgres(postgres_url=postgres_url)
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass
