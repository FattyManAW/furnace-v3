"""furnace-v3 state machine — test suite"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src.state_machine import validate, allowed, ORDER_TRANSITIONS

def test_all_valid_transitions():
    """Every defined transition must pass."""
    for from_s, to_set in ORDER_TRANSITIONS.items():
        for to_s in to_set:
            ok, err = validate("order", from_s, to_s)
            assert ok, f"VALID transition failed: '{from_s}' → '{to_s}': {err}"

def test_terminal_states():
    """completed and cancelled have no outgoing."""
    assert allowed("completed") == []
    assert allowed("cancelled") == []

def test_illegal_jumps():
    """Jumping outside transition matrix must fail."""
    illegal = [
        ("pending", "completed"),
        ("pending", "in_progress"),
        ("scheduled", "completed"),
        ("completed", "anything"),
        ("in_progress", "pending"),
    ]
    for f, t in illegal:
        ok, err = validate("order", f, t)
        assert not ok, f"ILLEGAL transition should fail: '{f}' → '{t}'"

def test_unknown_status():
    """Unknown status names must fail."""
    ok, err = validate("order", "pending", "nonexistent")
    assert not ok
    ok, err = validate("order", "nonexistent", "scheduled")
    assert not ok

def test_blocked_paths():
    """blocked can go to scheduled or cancelled."""
    assert "scheduled" in allowed("blocked")
    assert "cancelled" in allowed("blocked")
    # blocked → in_progress should NOT be allowed
    ok, err = validate("order", "blocked", "in_progress")
    assert not ok

def test_full_lifecycle():
    """pending→scheduled→in_progress→completed — full happy path."""
    path = [
        ("pending", "scheduled"),
        ("scheduled", "in_progress"),
        ("in_progress", "completed"),
    ]
    for f, t in path:
        ok, err = validate("order", f, t)
        assert ok, f"Lifecycle transition failed: '{f}' → '{t}': {err}"

def test_ten_transitions():
    """ORDER_TRANSITIONS must contain exactly 10 entries."""
    total = sum(len(v) for v in ORDER_TRANSITIONS.values())
    assert total == 9, f"Expected 9 transitions, got {total}"

if __name__ == "__main__":
    tests = [f for name, f in list(globals().items()) if name.startswith("test_")]
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
        except AssertionError as e:
            print(f"  ❌ {t.__name__}: {e}")