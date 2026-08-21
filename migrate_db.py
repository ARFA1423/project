import sqlite3
import os

db_path = "expentia.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Check if balance column exists
        cursor.execute("PRAGMA table_info(accounts)")
        columns = [row[1] for row in cursor.fetchall()]
        if "balance" in columns and "initial_balance" not in columns:
            print("Renaming balance to initial_balance...")
            cursor.execute("ALTER TABLE accounts RENAME COLUMN balance TO initial_balance")
            conn.commit()
            print("Done!")
        else:
            print("No migration needed.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("Database file not found.")
