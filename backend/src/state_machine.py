"""
furnace-v3 — 排爐系統狀態機
Linear Method lifecycle: pending→scheduled→in_progress→completed
"""
from typing import Literal

OrderStatus = Literal["pending", "scheduled", "in_progress", "completed", "cancelled", "blocked"]

ORDER_TRANSITIONS: dict[str, set[str]] = {
    "pending":      {"scheduled", "cancelled"},
    "scheduled":    {"in_progress", "cancelled", "blocked"},
    "in_progress":  {"completed", "blocked"},
    "completed":    set(),
    "blocked":      {"scheduled", "cancelled"},
    "cancelled":    set(),
}

def validate(entity: str, from_status: str, to_status: str) -> tuple[bool, str]:
    matrix = ORDER_TRANSITIONS
    if to_status not in matrix:
        return False, f"Unknown status: '{to_status}'"
    allowed = matrix.get(from_status)
    if allowed is None:
        return False, f"Unknown status: '{from_status}'"
    if to_status not in allowed:
        a = "', '".join(sorted(allowed)) if allowed else "(terminal)"
        return False, f"Invalid: '{from_status}' → '{to_status}'. Allowed: → '{a}'"
    return True, ""

def allowed(from_status: str) -> list[str]:
    return sorted(ORDER_TRANSITIONS.get(from_status, set()))