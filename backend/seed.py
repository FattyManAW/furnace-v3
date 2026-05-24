"""furnace-v3 — seed demo data"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from models import get_db

db = get_db()
try:
    db.execute("DELETE FROM orders")
    db.commit()

    orders = [
        ("FO-2026-001", "220kV 套管 A 型", 50, "urgent", "pending", "M-001", "10.1罐", 198),
        ("FO-2026-002", "110kV 變壓器鐵芯", 30, "high", "pending", "M-002", "10.2罐", 160),
        ("FO-2026-003", "66kV 套管", 80, "normal", "pending", "M-003", "10.3罐", 120),
        ("FO-2026-004", "345kV GIS 組件", 12, "urgent", "pending", "M-004", "10.4罐", 320),
        ("FO-2026-005", "220kV 套管 B 型", 40, "high", "pending", "M-001", "10.2罐", 210),
        ("FO-2026-006", "110kV 配電盤", 60, "normal", "pending", "M-005", "10.1罐", 90),
        ("FO-2026-007", "345kV 避雷器", 8, "high", "pending", "M-006", "10.4罐", 280),
        ("FO-2026-008", "220kV 變電站一次側", 3, "urgent", "pending", "M-007", "10.3罐", 400),
        ("FO-2026-009", "66kV 變壓器", 25, "normal", "pending", "M-002", "10.1罐", 140),
        ("FO-2026-010", "110kV 套管套組", 45, "high", "pending", "M-008", "10.2罐", 175),
    ]

    for o in orders:
        db.execute(
            "INSERT INTO orders (order_no,product,quantity,priority,status,mold_id,kiln_id,est_hours,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,datetime('now'),datetime('now'))",
            o)

    db.commit()
    print(f"Seed complete: {len(orders)} orders")
finally:
    db.close()