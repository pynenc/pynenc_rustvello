"""Named queues on the container backends engine-cloud uses: MongoDB 3.6 and RabbitMQ.

Mirrors a two-pool deployment: a general ``hpa`` queue and a high-concurrency
``hyper`` queue, with a runner that consumes only ``hyper``.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder
from pynenc.conf.config_broker import MAX_PRIORITY, MIN_PRIORITY
from pynenc.identifiers.invocation_id import InvocationId
from pynenc.invocation import InvocationStatus
from pynenc_tests.conftest import MockPynenc

if TYPE_CHECKING:
    from collections.abc import Generator

    from pynenc import Pynenc

pytestmark = pytest.mark.integration

QUEUES = ("default", "hpa", "hyper")
_mock = MockPynenc()


@_mock.task(queue="hyper", priority=5.0)
def hyper_task(x: int) -> int:
    return x * 2


@_mock.task(queue="hpa")
def hpa_task(x: int) -> int:
    return x + 1


def _build(backend: str, request: pytest.FixtureRequest, app_id: str) -> PynencBuilder:
    if backend.startswith("mongo3"):
        builder = PynencBuilder().rustvello(
            backend="mongo3",
            mongo_url=request.getfixturevalue("mongo3_url"),
            mongo_db_name="pynenc_test",
            app_id=app_id,
        )
        if backend == "mongo3+rabbitmq":
            # engine-cloud's stack: Mongo 3.6 orchestrator/state, RabbitMQ transport
            builder = builder.rustvello_rabbitmq_broker(
                rabbitmq_url=request.getfixturevalue("rabbitmq_url")
            )
        return builder
    db_path = request.getfixturevalue("rabbitmq_sqlite_db_path")
    return (
        PynencBuilder()
        .rustvello_sqlite(sqlite_db_path=db_path, app_id=app_id)
        .rustvello_rabbitmq_broker(rabbitmq_url=request.getfixturevalue("rabbitmq_url"))
    )


@pytest.fixture(params=["mongo3", "rabbitmq", "mongo3+rabbitmq"])
def queue_app(request: pytest.FixtureRequest) -> Generator[Pynenc, None, None]:
    """App declaring the three queues; the runner consumes only ``hyper``."""
    selected = os.environ.get("RUSTVELLO_TEST_BACKEND")
    if selected is not None and selected not in request.param.split("+"):
        pytest.skip(
            f"RUSTVELLO_TEST_BACKEND selects another backend than {request.param}"
        )
    app_id = f"queues_{request.param}_{uuid.uuid4().hex[:8]}"
    app = (
        _build(request.param, request, app_id)
        .thread_runner()
        .custom_config(queues=QUEUES, runner={"queues": ["hyper"]})
        .build()
    )
    yield app
    try:
        app.purge()
    except Exception:
        pass


def test_bare_broker_api_honours_queue_and_priority(queue_app: Pynenc) -> None:
    broker = queue_app.broker
    low, high, general = (InvocationId(str(uuid.uuid4())) for _ in range(3))
    broker.route_invocation(low, "hyper", MIN_PRIORITY)
    broker.route_invocation(high, "hyper", MAX_PRIORITY)
    broker.route_invocation(general, "hpa", 0.0)

    assert broker.count_invocations(("hyper",)) == 2
    assert broker.count_invocations(("hpa",)) == 1
    assert broker.count_invocations(("default",)) == 0
    assert broker.retrieve_invocation("hyper") == high
    assert broker.retrieve_invocation("hyper") == low
    assert broker.retrieve_invocation("hyper") is None
    assert broker.retrieve_invocation("hpa") == general
    assert broker.count_invocations() == 0


def test_runner_restricted_to_hyper_leaves_hpa_work_queued(queue_app: Pynenc) -> None:
    for task in (hyper_task, hpa_task):
        task.app = queue_app
        queue_app.tasks[task.task_id] = task

    hyper_inv = hyper_task(21)
    hpa_inv = hpa_task(1)
    assert queue_app.broker.count_invocations(("hyper",)) == 1
    assert queue_app.broker.count_invocations(("hpa",)) == 1

    runner_thread = threading.Thread(target=queue_app.runner.run, daemon=True)
    runner_thread.start()
    try:
        assert hyper_inv.result == 42
        # the hpa invocation must still be waiting: nobody consumes that queue
        deadline = time.time() + 5
        while time.time() < deadline:
            time.sleep(0.2)
        assert queue_app.broker.count_invocations(("hpa",)) == 1
        assert (
            queue_app.orchestrator.get_invocation_status(hpa_inv.invocation_id)
            == InvocationStatus.REGISTERED
        )
    finally:
        queue_app.runner.stop_runner_loop()
        runner_thread.join(timeout=30)
