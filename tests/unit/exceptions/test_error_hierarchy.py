"""Validate exception inheritance chains for both pynenc and rustvello exceptions.

Step 8.4 — Error Equivalence Tests (384).
"""

import pytest
import rustvello.rustvello as rv
from pynenc.exceptions import (
    AlreadyInitializedError,
    ConcurrencyRetryError,
    ConfigError,
    ConfigMultiInheritanceError,
    InvalidTaskOptionsError,
    InvocationConcurrencyWithDifferentArgumentsError,
    InvocationError,
    InvocationNotFoundError,
    InvocationStatusError,
    InvocationStatusOwnershipError,
    InvocationStatusRaceConditionError,
    InvocationStatusTransitionError,
    PynencError,
    RetryError,
    RunnerError,
    RunnerNotExecutableError,
    SerializationError,
    StateBackendError,
    TaskError,
    TaskParallelProcessingError,
    TaskRoutingError,
)

# ── pynenc hierarchy ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "exc_cls, parents",
    [
        # Retry branch
        (RetryError, [PynencError]),
        (ConcurrencyRetryError, [RetryError, PynencError]),
        # Serialization
        (SerializationError, [PynencError]),
        # Task branch
        (TaskError, [PynencError]),
        (InvalidTaskOptionsError, [TaskError, PynencError]),
        (TaskRoutingError, [TaskError, PynencError]),
        (
            InvocationConcurrencyWithDifferentArgumentsError,
            [TaskRoutingError, TaskError, PynencError],
        ),
        (TaskParallelProcessingError, [TaskError, PynencError]),
        # Invocation
        (InvocationError, [PynencError]),
        # StateBackend branch
        (StateBackendError, [PynencError]),
        (InvocationNotFoundError, [StateBackendError, PynencError]),
        # Runner
        (RunnerNotExecutableError, [PynencError]),
        (RunnerError, [PynencError]),
        # Config
        (ConfigError, [PynencError]),
        (ConfigMultiInheritanceError, [ConfigError, PynencError]),
        # Other
        (AlreadyInitializedError, [PynencError]),
        # Status branch
        (InvocationStatusError, [PynencError]),
        (InvocationStatusRaceConditionError, [InvocationStatusError, PynencError]),
        (InvocationStatusTransitionError, [InvocationStatusError, PynencError]),
        (InvocationStatusOwnershipError, [InvocationStatusError, PynencError]),
    ],
    ids=lambda x: x.__name__ if isinstance(x, type) else None,
)
def test_pynenc_exception_hierarchy(exc_cls: type, parents: list[type]) -> None:
    """Every pynenc exception must be a subclass of its documented parents."""
    for parent in parents:
        assert issubclass(exc_cls, parent), (
            f"{exc_cls.__name__} is not a subclass of {parent.__name__}"
        )


# ── rustvello (Rust-defined) hierarchy ───────────────────────────────


@pytest.mark.parametrize(
    "exc_name, parent_names",
    [
        # Base
        ("RustvelloError", ["Exception"]),
        # Retry
        ("RetryError", ["RustvelloError"]),
        ("ConcurrencyRetryError", ["RetryError", "RustvelloError"]),
        # Serialization
        ("SerializationError", ["RustvelloError"]),
        # Task
        ("TaskError", ["RustvelloError"]),
        ("TaskNotFoundError", ["TaskError", "RustvelloError"]),
        ("TaskNotRegisteredError", ["TaskError", "RustvelloError"]),
        ("CycleDetectedError", ["TaskError", "RustvelloError"]),
        ("RunnerNotExecutableError", ["TaskError", "RustvelloError"]),
        ("TaskClassNotFoundError", ["TaskError", "RustvelloError"]),
        # Invocation
        ("InvocationError", ["RustvelloError"]),
        ("InvocationNotFoundError", ["InvocationError", "RustvelloError"]),
        # Status (under Invocation)
        ("InvocationStatusError", ["InvocationError", "RustvelloError"]),
        ("StatusTransitionError", ["InvocationStatusError", "RustvelloError"]),
        ("StatusOwnershipError", ["InvocationStatusError", "RustvelloError"]),
        ("StatusRaceConditionError", ["InvocationStatusError", "RustvelloError"]),
        # Infrastructure
        ("StateBackendError", ["RustvelloError"]),
        ("BrokerError", ["RustvelloError"]),
        ("RunnerError", ["RustvelloError"]),
        ("ConfigurationError", ["RustvelloError"]),
        # Internal
        ("InternalError", ["RustvelloError"]),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
def test_rustvello_exception_hierarchy(exc_name: str, parent_names: list[str]) -> None:
    """Every Rust-defined exception must be a subclass of its documented parents."""
    exc_cls = getattr(rv, exc_name)
    for parent_name in parent_names:
        parent_cls = (
            Exception if parent_name == "Exception" else getattr(rv, parent_name)
        )
        assert issubclass(exc_cls, parent_cls), (
            f"rustvello.{exc_name} is not a subclass of rustvello.{parent_name}"
        )
