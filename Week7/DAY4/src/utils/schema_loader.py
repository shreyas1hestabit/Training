import sqlite3
from typing import Dict


class SchemaLoader:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cached_schema = None #we use this to save time and computation. if we want to access the db 10 times then the hard work of reading the databse is done only once. this stores the map in the memory

    def load_schema(self) -> str:
        """
        Extract tables and columns from SQLite DB
        Returns formatted schema string for LLM grounding
        """

        if self._cached_schema:
            return self._cached_schema

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") #every sqlite database has a hidden master table that lists everything inside it
        tables = cursor.fetchall()

        schema_text = ""

        for table in tables:
            table_name = table[0]

            # Skip SQLite internal tables
            if table_name.startswith("sqlite_"):
                continue

            schema_text += f"\nTable: {table_name}\nColumns:\n"

            cursor.execute(f"PRAGMA table_info({table_name});") #pragma is a special SQLite only command that returns metadata
            #it gives back a list of columns, their names and their types 
            columns = cursor.fetchall()

            for col in columns:
                col_name = col[1]
                col_type = col[2]
                schema_text += f"- {col_name} ({col_type})\n"

        conn.close()

        self._cached_schema = schema_text.strip()
        return self._cached_schema