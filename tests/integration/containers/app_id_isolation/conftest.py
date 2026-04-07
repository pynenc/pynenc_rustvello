"""App ID isolation test fixtures for Docker-backed container backends.

Overrides ``app_instance`` so that the standard pynenc app_id_isolation
integration tests run against each container backend (postgres, redis,
mongo, mongo3).
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder

from tests.integration.containers.conftest import filter_backends

if TYPE_CHECKING:
    from collections.abc import Generator

    from _pytest.fixtures import FixtureRequest
    from pynenc import Pynenc

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Unique app_id counter — avoids multiton collisions
# ---------------------------------------------------------------------------

_iso_app_counter = itertools.count(1)


def _next_app_id(backend: str) -> str:
    return f"container_iso_{backend}_{next(_iso_app_counter)}"


# ---------------------------------------------------------------------------
# app_instance override — parametrized by container backend
# ---------------------------------------------------------------------------


@pytest.fixture(
    params=filter_backends(["postgres", "redis", "mongo", "mongo3"]),
    ids=lambda b: b,
    scope="function",
)
def app_instance(
    request: FixtureRequest,
    postgres_url: str,
    redis_url: str,
    mongo_url: str,
    mongo3_url: str,
) -> Generator[Pynenc, None, None]:
    """Pynenc app instance backed by a container, for app_id isolation tests."""
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
