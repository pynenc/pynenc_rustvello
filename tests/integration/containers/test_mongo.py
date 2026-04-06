"""MongoDB-specific integration tests.

Validates connection lifecycle and Mongo-specific behaviors.
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
def mongo_task(x: int) -> int:
    return x * 3


def _runner_ctx() -> RunnerContext:
    return RunnerContext(runner_cls="TestRunner", runner_id="test-mongo-runner")


class TestMongoConnectionLifecycle:
    """Validate that the MongoDB backend connects and operates correctly."""

    def test_basic_connectivity(self, mongo_app: Pynenc) -> None:
        mongo_task.app = mongo_app
        inv = DistributedInvocation.isolated(Call(mongo_task))
        mongo_app.orchestrator.register_new_invocations([inv])
        status = mongo_app.orchestrator.get_invocation_status(inv.invocation_id)
        assert status == InvocationStatus.REGISTERED

    def test_multiple_apps_same_container(self, mongo_url: str) -> None:
        """Two independent apps against the same Mongo instance."""
        app1 = (
            PynencBuilder()
            .rustvello(
                backend="mongo",
                mongo_url=mongo_url,
                mongo_db_name="pynenc_test",
                app_id="mongo_iso_1",
            )
            .build()
        )
        app2 = (
            PynencBuilder()
            .rustvello(
                backend="mongo",
                mongo_url=mongo_url,
                mongo_db_name="pynenc_test",
                app_id="mongo_iso_2",
            )
            .build()
        )
        try:
            mongo_task.app = app1
            inv = DistributedInvocation.isolated(Call(mongo_task))
            app1.broker.route_invocation(inv.invocation_id)
            assert app1.broker.count_invocations() >= 1
            mongo_task.app = app2
            assert app2.broker.count_invocations() == 0
        finally:
            app1.purge()
            app2.purge()

    def test_full_lifecycle(self, mongo_app: Pynenc) -> None:
        """Broker→Orchestrator→StateBackend round-trip."""
        mongo_task.app = mongo_app
        inv = DistributedInvocation.isolated(Call(mongo_task))

        mongo_app.broker.route_invocation(inv.invocation_id)
        mongo_app.orchestrator.register_new_invocations([inv])
        mongo_app.state_backend.upsert_invocations([inv])
        retrieved = mongo_app.state_backend.get_invocation(inv.invocation_id)
        assert retrieved == inv

        mongo_app.state_backend.set_result(inv.invocation_id, "result_mongo")
        assert mongo_app.state_backend.get_result(inv.invocation_id) == "result_mongo"

    def test_purge_clears_all(self, mongo_app: Pynenc) -> None:
        mongo_task.app = mongo_app
        inv = DistributedInvocation.isolated(Call(mongo_task))
        mongo_app.broker.route_invocation(inv.invocation_id)
        mongo_app.orchestrator.register_new_invocations([inv])
        mongo_app.state_backend.upsert_invocations([inv])

        mongo_app.purge()

        assert mongo_app.broker.count_invocations() == 0
        assert mongo_app.orchestrator.count_invocations() == 0
