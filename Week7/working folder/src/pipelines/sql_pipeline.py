# src/pipelines/sql_pipeline.py

from src.utils.schema_loader import SchemaLoader
from src.utils.query_validator import QueryValidator
from src.utils.safe_executor import SafeExecutor
from src.generator.sql_generator import SQLGenerator


class SQLPipeline:
    def __init__(self, db_path: str):
        self.schema_loader = SchemaLoader(db_path)
        self.validator = QueryValidator()
        self.executor = SafeExecutor(db_path)
        self.generator = SQLGenerator()

    def run(self, question: str) -> str:

        # Step 1: Load schema
        schema = self.schema_loader.load_schema()

        # Step 2: Generate SQL
        sql = self.generator.generate(question, schema)

        # Step 3: Validate SQL
        sql = self.validator.validate(sql)

        # Step 4: Execute
        result = self.executor.execute(sql)

        # Step 5: Correction loop (max 2 retries)
        retry_count = 0
        while not result["success"] and retry_count < 2:
            sql = self.generator.correct(
                question,
                schema,
                sql,
                result["error"]
            )
            sql = self.validator.validate(sql)
            result = self.executor.execute(sql)
            retry_count += 1

        if not result["success"]:
            return f"Query failed: {result['error']}"

        # Step 6: Summarize result
        return self._summarize(question, result)

    def _summarize(self, question: str, result: dict) -> str:
        """
        Simple table summarizer (LLM optional upgrade later)
        """

        columns = result["columns"]
        rows = result["rows"]

        if not rows:
            return "No results found."

        summary = f"Query Results for: {question}\n\n"

        for row in rows:
            row_text = ", ".join(
                f"{col}: {val}" for col, val in zip(columns, row)
            )
            summary += row_text + "\n"

        return summary.strip()