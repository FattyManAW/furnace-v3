"""furnace-v3 — SQLite order model"""
import sqlite3, os
from datetime import datetime

DB_PATH = os.environ.get("FURNACE_V3_DB", os.path.join(os.path.dirname(__file__), "..", "data", "furnace_v3.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no    TEXT NOT NULL UNIQUE,
    product     TEXT NOT NULL DEFAULT '',
    quantity    INTEGER NOT NULL DEFAULT 0,
    priority    TEXT NOT NULL DEFAULT 'normal',
    status      TEXT NOT NULL DEFAULT 'pending',
    mold_id     TEXT NOT NULL DEFAULT '',
    kiln_id     TEXT NOT NULL DEFAULT '',
    est_hours   REAL NOT NULL DEFAULT 0.0,
    notes       TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

VALID_STATUSES = {"pending", "scheduled", "in_progress", "completed", "cancelled", "blocked"}
VALID_PRIORITIES = {"low", "normal", "high", "urgent"}

def get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn