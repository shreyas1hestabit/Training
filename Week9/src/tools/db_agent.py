# import sqlite3

# def query_database(sql_query: str) -> str:
#     """Executes a SQL query against business.db."""
#     try:
#         conn = sqlite3.connect("business.db")
#         cursor = conn.cursor()
#         cursor.execute(sql_query)
#         rows = cursor.fetchall()
#         conn.close()
#         return str(rows) if rows else "Success: No rows returned."
#     except Exception as e:
#         return f"SQL Error: {str(e)}"

# db_tool = {
#     "name": "db_querier",
#     "description": "Run SQL queries to fetch data from the SQLite database.",
#     "func": query_database
# }

import sqlite3


def query_database(sql_query: str) -> str:
    """Executes a SQL query against business.db."""
    try:
        conn = sqlite3.connect("business.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()
        if rows:
            # Format rows as readable table string
            return "\n".join(str(row) for row in rows)
        return "Success: Query executed. No rows returned."
    except Exception as e:
        return f"SQL Error: {str(e)}"


db_tool = {
    "name": "db_querier",
    "description": "Run SQL queries to fetch data from the SQLite database.",
    "func": query_database,
}