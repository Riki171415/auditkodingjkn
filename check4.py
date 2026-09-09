import sqlite3, json, collections
conn = sqlite3.connect('d:/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/audit.db')
cur = conn.cursor()
cur.execute('SELECT triggered_rules_json FROM kkr_dr01 WHERE kode_rs="1275655"')
rows = cur.fetchall()
groups = collections.defaultdict(int)
for r in rows:
  if r[0]:
    try:
      rules = json.loads(r[0])
      for rule in rules:
        groups[rule.get('kelompok_rule', 'Lainnya')] += 1
    except:
      pass
print('Findings:', dict(groups))
print('Total:', sum(groups.values()))
