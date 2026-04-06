from pynenc.call import compute_args_id


def test_args_id() -> None:
    args = {"a": "1", "b": "2"}
    args_id = compute_args_id(args)
    assert isinstance(args_id, str)
    assert len(args_id) == 64  # Length of a SHA256 hash


def test_empty_args_returns_no_args() -> None:
    assert compute_args_id({}) == "no_args"


def test_deterministic_ordering() -> None:
    """Same args in different insertion order produce the same hash."""
    h1 = compute_args_id({"x": "42", "y": "hello"})
    h2 = compute_args_id({"y": "hello", "x": "42"})
    assert h1 == h2


def test_different_args_different_hash() -> None:
    h1 = compute_args_id({"x": "42"})
    h2 = compute_args_id({"x": "43"})
    assert h1 != h2


def test_no_delimiter_collision() -> None:
    """Ensure delimiter chars inside values don't cause hash collisions."""
    h1 = compute_args_id({"a": "b;c=d"})
    h2 = compute_args_id({"a": "b", "c": "d"})
    assert h1 != h2


def test_unicode_args() -> None:
    h = compute_args_id({"key": "日本語テスト"})
    assert isinstance(h, str)
    assert len(h) == 64


class TestCrossSystemCompatibility:
    """Verify pynenc and rustvello produce identical hashes.

    These tests are the wire-format unification contract: they guarantee
    that any system (Python, Rust, or future Go/JS) sharing a backend
    computes the same ``args_id`` for the same serialized arguments.
    """

    @staticmethod
    def _rust_hash(args: dict[str, str]) -> str:
        from rustvello import compute_args_id as rust_compute

        return rust_compute(args)

    def test_simple_args(self) -> None:
        args = {"a": "1", "b": "2"}
        assert compute_args_id(args) == self._rust_hash(args)

    def test_single_arg(self) -> None:
        args = {"key": "value"}
        assert compute_args_id(args) == self._rust_hash(args)

    def test_empty_args(self) -> None:
        assert compute_args_id({}) == "no_args"
        # Rust also returns "no_args" for empty
        assert self._rust_hash({}) == "no_args"

    def test_unicode_values(self) -> None:
        args = {"msg": "こんにちは世界", "emoji": "🚀"}
        assert compute_args_id(args) == self._rust_hash(args)

    def test_special_json_chars(self) -> None:
        args = {"data": '{"nested": "json", "arr": [1,2]}'}
        assert compute_args_id(args) == self._rust_hash(args)

    def test_delimiter_chars_in_values(self) -> None:
        args = {"key": "val=ue;with;delims"}
        assert compute_args_id(args) == self._rust_hash(args)

    def test_many_args_ordering(self) -> None:
        args = {f"arg_{i}": str(i) for i in range(50)}
        assert compute_args_id(args) == self._rust_hash(args)

    def test_whitespace_values(self) -> None:
        args = {"sp": "  ", "tab": "\t", "nl": "\n"}
        assert compute_args_id(args) == self._rust_hash(args)

    def test_empty_string_values(self) -> None:
        args = {"a": "", "b": "notempty"}
        assert compute_args_id(args) == self._rust_hash(args)
