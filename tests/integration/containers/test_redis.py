"""Redis-specific integration tests.

Validates connection lifecycle and Redis-specific behaviors.
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
def redis_task(x: int) -> int:
    return x + 1


class TestRedisConnectionLifecycle:
    """Validate that the Redis backend connects and operates correctly."""

    def test_basic_connectivity(self, redis_app: Pynenc) -> None:
        redis_task.app = redis_app
        inv = DistributedInvocation.isolated(Call(redis_task))
        redis_app.orchestrator.register_new_invocations([inv])
        status = redis_app.orchestrator.get_invocation_status(inv.invocation_id)
        assert status == InvocationStatus.REGISTERED

    def test_multiple_apps_same_container(self, redis_url: str) -> None:
        """Two independent apps against the same Redis instance."""
        app1 = (
            PynencBuilder()
            .rustvello(backend="redis", redis_url=redis_url, app_id="redis_iso_1")
            .build()
        )
        app2 = (
            PynencBuilder()
            .rustvello(backend="redis", redis_url=redis_url, app_id="redis_iso_2")
            .build()
        )
        try:
            redis_task.app = app1
            inv = DistributedInvocation.isolated(Call(redis_task))
            app1.broker.route_invocation(inv.invocation_id)
            assert app1.broker.count_invocations() >= 1
            redis_task.app = app2
            assert app2.broker.count_invocations() == 0
        finally:
            app1.purge()
            app2.purge()

    def test_full_lifecycle(self, redis_app: Pynenc) -> None:
        """Broker→Orchestrator→StateBackend round-trip."""
        redis_task.app = redis_app
        inv = DistributedInvocation.isolated(Call(redis_task))

        redis_app.broker.route_invocation(inv.invocation_id)
        redis_app.orchestrator.register_new_invocations([inv])
        redis_app.state_backend.upsert_invocations([inv])
        retrieved = redis_app.state_backend.get_invocation(inv.invocation_id)
        assert retrieved == inv

        redis_app.state_backend.set_result(inv.invocation_id, "result_redis")
        assert redis_app.state_backend.get_result(inv.invocation_id) == "result_redis"

    def test_purge_clears_all(self, redis_app: Pynenc) -> None:
        redis_task.app = redis_app
        inv = DistributedInvocation.isolated(Call(redis_task))
        redis_app.broker.route_invocation(inv.invocation_id)
        redis_app.orchestrator.register_new_invocations([inv])
        redis_app.state_backend.upsert_invocations([inv])

        redis_app.purge()

        assert redis_app.broker.count_invocations() == 0
        assert redis_app.orchestrator.count_invocations() == 0
