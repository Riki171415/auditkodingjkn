import os
import json
from modules.db_manager import get_recap_desk_review
from modules.export_generator import generate_lha_word

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'laporan_review_per_rs')

def generate_all_lhr_word():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 60)
    print("Generating Laporan Hasil Review (LHR) Word Per Rumah Sakit...")
    print("=" * 60)

    dr_data = get_recap_desk_review()
    print(f"Total data kasus: {len(dr_data)}")

    rs_map = {}
    for row in dr_data:
        kode_rs = row['kode_rs']
        if kode_rs not in rs_map:
            rs_map[kode_rs] = {'nama_rs': row.get('nama_rs', kode_rs), 'cases': []}
        rs_map[kode_rs]['cases'].append(row)

    print(f"Ditemukan {len(rs_map)} Rumah Sakit.")

    for kode_rs, data in rs_map.items():
        rs_name = data['nama_rs']
        cases = data['cases']
        
        # Format cases agar kompatibel dengan generate_lha_word
        formatted_cases = []
        for c in cases:
            try:
                fd = json.loads(c.get('tindakan_reviewer') or '{}')
            except Exception:
                fd = {}
            
            c_dict = dict(c)
            c_dict['knavp_skor'] = fd.get('knavp_skor', c.get('knavp_skor', 0)) or 0
            c_dict['triggered_rules'] = c.get('triggered_rules', [])
            c_dict['tingkat_risiko'] = fd.get('tingkat_risiko', c.get('tingkat_risiko', '-')) or '-'
            c_dict['keputusan_sistem'] = fd.get('keputusan_sistem', fd.get('keputusan', c.get('keputusan_sistem', '-')))
            c_dict['jumlah_beda_dual_coding'] = fd.get('jumlah_beda_dual_coding', c.get('jumlah_beda_dual_coding', 0)) or 0
            formatted_cases.append(c_dict)

        safe_name = rs_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
        filename = f"Laporan_Hasil_Review_Koding_{kode_rs}_{safe_name}.docx"
        filepath = os.path.join(OUTPUT_DIR, filename)

        generate_lha_word(kode_rs, rs_name, formatted_cases, filepath)
        print(f"  -> Tersimpan: {filename}")

    print(f"\nSELESAI! Seluruh Laporan Hasil Review (LHR) Word Per RS tersimpan di: {OUTPUT_DIR}")

if __name__ == '__main__':
    generate_all_lhr_word()
