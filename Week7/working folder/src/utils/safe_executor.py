# src/utils/safe_executor.py

import sqlite3
from typing import List, Tuple, Dict


class SafeExecutor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def execute(self, sql: str) -> Dict:
        """
        Executes SQL safely in read-only mode.
        Returns dict with columns + rows.
        """

        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            conn.close()

            return {
                "success": True,
                "columns": columns,
                "rows": rows
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }