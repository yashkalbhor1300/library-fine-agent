"""SQLite member profile store for TA2."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "library_ta2.db"

class ProfileStore:
    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = str(db_path)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS profiles (member_id TEXT PRIMARY KEY, profile_json TEXT NOT NULL)")
            conn.commit()

    def save_profile(self, member_id: str, profile: dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO profiles(member_id, profile_json) VALUES (?, ?) "
                "ON CONFLICT(member_id) DO UPDATE SET profile_json=excluded.profile_json",
                (member_id, json.dumps(profile)),
            )
            conn.commit()

    def get_profile(self, member_id: str) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT profile_json FROM profiles WHERE member_id=?", (member_id,)).fetchone()
        return json.loads(row[0]) if row else {}
