import pandas as pd
import sqlite3


def convert_csv_to_sqlite(csv_path: str, db_path: str, table_name: str):
    # Load CSV
    df = pd.read_csv(csv_path)

    # Create SQLite connection
    conn = sqlite3.connect(db_path)

    # Write to database
    df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.close()

    print(f"CSV converted to SQLite table '{table_name}' successfully.")


if __name__ == "__main__":
    convert_csv_to_sqlite(
        csv_path="src/data/raw/database/products-100.csv",      # your CSV file
        db_path="src/data/cleaned/database.db",     # SQLite file
        table_name="products"         # table name inside DB
    )