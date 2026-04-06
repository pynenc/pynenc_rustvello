"""Unit test fixtures for pynenc-rustvello.

Parametrizes ``app_instance`` over the two backends that need no external
services: **mem** (in-process) and **sqlite** (temp file).

Postgres, Redis, and MongoDB backends connect from Rust code over TCP —
Python mocking libraries (fakeredis, mongomock) cannot intercept those
connections.  Those backends are exercised by the Docker-based integration
tests in ``tests/integration/containers/``.
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

_unit_app_counter = itertools.count(1)


def _next_app_id(backend: str) -> str:
    return f"unit_{backend}_{next(_unit_app_counter)}"


@pytest.fixture(scope="function")
def temp_sqlite_db_path() -> Generator[str, None, None]:
    """Temporary SQLite file, removed after the test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture(params=["mem", "sqlite"], scope="function")
def app_instance(
    request: pytest.FixtureRequest,
    temp_sqlite_db_path: str,
) -> Generator[Pynenc, None, None]:
    """Pynenc app backed by rustvello, parametrized over mem and sqlite."""
    backend: str = request.param

    if backend == "mem":
        app = PynencBuilder().app_id(_next_app_id("mem")).rustvello_mem().build()
    elif backend == "sqlite":
        app = (
            PynencBuilder().app_id(_next_app_id("sqlite")).rustvello_sqlite(sqlite_db_path=temp_sqlite_db_path).build()
        )
    else:
        raise ValueError(f"Unknown backend: {backend}")

    yield app
