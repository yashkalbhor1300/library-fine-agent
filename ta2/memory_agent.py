"""Thread memory backed by SQLite.

Stores the latest conversation facts so follow-ups such as
"and if it were a reference book?" can reuse the previous overdue days.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "library_ta2.db"

class ThreadMemory:
    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = str(db_path)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS thread_memory (thread_id TEXT PRIMARY KEY, state_json TEXT NOT NULL)")
            conn.commit()

    def get(self, thread_id: str) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT state_json FROM thread_memory WHERE thread_id=?", (thread_id,)).fetchone()
        return json.loads(row[0]) if row else {}

    def update(self, thread_id: str, **values: Any) -> dict[str, Any]:
        state = self.get(thread_id)
        state.update(values)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO thread_memory(thread_id, state_json) VALUES (?, ?) "
                "ON CONFLICT(thread_id) DO UPDATE SET state_json=excluded.state_json",
                (thread_id, json.dumps(state)),
            )
            conn.commit()
        return state
