"""PostgreSQL-specific integration tests.

Validates connection lifecycle and Postgres-specific behaviors.
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
def pg_task(x: int) -> int:
    return x * 2


def _runner_ctx() -> RunnerContext:
    return RunnerContext(runner_cls="TestRunner", runner_id="test-pg-runner")


class TestPostgresConnectionLifecycle:
    """Validate that the Postgres backend connects, operates, and survives reconnection."""

    def test_basic_connectivity(self, postgres_app: Pynenc) -> None:
        """App builds successfully and core operations work."""
        pg_task.app = postgres_app
        inv = DistributedInvocation.isolated(Call(pg_task))
        postgres_app.orchestrator.register_new_invocations([inv])
        status = postgres_app.orchestrator.get_invocation_status(inv.invocation_id)
        assert status == InvocationStatus.REGISTERED

    def test_multiple_apps_same_container(self, postgres_url: str) -> None:
        """Two independent apps against the same Postgres instance."""
        app1 = (
            PynencBuilder()
            .rustvello(backend="postgres", postgres_url=postgres_url, app_id="postgres_iso_1")
            .build()
        )
        app2 = (
            PynencBuilder()
            .rustvello(backend="postgres", postgres_url=postgres_url, app_id="postgres_iso_2")
            .build()
        )
        try:
            pg_task.app = app1
            inv = DistributedInvocation.isolated(Call(pg_task))
            app1.broker.route_invocation(inv.invocation_id)
            assert app1.broker.count_invocations() >= 1
            # app2 should not see app1's data (different app_id)
            pg_task.app = app2
            assert app2.broker.count_invocations() == 0
        finally:
            app1.purge()
            app2.purge()

    def test_full_lifecycle(self, postgres_app: Pynenc) -> None:
        """Broker→Orchestrator→StateBackend round-trip within one app."""
        pg_task.app = postgres_app
        inv = DistributedInvocation.isolated(Call(pg_task))

        # Route via broker
        postgres_app.broker.route_invocation(inv.invocation_id)

        # Register in orchestrator
        postgres_app.orchestrator.register_new_invocations([inv])

        # Store in state backend
        postgres_app.state_backend.upsert_invocations([inv])
        retrieved = postgres_app.state_backend.get_invocation(inv.invocation_id)
        assert retrieved == inv

        # Store result
        postgres_app.state_backend.set_result(inv.invocation_id, "result_pg")
        assert postgres_app.state_backend.get_result(inv.invocation_id) == "result_pg"

    def test_purge_clears_all(self, postgres_app: Pynenc) -> None:
        """Purge removes data from all subsystems."""
        pg_task.app = postgres_app
        inv = DistributedInvocation.isolated(Call(pg_task))
        postgres_app.broker.route_invocation(inv.invocation_id)
        postgres_app.orchestrator.register_new_invocations([inv])
        postgres_app.state_backend.upsert_invocations([inv])

        postgres_app.purge()

        assert postgres_app.broker.count_invocations() == 0
        assert postgres_app.orchestrator.count_invocations() == 0
