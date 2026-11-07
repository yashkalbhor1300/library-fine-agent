"""SQLite audit ledger for simulated fine-waiver actions.

This records demo events only. It does not connect to or modify a live library
account, payment system, or production fine record.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "library_ta2.db"


class WaiverStore:
    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = str(db_path)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS waiver_events (
                    request_id TEXT PRIMARY KEY,
                    member_id TEXT NOT NULL,
                    fine_amount TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status = 'APPROVED'),
                    approval_method TEXT NOT NULL,
                    authenticated_identity INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def record_approved_waiver(
        self,
        *,
        request_id: str,
        member_id: str,
        fine_amount: str,
        reason: str,
        approval: dict[str, Any],
    ) -> dict[str, str]:
        """Persist an approved demo event once; reject missing/mismatched approval."""
        if not request_id or not member_id or not fine_amount:
            raise ValueError("Request ID, member ID, and fine amount are required.")
        if (
            approval.get("approved") is not True
            or approval.get("status") != "APPROVED"
            or approval.get("request_id") != request_id
        ):
            raise PermissionError(
                "A matching explicit human approval is required; no waiver was recorded."
            )

        created_at = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO waiver_events (
                    request_id, member_id, fine_amount, reason, status,
                    approval_method, authenticated_identity, created_at
                ) VALUES (?, ?, ?, ?, 'APPROVED', ?, 0, ?)
                """,
                (
                    request_id,
                    member_id,
                    fine_amount,
                    reason,
                    approval.get("approval_method", "unknown"),
                    created_at,
                ),
            )
            conn.commit()

        return {
            "request_id": request_id,
            "status": "APPROVED",
            "fine_amount": fine_amount,
            "created_at": created_at,
        }

    def get_event(self, request_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM waiver_events WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        return dict(row) if row else None
