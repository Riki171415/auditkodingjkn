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

    # Delete existing KKR-DR01 to start fresh
    conn = get_audit_db()
    c = conn.cursor()
    c.execute("DELETE FROM kkr_dr01")
    conn.commit()
    conn.close()

    total_generated = 0
    conn = get_audit_db()

    for idx, hs in enumerate(hospitals):
        kode_rs = hs['kode_rs']
        print(f"[{idx+1}/{len(hospitals)}] Processing RS {kode_rs} - {hs['nama_rs']}...")
        
        rs_data = df_ind[df_ind['kode_rs'] == str(kode_rs)].copy()
        rs_data['rules'] = rs_data.apply(lambda row: validate_case(row.to_dict()), axis=1)
        # Filter cases with audit findings (rules > 0)
        cases_with_findings = rs_data[rs_data['rules'].apply(lambda x: len(x) > 0)]
        cases_clean = rs_data[rs_data['rules'].apply(lambda x: len(x) == 0)]
        
        target_cases = cases_with_findings.head(50).to_dict('records')
        
        # If less than 50, pad with clean cases
        if len(target_cases) < 50:
            shortfall = 50 - len(target_cases)
            padding_cases = cases_clean.head(shortfall).to_dict('records')
            target_cases.extend(padding_cases)
        
        for case in target_cases:
            rules = case.get('rules', [])
            sep = case['sep']
            
            if len(rules) == 0:
                keputusan = 'Sesuai (Terbukti Valid)'
                rekomendasi = 'Tidak ada temuan. Klaim sesuai.'
                has_high = False
            else:
                priorities = [r.get('priority', 'Low') for r in rules]
                has_high = 'High' in priorities or 'Medium' in priorities
                
                keputusan = 'Tidak Sesuai (Terindikasi Fraud/Error)'
                if has_high:
                    rekomendasi = 'On-Site Audit'
                else:
                    rekomendasi = 'Monitoring / Pembinaan'
                
            reviewer = random.choice(REVIEWER_NAMES)
            tgl = generate_random_date()
            
            data = {
                'kode_rs': str(kode_rs),
                'reviewer_name': reviewer,
                'kesesuaian_dokumen': 'Lengkap',
                'kesesuaian_medis': 'Ada Ketidaksesuaian' if len(rules) > 0 else 'Sesuai Medis',
                'analisis_reviewer': f'Di-generate otomatis oleh sistem berdasarkan {len(rules)} temuan (Auto-Logic).',
                'keputusan_reviewer': keputusan,
                'rekomendasi_lanjut': rekomendasi,
                'kategori_perubahan_tarif': 'Tidak Berubah' if len(rules) == 0 else 'Turun'
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
