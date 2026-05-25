"""Smoke tests for furnace-v3 health + models"""
from fastapi.testclient import TestClient
from main import app
from models import get_db, VALID_STATUSES

client = TestClient(app)

def test_health_200():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_stats_200():
    r = client.get("/api/v1/stats")
    assert r.status_code == 200
    assert "total" in r.json()

def test_kanban_200():
    r = client.get("/api/v1/kanban")
    assert r.status_code == 200
    assert "columns" in r.json()
    assert "items" in r.json()

def test_create_order_200():
    r = client.post("/api/v1/orders", json={"order_no":"TEST-001","product":"測試","quantity":1})
    assert r.status_code == 200
    assert r.json()["status"] == "pending"

def test_bad_transition_400():
    client.post("/api/v1/orders", json={"order_no":"TEST-002","product":"測試2","quantity":1})
    r = client.patch("/api/v1/orders/2", json={"status":"completed"})
    assert r.status_code == 400

def test_db_models():
    db = get_db()
    try:
        c = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        assert c >= 0
        assert "pending" in VALID_STATUSES
    finally:
        db.close()
