"""Broker test fixtures for Docker-backed container backends.

Overrides ``app_instance`` so that the standard pynenc broker integration
tests run against each container backend (postgres, redis, mongo, mongo3,
rabbitmq).
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

    from _pytest.fixtures import FixtureRequest
    from pynenc import Pynenc

pytestmark = pytest.mark.integration

_broker_app_counter = itertools.count(1)


def _next_app_id(backend: str) -> str:
    return f"container_broker_{backend}_{next(_broker_app_counter)}"


@pytest.fixture(
    params=["postgres", "redis", "mongo", "mongo3", "rabbitmq"],
    ids=["postgres", "redis", "mongo", "mongo3", "rabbitmq"],
    scope="function",
)
def app_instance(
    request: FixtureRequest,
    postgres_url: str,
    redis_url: str,
    mongo_url: str,
    mongo3_url: str,
    rabbitmq_url: str,
) -> Generator[Pynenc, None, None]:
    """Pynenc app instance backed by a container, for broker tests."""
    backend: str = request.param
    kwargs: dict = {"app_id": _next_app_id(backend)}
    db_path: str | None = None

    if backend == "rabbitmq":
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        app = (
            PynencBuilder()
            .rustvello_sqlite(sqlite_db_path=db_path, app_id=kwargs["app_id"])
            .rustvello_rabbitmq_broker(rabbitmq_url=rabbitmq_url)
            .build()
        )
    else:
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
    if db_path is not None:
        try:
            os.unlink(db_path)
        except OSError:
            pass
