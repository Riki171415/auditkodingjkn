
import sys
sys.path.append('.')
from modules.db_manager import get_recap_desk_review
import json

data = get_recap_desk_review()
rs_stats = {}
for r in data:
    kode_rs = r.get('kode_rs')
    nama_rs = r.get('nama_rs')
    if kode_rs not in rs_stats:
        rs_stats[kode_rs] = {'nama': nama_rs, 'total': 0, 'lolos': 0, 'onsite': 0}
    rs_stats[kode_rs]['total'] += 1
    
    try:
        fd = json.loads(r.get('tindakan_reviewer') or '{}')
    except:
        fd = {}
    kep_sis = fd.get('keputusan_sistem', 'Tidak diperlukan tindak lanjut')
    kep = fd.get('keputusan') or kep_sis
    kep_str = str(kep)
    if 'Fraud' in kep_str or 'Tidak Sesuai' in kep_str or 'On-Site' in kep_str:
        rs_stats[kode_rs]['onsite'] += 1
    elif 'Sesuai' in kep_str or 'Valid' in kep_str or 'Tidak perlu' in kep_str or 'Tidak diperlukan' in kep_str:
        rs_stats[kode_rs]['lolos'] += 1

sorted_rs = sorted(rs_stats.values(), key=lambda x: x['total'], reverse=True)
import pickle
with open('rs_stats_dump.pkl', 'wb') as f:
    pickle.dump(sorted_rs, f)

