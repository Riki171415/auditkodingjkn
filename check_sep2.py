import sqlite3, json
c = sqlite3.connect('audit.db')
r = c.execute("SELECT triggered_rules_json FROM kkr_dr01 WHERE sep='0201R0011125V014938'").fetchone()
if r:
    print(r[0])
