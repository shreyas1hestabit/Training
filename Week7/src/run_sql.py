from dotenv import load_dotenv
import os

load_dotenv()

from src.pipelines.sql_pipeline import SQLPipeline


def main():
    db_path = "src/data/cleaned/database.db"  # your SQLite DB file

    pipeline = SQLPipeline(db_path)

    while True:
        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        answer = pipeline.run(question)
        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()