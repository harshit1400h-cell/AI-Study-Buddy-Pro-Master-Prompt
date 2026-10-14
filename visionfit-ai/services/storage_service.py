"""
Persistent Storage and Favorites Service for VisionFit AI
Uses local SQLite database alongside Streamlit session state for reliable favorites management.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "visionfit.db"


def init_db(db_path: Path = DB_PATH):
    """Initializes SQLite database and creates favorites table if not exists."""
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL,  -- 'recipe' or 'workout'
                title TEXT NOT NULL,
                summary TEXT,
                data_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_favorite(item_type: str, title: str, summary: str, data: Dict[str, Any], db_path: Path = DB_PATH) -> int:
    """Saves a recipe or workout to favorites. Returns the inserted row ID."""
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        cursor.execute("""
            INSERT INTO favorites (item_type, title, summary, data_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (item_type, title, summary, json.dumps(data), now_str))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_favorites(item_type: Optional[str] = None, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all favorites or filtered by item_type ('recipe' or 'workout')."""
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        if item_type and item_type.lower() != "all":
            cursor.execute(
                "SELECT * FROM favorites WHERE item_type = ? ORDER BY id DESC",
                (item_type.lower(),)
            )
        else:
            cursor.execute("SELECT * FROM favorites ORDER BY id DESC")
        
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "item_type": r["item_type"],
                "title": r["title"],
                "summary": r["summary"],
                "data": json.loads(r["data_json"]),
                "created_at": r["created_at"]
            })
        return results
    finally:
        conn.close()


def delete_favorite(item_id: int, db_path: Path = DB_PATH) -> bool:
    """Deletes a single favorite by its primary key ID."""
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM favorites WHERE id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def clear_all_favorites(db_path: Path = DB_PATH) -> int:
    """Clears all saved favorites. Returns count of deleted items."""
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM favorites")
        count = cursor.rowcount
        conn.commit()
        return count
    finally:
        conn.close()


def get_favorites_counts(db_path: Path = DB_PATH) -> Dict[str, int]:
    """Returns counts of saved recipes and workouts."""
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT item_type, COUNT(*) FROM favorites GROUP BY item_type")
        rows = cursor.fetchall()
        counts = {"recipe": 0, "workout": 0, "total": 0}
        for item_type, cnt in rows:
            counts[item_type] = cnt
            counts["total"] += cnt
        return counts
    finally:
        conn.close()

