import sqlite3
import json
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).parent / "long_term.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS facts (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    key       TEXT NOT NULL,
    value     TEXT NOT NULL,
    source    TEXT,                  -- which conversation turn created this
    created   TEXT NOT NULL,
    updated   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS episodes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    summary   TEXT NOT NULL,         -- LLM-generated summary of a conversation
    raw       TEXT,                  -- optional: full raw transcript
    created   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recall_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    query       TEXT NOT NULL,
    memory_type TEXT NOT NULL,       -- "fact" | "episode" | "vector"
    memory_id   INTEGER,
    recalled_at TEXT NOT NULL
);
"""

class LongTermMemory:
    """
    SQLite-backed persistent memory.

    All three memory types (facts, episodes, recall_log) live in a single
    `long_term.db` file next to this module.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def save_fact(self, key: str, value: str, source: str = "") -> None:
        """Insert or update a fact. One canonical value per key."""
        now = datetime.now().isoformat()
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM facts WHERE key = ?", (key,)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE facts SET value=?, source=?, updated=? WHERE key=?",
                    (value, source, now, key)
                )
            else:
                conn.execute(
                    "INSERT INTO facts (key, value, source, created, updated) VALUES (?,?,?,?,?)",
                    (key, value, source, now, now)
                )

    def get_fact(self, key: str) -> str | None:
        """Retrieve a single fact by key."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM facts WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else None

    def get_all_facts(self) -> dict:
        """Return all facts as a plain dict."""
        with self._connect() as conn:
            rows = conn.execute("SELECT key, value FROM facts").fetchall()
            return {r["key"]: r["value"] for r in rows}

    def search_facts(self, keyword: str) -> list[dict]:
        """Full-text search over fact keys and values."""
        like = f"%{keyword}%"
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT key, value, updated FROM facts WHERE key LIKE ? OR value LIKE ?",
                (like, like)
            ).fetchall()
            return [dict(r) for r in rows]

    def delete_fact(self, key: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM facts WHERE key = ?", (key,))

    def save_episode(self, summary: str, raw: str = "") -> int:
        """Store a conversation summary. Returns the new episode id."""
        now = datetime.now().isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO episodes (summary, raw, created) VALUES (?,?,?)",
                (summary, raw, now)
            )
            return cur.lastrowid

    def get_recent_episodes(self, n: int = 5) -> list[dict]:
        """Return the n most recent episode summaries."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, summary, created FROM episodes ORDER BY id DESC LIMIT ?",
                (n,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_all_episodes(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, summary, created FROM episodes ORDER BY id DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def log_recall(self, query: str, memory_type: str, memory_id: int | None = None) -> None:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO recall_log (query, memory_type, memory_id, recalled_at) VALUES (?,?,?,?)",
                (query, memory_type, memory_id, now)
            )

    def get_recall_log(self, limit: int = 20) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM recall_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def stats(self) -> dict:
        """Return counts for each table."""
        with self._connect() as conn:
            facts    = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
            episodes = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
            recalls  = conn.execute("SELECT COUNT(*) FROM recall_log").fetchone()[0]
        return {"facts": facts, "episodes": episodes, "recall_log": recalls}

    def __repr__(self) -> str:
        s = self.stats()
        return (f"LongTermMemory(db='{self.db_path.name}', "
                f"facts={s['facts']}, episodes={s['episodes']})")