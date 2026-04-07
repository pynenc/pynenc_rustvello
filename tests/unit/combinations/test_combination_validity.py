"""Unit tests for Rust backend class bundles.

Verifies that the Rust backend adapter classes exposed by pynenc-rustvello
are internally consistent:
- Each bundle (Mem / SQLite) contains exactly 5 component classes
- All classes in a bundle belong to the same backend variant
- No overlap between Mem and SQLite bundles
"""

import pytest

from pynenc_rustvello.broker import RustMemBroker, RustSqliteBroker
from pynenc_rustvello.client_data_store import (
    RustMemClientDataStore,
    RustSqliteClientDataStore,
)
from pynenc_rustvello.orchestrator import RustMemOrchestrator, RustSqliteOrchestrator
from pynenc_rustvello.state_backend import (
    RustMemStateBackend,
    RustSqliteStateBackend,
)
from pynenc_rustvello.trigger import RustMemTrigger, RustSqliteTrigger

RUST_MEM_CLASSES = (
    RustMemClientDataStore,
    RustMemBroker,
    RustMemOrchestrator,
    RustMemStateBackend,
    RustMemTrigger,
)
RUST_SQLITE_CLASSES = (
    RustSqliteClientDataStore,
    RustSqliteBroker,
    RustSqliteOrchestrator,
    RustSqliteStateBackend,
    RustSqliteTrigger,
)


# ---------------------------------------------------------------------------
# Bundle consistency tests
# ---------------------------------------------------------------------------


def test_rust_mem_bundle_size() -> None:
    """RUST_MEM bundle must have exactly 5 components."""
    assert len(RUST_MEM_CLASSES) == 5


def test_rust_sqlite_bundle_size() -> None:
    """RUST_SQLITE bundle must have exactly 5 components."""
    assert len(RUST_SQLITE_CLASSES) == 5


@pytest.mark.parametrize("cls", RUST_MEM_CLASSES, ids=lambda c: c.__name__)
def test_rust_mem_classes_are_mem(cls: type) -> None:
    """Every class in RUST_MEM_CLASSES must be a RustMem* adapter."""
    assert cls.__name__.startswith("RustMem"), f"{cls.__name__} is not a RustMem* class"


@pytest.mark.parametrize("cls", RUST_SQLITE_CLASSES, ids=lambda c: c.__name__)
def test_rust_sqlite_classes_are_sqlite(cls: type) -> None:
    """Every class in RUST_SQLITE_CLASSES must be a RustSqlite* adapter."""
    assert cls.__name__.startswith("RustSqlite"), (
        f"{cls.__name__} is not a RustSqlite* class"
    )


def test_no_overlap_between_bundles() -> None:
    """Mem and SQLite class bundles must have no classes in common."""
    overlap = set(RUST_MEM_CLASSES) & set(RUST_SQLITE_CLASSES)
    assert not overlap, (
        f"Classes appear in both bundles: {[c.__name__ for c in overlap]}"
    )


def test_no_python_classes_in_rust_bundles() -> None:
    """No pure-Python backend class should appear in a Rust bundle."""
    from pynenc.broker import MemBroker, SQLiteBroker
    from pynenc.client_data_store import MemClientDataStore, SQLiteClientDataStore
    from pynenc.orchestrator import MemOrchestrator, SQLiteOrchestrator
    from pynenc.state_backend import MemStateBackend, SQLiteStateBackend
    from pynenc.trigger import MemTrigger, SQLiteTrigger

    python_only = {
        MemClientDataStore,
        MemBroker,
        MemOrchestrator,
        MemStateBackend,
        MemTrigger,
        SQLiteClientDataStore,
        SQLiteBroker,
        SQLiteOrchestrator,
        SQLiteStateBackend,
        SQLiteTrigger,
    }
    all_rust = set(RUST_MEM_CLASSES) | set(RUST_SQLITE_CLASSES)
    leaked = all_rust & python_only
    assert not leaked, (
        f"Python-only classes found in Rust bundles: {[c.__name__ for c in leaked]}"
    )
