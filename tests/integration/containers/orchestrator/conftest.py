"""Orchestrator test fixtures for Docker-backed container backends.

Overrides ``app_instance`` so that the standard pynenc orchestrator
integration tests run against each container backend (postgres, redis,
mongo, mongo3).
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder
from pynenc.call import Call
from pynenc.invocation import DistributedInvocation
from pynenc_tests.integration.orchestrator.orchestrator_tasks import (
    dummy_concat,
    dummy_key_arg,
    dummy_mirror,
    dummy_sum,
    dummy_task,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from _pytest.fixtures import FixtureRequest
    from pynenc import Pynenc
    from pynenc.task import Task

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Unique app_id counter — avoids multiton collisions
# ---------------------------------------------------------------------------

_orch_app_counter = itertools.count(1)


def _next_app_id(backend: str) -> str:
    return f"container_orch_{backend}_{next(_orch_app_counter)}"


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
    """Pynenc app instance backed by a container, for orchestrator tests."""
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
# Task fixtures (mirrored from orchestrator/conftest.py)
# ---------------------------------------------------------------------------


@pytest.fixture
def task_dummy_io(app_instance: Pynenc) -> Task:
    dummy_task.app = app_instance
    return dummy_task


@pytest.fixture
def task_sum_io(app_instance: Pynenc) -> Task:
    dummy_sum.app = app_instance
    return dummy_sum


@pytest.fixture
def task_concat_io(app_instance: Pynenc) -> Task:
    dummy_concat.app = app_instance
    return dummy_concat


@pytest.fixture
def task_mirror_io(app_instance: Pynenc) -> Task:
    dummy_mirror.app = app_instance
    return dummy_mirror


@pytest.fixture
def task_key_arg_io(app_instance: Pynenc) -> Task:
    dummy_key_arg.app = app_instance
    return dummy_key_arg


@pytest.fixture
def dummy_invocation_io(task_dummy_io: Task) -> DistributedInvocation:
    return DistributedInvocation.isolated(Call(task_dummy_io))
