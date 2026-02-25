# src/utils/schema_loader.py

import sqlite3
from typing import Dict


class SchemaLoader:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cached_schema = None

    def load_schema(self) -> str:
        """
        Extract tables and columns from SQLite DB
        Returns formatted schema string for LLM grounding
        """

        if self._cached_schema:
            return self._cached_schema

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema_text = ""

        for table in tables:
            table_name = table[0]

            # Skip SQLite internal tables
            if table_name.startswith("sqlite_"):
                continue

            schema_text += f"\nTable: {table_name}\nColumns:\n"

            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            for col in columns:
                col_name = col[1]
                col_type = col[2]
                schema_text += f"- {col_name} ({col_type})\n"

        conn.close()

        self._cached_schema = schema_text.strip()
        return self._cached_schema