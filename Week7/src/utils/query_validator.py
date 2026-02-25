# src/utils/query_validator.py

import re


class QueryValidator:
    FORBIDDEN_KEYWORDS = [
        "DROP", "DELETE", "UPDATE", "INSERT",
        "ALTER", "TRUNCATE", "ATTACH", "PRAGMA"
    ]

    def validate(self, sql: str) -> str:
        """
        Ensure SQL is safe to execute.
        """

        sql_upper = sql.upper().strip()

        # Only allow SELECT or WITH (CTE)
        if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
            raise ValueError("Only SELECT queries are allowed.")

        # Block dangerous keywords
        for keyword in self.FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{keyword}\b", sql_upper):
                raise ValueError(f"Forbidden keyword detected: {keyword}")

        # Block multiple statements
        if ";" in sql.strip()[:-1]:
            raise ValueError("Multiple SQL statements not allowed.")

        return sql.strip()