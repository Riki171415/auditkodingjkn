import sys
from pathlib import Path
import json

BASE = Path('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app')
sys.path.insert(0, str(BASE))
from modules.report_excel import export_reports

out = BASE / 'outputs' / 'laporan_final_20260831'
snap = json.loads((out / 'snapshot.json').read_text(encoding='utf-8'))
excel_dir = out / 'excel_per_rs'
excel_dir.mkdir(parents=True, exist_ok=True)
nasional_path = out / 'Laporan_Akhir_Nasional.xlsx'

# According to modules.report_excel, let's see how to call it. 
# We saw earlier it might just be export_reports() or export_reports(per_rs=False)
# But wait, looking at my previous python error, it says:
# TypeError: export_reports() takes from 0 to 1 positional arguments but 3 were given
# Ah! It doesn't take 'snapshot, dir, file'. It takes 'per_rs=False'!
