"""Named-queue routing through the Rust brokers (pynenc 0.4 contract).

Covers the two routing paths: the bare ``BaseBroker`` API (no task identity,
sentinel Python-lane task) and the orchestrator path used by real task calls,
which passes the task's queue, priority and identity.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder
from pynenc.conf.config_broker import MAX_PRIORITY, MIN_PRIORITY
from pynenc.identifiers.invocation_id import InvocationId
from pynenc_tests.conftest import MockPynenc

if TYPE_CHECKING:
    from pynenc import Pynenc

mock_app = MockPynenc()


@mock_app.task(queue="payments", priority=10.0)
def payment_task() -> str:
    return "payment"


@mock_app.task(queue="payments", priority=MAX_PRIORITY)
def urgent_payment_task() -> str:
    return "urgent"


@mock_app.task
def default_task() -> str:
    return "default"


@pytest.fixture(params=["mem", "sqlite"])
def queue_app(request: pytest.FixtureRequest, temp_sqlite_db_path: str) -> Pynenc:
    builder = PynencBuilder().app_id(f"queues_{request.param}")
    if request.param == "mem":
        builder = builder.rustvello_mem()
    else:
        builder = builder.rustvello_sqlite(sqlite_db_path=temp_sqlite_db_path)
    return builder.custom_config(queues=("default", "payments", "reports")).build()


def test_bare_broker_api_routes_per_queue_and_priority(queue_app: Pynenc) -> None:
    broker = queue_app.broker
    low, high, other = (
        InvocationId(str(uuid.uuid4())),
        InvocationId(str(uuid.uuid4())),
        InvocationId(str(uuid.uuid4())),
    )
    broker.route_invocation(low, "payments", MIN_PRIORITY)
    broker.route_invocation(high, "payments", MAX_PRIORITY)
    broker.route_invocation(other, "reports", 0.0)

    assert broker.count_invocations(("payments",)) == 2
    assert broker.count_invocations(("payments", "reports")) == 3
    assert broker.count_invocations(("default",)) == 0

    assert broker.retrieve_invocation("payments") == high
    assert broker.retrieve_invocation("payments") == low
    assert broker.retrieve_invocation("payments") is None
    assert broker.retrieve_invocation("reports") == other
    assert broker.retrieve_invocation() is None


def test_batch_routing_keeps_queue(queue_app: Pynenc) -> None:
    broker = queue_app.broker
    ids = [InvocationId(str(uuid.uuid4())) for _ in range(3)]
    broker.route_invocations(ids, "reports", 1.0)
    assert broker.count_invocations(("reports",)) == 3
    retrieved = {broker.retrieve_invocation("reports") for _ in range(3)}
    assert retrieved == set(ids)


def test_task_calls_route_to_their_configured_queue(queue_app: Pynenc) -> None:
    for task in (payment_task, urgent_payment_task, default_task):
        task.app = queue_app
        queue_app.tasks[task.task_id] = task

    default_inv = default_task()
    payment_inv = payment_task()
    urgent_inv = urgent_payment_task()

    broker = queue_app.broker
    assert broker.count_invocations(("payments",)) == 2
    assert broker.retrieve_invocation("payments") == urgent_inv.invocation_id
    assert broker.retrieve_invocation("payments") == payment_inv.invocation_id
    assert broker.retrieve_invocation("default") == default_inv.invocation_id
    assert broker.count_invocations() == 0


def test_purge_empties_every_queue(queue_app: Pynenc) -> None:
    broker = queue_app.broker
    broker.route_invocation(InvocationId(str(uuid.uuid4())), "payments", 0.0)
    broker.route_invocation(InvocationId(str(uuid.uuid4())), "reports", 0.0)
    broker.purge()
    assert broker.count_invocations(("payments", "reports", "default")) == 0
