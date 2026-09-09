import os
import json
from modules.db_manager import get_recap_desk_review
from modules.export_generator import generate_lha_word

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'laporan_review_per_rs')

os.makedirs(OUTPUT_DIR, exist_ok=True)
dr_data = get_recap_desk_review()

rs_cases = [r for r in dr_data if r['kode_rs'] == '1275655']
rs_name = 'RSU H. ADAM MALIK'

formatted_cases = []
for c in rs_cases:
    try:
        fd = json.loads(c.get('tindakan_reviewer') or '{}')
    except Exception:
        fd = {}
    c_dict = dict(c)
    c_dict['knavp_skor'] = fd.get('knavp_skor', c.get('knavp_skor', 0)) or 0
    try:
                c_dict['triggered_rules'] = __import__('json').loads(c.get('triggered_rules_json') or '[]')
            except:
                c_dict['triggered_rules'] = []
    c_dict['tingkat_risiko'] = fd.get('tingkat_risiko', c.get('tingkat_risiko', '-')) or '-'
    c_dict['keputusan_sistem'] = fd.get('keputusan_sistem', fd.get('keputusan', c.get('keputusan_sistem', '-')))
    c_dict['jumlah_beda_dual_coding'] = fd.get('jumlah_beda_dual_coding', c.get('jumlah_beda_dual_coding', 0)) or 0
    formatted_cases.append(c_dict)

safe_name = rs_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
filename = f"Laporan_Hasil_Review_Koding_1275655_{safe_name}.docx"
filepath = os.path.join(OUTPUT_DIR, filename)

generate_lha_word('1275655', rs_name, formatted_cases, filepath)
print(f"Berhasil men-generate Word khusus untuk {rs_name}: {filepath}")
