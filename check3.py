import sqlite3, json
conn = sqlite3.connect('d:/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/audit.db')
cur = conn.cursor()
cur.execute('SELECT triggered_rules_json FROM kkr_dr01 WHERE kode_rs="1275655" AND triggered_rules_json IS NOT NULL')
rows = cur.fetchall()
print([r[0] for r in rows if r[0] and r[0] != '[]'][:5])
