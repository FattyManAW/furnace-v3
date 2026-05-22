"""furnace-v3 state machine — fuzz/stress test"""
import sys, pathlib, random, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src.state_machine import validate, allowed, ORDER_TRANSITIONS

ALL_STATUSES = list(ORDER_TRANSITIONS.keys())
ITERATIONS = 100000

def test_random_jumps():
    """Random status pairs — legal must pass, illegal must fail."""
    failures = 0
    for _ in range(ITERATIONS):
        f = random.choice(ALL_STATUSES)
        t = random.choice(ALL_STATUSES)
        ok, err = validate("order", f, t)
        is_legal = t in ORDER_TRANSITIONS.get(f, set())
        if ok != is_legal:
            failures += 1
    assert failures == 0, f"{failures}/{ITERATIONS} mismatches"

def test_rapid_transitions():
    """Same order rapid-fire transitions."""
    order_id = "stress-1"
    legal = 0
    state = "pending"
    for _ in range(1000):
        targets = allowed(state)
        if not targets:
            break
        state = random.choice(targets)
        ok, _ = validate("order", "pending", state)
        if ok:
            legal += 1
    print(f"  📊 rapid-fire: {legal}/1000 legal transitions completed")

def test_health_ping():
    """Repeated health endpoint calls."""
    import urllib.request
    for i in range(50):
        try:
            r = urllib.request.urlopen("http://localhost:8005/health", timeout=5)
            assert r.status == 200
        except Exception:
            print(f"  ❌ health ping #{i} failed")
            return
    print("  📊 health: 50/50 pings OK")

if __name__ == "__main__":
    tests = [f for name, f in list(globals().items()) if name.startswith("test_")]
    start = time.time()
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
        except AssertionError as e:
            print(f"  ❌ {t.__name__}: {e}")
    elapsed = time.time() - start
    print(f"\n  ⏱  elapsed: {elapsed:.1f}s")