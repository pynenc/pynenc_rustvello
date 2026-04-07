"""MongoDB 3.6 (transaction-free) integration tests.

Validates that the ``mongo3`` backend works correctly against a real
MongoDB 3.6 instance which does NOT support multi-document transactions.
The rustvello-mongo3 crate uses optimistic CAS for status transitions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder
from pynenc.call import Call
from pynenc.invocation import DistributedInvocation, InvocationStatus
from pynenc.runner.runner_context import RunnerContext
from pynenc_tests.conftest import MockPynenc

if TYPE_CHECKING:
    from pynenc import Pynenc

pytestmark = pytest.mark.integration

_mock = MockPynenc()


@_mock.task
def mongo3_task(x: int) -> int:
    return x * 3


def _runner_ctx() -> RunnerContext:
    return RunnerContext(runner_cls="TestRunner", runner_id="test-mongo3-runner")


class TestMongo3ConnectionLifecycle:
    """Validate that the MongoDB 3.6 backend connects and operates correctly."""

    def test_basic_connectivity(self, mongo3_app: Pynenc) -> None:
        mongo3_task.app = mongo3_app
        inv = DistributedInvocation.isolated(Call(mongo3_task))
        mongo3_app.orchestrator.register_new_invocations([inv])
        status = mongo3_app.orchestrator.get_invocation_status(inv.invocation_id)
        assert status == InvocationStatus.REGISTERED

    def test_multiple_apps_same_container(self, mongo3_url: str) -> None:
        """Two independent apps against the same Mongo 3.6 instance."""
        app1 = (
            PynencBuilder()
            .rustvello(
                backend="mongo3",
                mongo_url=mongo3_url,
                mongo_db_name="pynenc_test",
                app_id="mongo3_iso_1",
            )
            .build()
        )
        app2 = (
            PynencBuilder()
            .rustvello(
                backend="mongo3",
                mongo_url=mongo3_url,
                mongo_db_name="pynenc_test",
                app_id="mongo3_iso_2",
            )
            .build()
        )
        try:
            mongo3_task.app = app1
            inv = DistributedInvocation.isolated(Call(mongo3_task))
            app1.broker.route_invocation(inv.invocation_id)
            assert app1.broker.count_invocations() >= 1
            mongo3_task.app = app2
            assert app2.broker.count_invocations() == 0
        finally:
            app1.purge()
            app2.purge()

    def test_full_lifecycle(self, mongo3_app: Pynenc) -> None:
        """Broker→Orchestrator→StateBackend round-trip."""
        mongo3_task.app = mongo3_app
        inv = DistributedInvocation.isolated(Call(mongo3_task))

        mongo3_app.broker.route_invocation(inv.invocation_id)
        mongo3_app.orchestrator.register_new_invocations([inv])
        mongo3_app.state_backend.upsert_invocations([inv])
        retrieved = mongo3_app.state_backend.get_invocation(inv.invocation_id)
        assert retrieved == inv

        mongo3_app.state_backend.set_result(inv.invocation_id, "result_mongo3")
        assert mongo3_app.state_backend.get_result(inv.invocation_id) == "result_mongo3"

    def test_purge_clears_all(self, mongo3_app: Pynenc) -> None:
        mongo3_task.app = mongo3_app
        inv = DistributedInvocation.isolated(Call(mongo3_task))
        mongo3_app.broker.route_invocation(inv.invocation_id)
        mongo3_app.orchestrator.register_new_invocations([inv])
        mongo3_app.state_backend.upsert_invocations([inv])

        mongo3_app.purge()

        assert mongo3_app.broker.count_invocations() == 0
        assert mongo3_app.orchestrator.count_invocations() == 0

    def test_status_transitions_without_transactions(self, mongo3_app: Pynenc) -> None:
        """Verify status transitions work on Mongo 3.6 (no transaction support).

        This validates the optimistic CAS mechanism used by rustvello-mongo3
        for atomic status updates.
        """
        mongo3_task.app = mongo3_app
        inv = DistributedInvocation.isolated(Call(mongo3_task))
        ctx = _runner_ctx()

        mongo3_app.orchestrator.register_new_invocations([inv])
        assert (
            mongo3_app.orchestrator.get_invocation_status(inv.invocation_id)
            == InvocationStatus.REGISTERED
        )

        mongo3_app.orchestrator.set_invocation_status(
            inv.invocation_id, InvocationStatus.PENDING, ctx
        )
        assert (
            mongo3_app.orchestrator.get_invocation_status(inv.invocation_id)
            == InvocationStatus.PENDING
        )

        mongo3_app.orchestrator.set_invocation_status(
            inv.invocation_id, InvocationStatus.RUNNING, ctx
        )
        assert (
            mongo3_app.orchestrator.get_invocation_status(inv.invocation_id)
            == InvocationStatus.RUNNING
        )

        mongo3_app.orchestrator.set_invocation_status(
            inv.invocation_id, InvocationStatus.SUCCESS, ctx
        )
        assert (
            mongo3_app.orchestrator.get_invocation_status(inv.invocation_id)
            == InvocationStatus.SUCCESS
        )
