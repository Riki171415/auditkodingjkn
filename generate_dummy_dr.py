import os
import sqlite3
import json
import random
import datetime
import sys

# Change working directory to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_loader import get_hospital_list, load_individual_data
from modules.rule_engine import validate_case
from modules.db_manager import save_kkr_dr01, get_audit_db

REVIEWER_NAMES = [
    "Riki Permana Putra",
    "Yosi Prasetyo",
    "dr. Yusuf",
    "dr. Dyah Armi",
    "dr. Karlina",
    "Annisa Clara",
    "Deny Wahyu",
    "Wahyu Ramadhan"
]

def generate_random_date():
    start_date = datetime.date(2026, 5, 18)
    end_date = datetime.date(2026, 5, 29)
    days_between_dates = (end_date - start_date).days
    random_days = random.randrange(days_between_dates + 1)
    random_date = start_date + datetime.timedelta(days=random_days)
    return f"{random_date.isoformat()} {random.randint(8,16):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

def generate_dummy_data():
    print("Starting Dummy KKR-DR01 Data Generation...")
    
    hospitals = get_hospital_list(sample_only=True)
    if not hospitals:
        print("No hospitals found in sample!")
        return
        
    print(f"Loaded {len(hospitals)} sample hospitals.")
    
    df_ind = load_individual_data()
    if df_ind is None or df_ind.empty:
        print("No individual data found!")
        return

    total_generated = 0
    conn = get_audit_db()

    for idx, hs in enumerate(hospitals):
        kode_rs = hs['kode_rs']
        print(f"[{idx+1}/{len(hospitals)}] Processing RS {kode_rs} - {hs['nama_rs']}...")
        
        rs_data = df_ind[df_ind['kode_rs'] == str(kode_rs)].copy()
        rs_data['rules'] = rs_data.apply(lambda row: validate_case(row.to_dict()), axis=1)
        cases_with_findings = rs_data[rs_data['rules'].apply(lambda x: len(x) > 0)]
        target_cases = cases_with_findings.head(50).to_dict('records')
        
        for case in target_cases:
            rules = case['rules']
            sep = case['sep']
            
            priorities = [r.get('priority', 'Low') for r in rules]
            has_high = 'Kritis' in priorities or 'Tinggi' in priorities
            
            if has_high:
                keputusan = 'Direkomendasikan On-Site Audit'
                rekomendasi = 'Kasus ini memiliki temuan kritis/tinggi dan memerlukan investigasi rekam medis fisik.'
            else:
                keputusan = 'Perlu Monitoring'
                rekomendasi = 'Terdapat temuan administrasi/koding ringan, perlu pengawasan pada klaim bulan berikutnya.'
                
            reviewer = random.choice(REVIEWER_NAMES)
            tgl = generate_random_date()
            
            data = {
                'kode_rs': str(kode_rs),
                'reviewer_name': reviewer,
                'kesesuaian_dokumen': 'Lengkap',
                'kesesuaian_medis': 'Ada Ketidaksesuaian' if has_high else 'Kurang Jelas',
                'analisis_reviewer': f'Di-generate otomatis oleh sistem berdasarkan {len(rules)} temuan (Auto-Logic).',
                'keputusan': keputusan,
                'rekomendasi_lanjut': rekomendasi
            }
            
            save_kkr_dr01(sep, data)
            
            c = conn.cursor()
            c.execute("UPDATE kkr_dr01 SET updated_at = ? WHERE sep = ?", (tgl, sep))
            conn.commit()
            
            total_generated += 1
            
    conn.close()
    print(f"SUCCESS! {total_generated} dummy KKR-DR01 records have been generated and saved to the database.")

if __name__ == '__main__':
    generate_dummy_data()
