"""furnace-v3 — FastAPI 主程式 (full CRUD)"""
import pathlib, logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from models import get_db, VALID_STATUSES, VALID_PRIORITIES
from src.state_machine import validate as validate_transition

logger = logging.getLogger("furnace-v3")
_GIT_COMMIT = pathlib.Path(__file__).parent / "GIT_COMMIT"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("furnace-v3 starting — supervision active, db ready")
    # Auto-seed if empty
    try:
        db = get_db()
        count = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        if count == 0:
            import seed
            logger.info(f"DB empty — seeding demo data")
        db.close()
    except Exception as e:
        logger.warning(f"seed check skipped: {e}")
    yield
    logger.info("SIGTERM — draining")
    try:
        logger.info("shutdown complete")
    except Exception as e:
        logger.error(f"shutdown error: {e}")

app = FastAPI(title="排爐系統 v3", version="3.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def _read_commit():
    p = pathlib.Path(__file__).parent / "GIT_COMMIT"
    return p.read_text().strip() if p.exists() else "unknown"

def _to_dict(row):
    return dict(row) if row else {}

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── Health ──────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "commit": _read_commit(), "version": "3.1.0"}

# ── Orders CRUD ─────────────────────────────────────────
@app.get("/api/v1/orders")
def list_orders(status: str = Query(None), priority: str = Query(None),
                limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    db = get_db()
    try:
        conds = []; params = []
        if status:
            conds.append("status=?"); params.append(status)
        if priority:
            conds.append("priority=?"); params.append(priority)
        where = (" WHERE " + " AND ".join(conds)) if conds else ""
        rows = db.execute(
            f"SELECT * FROM orders{where} ORDER BY id DESC LIMIT ? OFFSET ?",
            params + [limit, offset]).fetchall()
        total = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        return {"items": [_to_dict(r) for r in rows], "total": total}
    finally:
        db.close()

@app.post("/api/v1/orders")
def create_order(body: dict):
    required = {"order_no", "product", "quantity"}
    missing = required - set(body.keys())
    if missing:
        raise HTTPException(400, f"Missing fields: {', '.join(missing)}")
    status = body.get("status", "pending")
    if status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status: {status}")
    priority = body.get("priority", "normal")
    if priority not in VALID_PRIORITIES:
        raise HTTPException(400, f"Invalid priority: {priority}")
    db = get_db()
    try:
        now = _now()
        cur = db.execute(
            """INSERT INTO orders (order_no, product, quantity, priority, status,
               mold_id, kiln_id, est_hours, notes, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (body["order_no"], body["product"], body["quantity"],
             priority, status,
             body.get("mold_id", ""), body.get("kiln_id", ""),
             body.get("est_hours", 0.0), body.get("notes", ""), now, now))
        db.commit()
        return _to_dict(db.execute("SELECT * FROM orders WHERE id=?", (cur.lastrowid,)).fetchone())
    except Exception as e:
        db.rollback()
        if "UNIQUE" in str(e):
            raise HTTPException(409, f"Order {body['order_no']} already exists")
        raise HTTPException(500, str(e))
    finally:
        db.close()

@app.get("/api/v1/orders/{order_id}")
def get_order(order_id: int):
    db = get_db()
    try:
        row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if not row:
            raise HTTPException(404, f"Order {order_id} not found")
        return _to_dict(row)
    finally:
        db.close()

@app.patch("/api/v1/orders/{order_id}")
def update_order(order_id: int, body: dict):
    db = get_db()
    try:
        existing = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if not existing:
            raise HTTPException(404, f"Order {order_id} not found")

        # Status transition validation
        new_status = body.get("status")
        if new_status:
            if new_status not in VALID_STATUSES:
                raise HTTPException(400, f"Invalid status: {new_status}")
            ok, err = validate_transition("order", existing["status"], new_status)
            if not ok:
                raise HTTPException(400, err)

        allowed = {"product", "quantity", "priority", "status",
                   "mold_id", "kiln_id", "est_hours", "notes"}
        updates = {k: v for k, v in body.items() if k in allowed and v is not None}
        if not updates:
            return _to_dict(existing)
        if "priority" in updates and updates["priority"] not in VALID_PRIORITIES:
            raise HTTPException(400, f"Invalid priority: {updates['priority']}")
        sets = ", ".join(f"{k}=?" for k in updates)
        vals = list(updates.values()) + [_now(), order_id]
        db.execute(f"UPDATE orders SET {sets}, updated_at=? WHERE id=?", vals)
        db.commit()
        return _to_dict(db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone())
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))
    finally:
        db.close()

@app.delete("/api/v1/orders/{order_id}")
def delete_order(order_id: int):
    db = get_db()
    try:
        existing = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if not existing:
            raise HTTPException(404, f"Order {order_id} not found")
        db.execute("DELETE FROM orders WHERE id=?", (order_id,))
        db.commit()
        return {"deleted": True, "id": order_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))
    finally:
        db.close()

# ── Kanban (live data) ──────────────────────────────────
@app.get("/api/v1/kanban")
def kanban():
    db = get_db()
    try:
        columns = ["pending", "scheduled", "in_progress", "completed", "cancelled", "blocked"]
        rows = db.execute("SELECT * FROM orders ORDER BY priority DESC, created_at DESC").fetchall()
        items = [_to_dict(r) for r in rows]
        return {"columns": columns, "items": items}
    finally:
        db.close()

# ── Stats ───────────────────────────────────────────────
@app.get("/api/v1/stats")
def stats():
    db = get_db()
    try:
        total = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        by_status = db.execute(
            "SELECT status, COUNT(*) as cnt FROM orders GROUP BY status").fetchall()
        by_priority = db.execute(
            "SELECT priority, COUNT(*) as cnt FROM orders GROUP BY priority").fetchall()
        return {
            "total": total,
            "by_status": {r["status"]: r["cnt"] for r in by_status},
            "by_priority": {r["priority"]: r["cnt"] for r in by_priority},
        }
    finally:
        db.close()

# ── Sync Bridge (furnace-v2 → v3) ────────────────────────
FURNACE_V2_URL = "http://100.107.36.80:8002"

@app.post("/api/v1/sync/from-v2")
def sync_from_v2():
    """從 furnace-v2 optimizer 結果匯入訂單到 v3"""
    import urllib.request
    import json as _json
    db = get_db()
    try:
        req = urllib.request.Request(f"{FURNACE_V2_URL}/api/v1/schedule/optimize",
                                     data=b"{}", headers={"Content-Type": "application/json"},
                                     method="POST")
        resp = urllib.request.urlopen(req, timeout=30)
        schedule = _json.loads(resp.read())
        imported = 0
        skipped = 0
        for ks in schedule.get("kiln_summary", []):
            for entry in ks.get("orders", []):
                plan_no = entry.get("plan_no", "")
                if not plan_no:
                    skipped += 1
                    continue
                existing = db.execute(
                    "SELECT id FROM orders WHERE order_no=?", (plan_no,)).fetchone()
                if existing:
                    skipped += 1
                    continue
                db.execute(
                    """INSERT INTO orders (order_no, product, quantity, priority, status,
                       kiln_id, est_hours, notes, created_at, updated_at)
                       VALUES (?,?,?,?,?,?,?,?,datetime('now'),datetime('now'))""",
                    (plan_no, f"排產工單 {plan_no}", entry.get("qty", 0),
                     "normal", "pending",
                     ks.get("kiln_name", ""), entry.get("hours", 0),
                     f"from-v2: kiln={ks.get('kiln_id')}"))
                imported += 1
        db.commit()
        return {"imported": imported, "skipped": skipped,
                "total_v2": schedule["summary"]["total_orders"],
                "generated_at": schedule["summary"].get("generated_at")}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Sync failed: {e}")
    finally:
        db.close()