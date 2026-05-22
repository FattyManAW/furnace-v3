"""furnace-v3 — FastAPI 主程式"""
import pathlib, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.state_machine import validate as validate_transition

logger = logging.getLogger("furnace-v3")
_GIT_COMMIT = pathlib.Path(__file__).parent.parent / "GIT_COMMIT"
_COMMIT_HASH = _GIT_COMMIT.read_text().strip() if _GIT_COMMIT.exists() else "unknown"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("furnace-v3 starting — supervision active")
    yield
    logger.info("SIGTERM — draining")
    try: logger.info("shutdown complete")
    except Exception as e: logger.error(f"shutdown error: {e}")

app = FastAPI(title="排爐系統 v3", version="3.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok", "commit": _COMMIT_HASH, "version": "3.0.0"}

@app.patch("/api/v1/orders/{order_id}/status")
def transition_status(order_id: str, body: dict):
    to_status = body.get("status", "")
    ok, err = validate_transition("order", "pending", to_status)
    if not ok:
        raise HTTPException(400, err)
    return {"order_id": order_id, "status": to_status, "transition": "ok"}

@app.get("/api/v1/kanban")
def kanban():
    return {"columns": ["pending", "scheduled", "in_progress", "completed", "cancelled", "blocked"], "items": []}