import sqlite3
import pandas as pd
import os

DATA_DIR = ""

def query_database(db_name: str, sql_query: str) -> str:
    """Run a SQL query on a database file and return results or confirmation."""
    path = os.path.join(DATA_DIR, os.path.basename(db_name))
    try:
        conn = sqlite3.connect(path)
        query_lower = sql_query.strip().lower()
        
        if query_lower.startswith("select") or "pragma" in query_lower:
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            return df.to_string() if not df.empty else "No results found."
        else:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            conn.commit()
            changes = conn.total_changes
            conn.close()
            return f"SUCCESS: {changes} rows modified."
    except Exception as e:
        return f"DB Error: {str(e)}"