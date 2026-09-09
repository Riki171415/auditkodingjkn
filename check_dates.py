import sqlite3, os, datetime
c=sqlite3.connect('audit.db')
r=c.execute("SELECT updated_at FROM kkr_dr01 WHERE sep='0201R0011125V014938'").fetchone()
print('DB updated:', r[0] if r else None)
from modules.output_catalog import find_kkr
pdf_path = find_kkr('0201R0011125V014938')
print('PDF updated:', datetime.datetime.fromtimestamp(os.path.getmtime(pdf_path)) if pdf_path else 'No PDF')
