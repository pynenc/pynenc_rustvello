"""State backend test fixtures for Docker-backed container backends.

Overrides ``app_instance`` so that the standard pynenc state_backend
integration tests run against each container backend (postgres, redis,
mongo, mongo3).
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder
from pynenc.identifiers.call_id import CallId
from pynenc.identifiers.invocation_id import InvocationId
from pynenc.identifiers.task_id import TaskId

if TYPE_CHECKING:
    from collections.abc import Generator

    from _pytest.fixtures import FixtureRequest
    from pynenc import Pynenc

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Unique app_id counter — avoids multiton collisions
# ---------------------------------------------------------------------------

_sb_app_counter = itertools.count(1)


def _next_app_id(backend: str) -> str:
    return f"container_sb_{backend}_{next(_sb_app_counter)}"


# ---------------------------------------------------------------------------
# app_instance override — parametrized by container backend
# ---------------------------------------------------------------------------


@pytest.fixture(
    params=["postgres", "redis", "mongo", "mongo3"],
    ids=["postgres", "redis", "mongo", "mongo3"],
    scope="function",
)
def app_instance(
    request: FixtureRequest,
    postgres_url: str,
    redis_url: str,
    mongo_url: str,
    mongo3_url: str,
) -> Generator[Pynenc, None, None]:
    """Pynenc app instance backed by a container, for state backend tests."""
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
# Identifier fixtures required by test_set_pynenc_exceptions
# (normally provided by pynenc_tests/conftest.py root conftest)
# ---------------------------------------------------------------------------


@pytest.fixture
def task_id() -> TaskId:
    return TaskId("some_module", "some_func")


@pytest.fixture
def other_task_id() -> TaskId:
    return TaskId("some_other_module", "some_other_func")


@pytest.fixture
def call_id(task_id: TaskId) -> CallId:
    return CallId(task_id=task_id, args_id="some_args_id")


@pytest.fixture
def other_call_id(other_task_id: TaskId) -> CallId:
    return CallId(task_id=other_task_id, args_id="some_other_args_id")


@pytest.fixture
def inv_id() -> InvocationId:
    return InvocationId("some_inv_id")


@pytest.fixture
def other_inv_id() -> InvocationId:
    return InvocationId("some_other_inv_id")
