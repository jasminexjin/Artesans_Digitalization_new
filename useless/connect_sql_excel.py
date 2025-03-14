import sqlite3
import pandas as pd
import time

DB_PATH = "medical_supplies.db"
EXCEL_PATH = "test.xlsx"

def update_excel():
    """Fetch data from SQLite and update the Excel file."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM supplies", conn)
    conn.close()

    df.to_excel(EXCEL_PATH, index=False, engine='openpyxl')
    print(f"Excel updated at {time.strftime('%H:%M:%S')}")


def watch_database(interval=5):
    """Continuously check the SQLite database and update Excel when changes occur."""
    prev_count = -1
    while True:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM supplies")
        row_count = cursor.fetchone()[0]
        conn.close()

        if row_count != prev_count:  # If data changes, update Excel
            update_excel()
            prev_count = row_count

        time.sleep(interval)  # Check every 5 seconds


if __name__ == "__main__":
    watch_database()
