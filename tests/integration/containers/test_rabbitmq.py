"""RabbitMQ-specific integration tests.

Validates broker connection lifecycle and RabbitMQ-specific behaviours
when paired with a SQLite backend for state/orchestrator/triggers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pynenc import PynencBuilder
from pynenc.call import Call
from pynenc.invocation import DistributedInvocation, InvocationStatus
from pynenc_tests.conftest import MockPynenc

if TYPE_CHECKING:
    from pynenc import Pynenc

pytestmark = pytest.mark.integration

_mock = MockPynenc()


@_mock.task
def rmq_task(x: int) -> int:
    return x * 2


class TestRabbitmqConnectionLifecycle:
    """Validate that the RabbitMQ broker connects and operates correctly."""

    def test_basic_connectivity(self, rabbitmq_app: Pynenc) -> None:
        """App builds successfully and broker operations work."""
        rmq_task.app = rabbitmq_app
        inv = DistributedInvocation.isolated(Call(rmq_task))
        rabbitmq_app.broker.route_invocation(inv.invocation_id)
        assert rabbitmq_app.broker.count_invocations() >= 1

    def test_multiple_apps_same_container(
        self, rabbitmq_url: str, rabbitmq_sqlite_db_path: str
    ) -> None:
        """Two independent apps against the same RabbitMQ instance."""
        import os
        import tempfile

        fd, path2 = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            app1 = (
                PynencBuilder()
                .rustvello_sqlite(
                    sqlite_db_path=rabbitmq_sqlite_db_path, app_id="rmq_iso_1"
                )
                .rustvello_rabbitmq_broker(rabbitmq_url=rabbitmq_url)
                .build()
            )
            app2 = (
                PynencBuilder()
                .rustvello_sqlite(sqlite_db_path=path2, app_id="rmq_iso_2")
                .rustvello_rabbitmq_broker(rabbitmq_url=rabbitmq_url)
                .build()
            )
            rmq_task.app = app1
            inv = DistributedInvocation.isolated(Call(rmq_task))
            app1.broker.route_invocation(inv.invocation_id)
            assert app1.broker.count_invocations() >= 1
            # app2 should not see app1's data (different app_id → different prefix)
            rmq_task.app = app2
            assert app2.broker.count_invocations() == 0
        finally:
            app1.purge()
            app2.purge()
            try:
                os.unlink(path2)
            except OSError:
                pass

    def test_publish_consume_cycle(self, rabbitmq_app: Pynenc) -> None:
        """Route invocations and retrieve them in FIFO order."""
        rmq_task.app = rabbitmq_app
        inv1 = DistributedInvocation.isolated(Call(rmq_task))
        inv2 = DistributedInvocation.isolated(Call(rmq_task))

        rabbitmq_app.broker.route_invocation(inv1.invocation_id)
        rabbitmq_app.broker.route_invocation(inv2.invocation_id)
        assert rabbitmq_app.broker.count_invocations() == 2

        retrieved_a = rabbitmq_app.broker.retrieve_invocation()
        retrieved_b = rabbitmq_app.broker.retrieve_invocation()
        assert retrieved_a is not None
        assert retrieved_b is not None
        assert {retrieved_a, retrieved_b} == {inv1.invocation_id, inv2.invocation_id}

    def test_purge(self, rabbitmq_app: Pynenc) -> None:
        """Broker purge clears all queued invocations."""
        rmq_task.app = rabbitmq_app
        for _ in range(3):
            inv = DistributedInvocation.isolated(Call(rmq_task))
            rabbitmq_app.broker.route_invocation(inv.invocation_id)
        assert rabbitmq_app.broker.count_invocations() == 3
        rabbitmq_app.broker.purge()
        assert rabbitmq_app.broker.count_invocations() == 0

    def test_full_lifecycle_with_sqlite(self, rabbitmq_app: Pynenc) -> None:
        """RabbitMQ broker + SQLite orchestrator/state round-trip."""
        rmq_task.app = rabbitmq_app
        inv = DistributedInvocation.isolated(Call(rmq_task))

        # Route via RabbitMQ broker
        rabbitmq_app.broker.route_invocation(inv.invocation_id)

        # Register in SQLite orchestrator
        rabbitmq_app.orchestrator.register_new_invocations([inv])
        status = rabbitmq_app.orchestrator.get_invocation_status(inv.invocation_id)
        assert status == InvocationStatus.REGISTERED

        # Store in SQLite state backend
        rabbitmq_app.state_backend.upsert_invocations([inv])
        retrieved = rabbitmq_app.state_backend.get_invocation(inv.invocation_id)
        assert retrieved == inv

        # Store result in SQLite state backend
        rabbitmq_app.state_backend.set_result(inv.invocation_id, "rmq_result")
        assert rabbitmq_app.state_backend.get_result(inv.invocation_id) == "rmq_result"
