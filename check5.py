import sqlite3, json
conn = sqlite3.connect('d:/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/audit.db')
cur = conn.cursor()
cur.execute('SELECT tindakan_reviewer FROM kkr_dr01 WHERE kode_rs="1275655"')
rows = cur.fetchall()
count = 0
total = 0
for r in rows:
  if r[0]:
    try:
      fd = json.loads(r[0])
      diff = int(fd.get('jumlah_beda_dual_coding', 0) or 0)
      if diff > 0:
        count += 1
        total += diff
    except:
      pass
print(f'Count: {count}, Total Diff: {total}')
