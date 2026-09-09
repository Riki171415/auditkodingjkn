import sqlite3, json
c = sqlite3.connect('audit.db')
r = c.execute("SELECT * FROM kkr_dr01 WHERE sep='0201R0011125V014938'").fetchone()
if r:
    print(json.dumps(json.loads(r[3]), indent=2))
else:
    print('Not found')
