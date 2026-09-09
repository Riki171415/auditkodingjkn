"""inspect_knavp.py — Inspeksi format rule_id KNAVP di database"""
import sqlite3, json, os

DB_CANDIDATES = [
    "audit.db", "data.db", "database.db",
    "d:/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/audit.db",
    "d:/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/data.db",
]

conn = None
for db in DB_CANDIDATES:
    if os.path.exists(db):
        print(f"Found DB: {db}")
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        break

if not conn:
    print("DB tidak ditemukan!")
    exit()

cur = conn.cursor()

# Cek semua tabel
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(f"\nTabel: {tables}")

# Cari kolom yang mengandung 'rule' atau 'knavp'
for tbl in tables:
    cur.execute(f"PRAGMA table_info({tbl})")
    cols = [r[1] for r in cur.fetchall()]
    rule_cols = [c for c in cols if 'rule' in c.lower() or 'knavp' in c.lower() or 'alert' in c.lower()]
    if rule_cols:
        print(f"\n  Tabel [{tbl}] -- kolom rule/alert: {rule_cols}")

        for col in rule_cols:
            cur.execute(f"SELECT {col} FROM {tbl} WHERE {col} IS NOT NULL AND {col} != '' AND {col} != '[]' LIMIT 3")
            rows = cur.fetchall()
            for r in rows:
                val = r[0]
                print(f"    Sample [{col}]: {str(val)[:200]}")
                # Coba parse sebagai JSON
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list) and parsed:
                        first = parsed[0]
                        print(f"    --> Keys: {list(first.keys()) if isinstance(first, dict) else type(first)}")
                        if isinstance(first, dict):
                            for k, v in first.items():
                                print(f"       {k}: {str(v)[:80]}")
                except:
                    pass
                break

conn.close()
