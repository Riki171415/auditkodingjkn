import sys
from pathlib import Path
BASE = Path('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app')
sys.path.insert(0, str(BASE))
from modules.report_excel import export_reports
out_dir = 'outputs/hasil_akhir_20260907'
print('Generating Excel Nasional...')
export_reports(per_rs=False, out_dir=out_dir)
print('Generating Excel per RS...')
export_reports(per_rs=True, out_dir=out_dir)
print('Done!')
