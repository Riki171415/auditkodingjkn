import sqlite3
import os

if os.path.exists('individual_data.db'):
    conn = sqlite3.connect('individual_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"Table: {table[0]}")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print([c[1] for c in columns])
else:
    print("individual_data.db not found")
