"""
Generate dummy KKR-DR01 data menggunakan logika KNAVP terbaru:
- Bobot per rule (High=3, Medium=2, Low=1)
- Dual coding discrepancy check (INA-CBG vs iDRG, dengan aturan prefix & +modifier)
- CCL dari digit terakhir idrg_code
- Rekomendasi berdasarkan total skor (0-3=Rendah, 4-7=Sedang, >=8=Tinggi)
"""
import os
import json
import random
import datetime
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_loader import get_hospital_list, load_individual_data
from modules.rule_engine import (
    validate_case,
    calculate_knavp_score,
    determine_recommendation_knavp,
    check_dual_coding_discrepancy,
)
from modules.db_manager import save_kkr_dr01, get_audit_db

# ── Konfigurasi ──────────────────────────────────────────────────────────────
REVIEWER_NAMES = [
    "Riki Permana Putra",
    "Yosi Prasetyo",
    "dr. Yusuf",
    "dr. Dyah Armi",
    "dr. Karlina",
    "Annisa Clara",
    "Deny Wahyu",
    "Wahyu Ramadhan",
]

CCL_MAP = {
    '0': 'No CC', '1': 'Mild CC', '2': 'Moderate CC',
    '3': 'Severe CC', '4': 'Catastrophic CC', '9': 'Merge CC',
}


def _parse_ccl(idrg_code):
    if not idrg_code:
        return '-'
    last = str(idrg_code).strip()[-1]
    return CCL_MAP.get(last, '-')


def generate_random_date():
    start_date = datetime.date(2026, 5, 18)
    end_date   = datetime.date(2026, 5, 29)
    random_days = random.randrange((end_date - start_date).days + 1)
    random_date = start_date + datetime.timedelta(days=random_days)
    return (f"{random_date.isoformat()} "
            f"{random.randint(8, 16):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}")


def generate_dummy_data():
    print("=" * 60)
    print("Generating Dummy KKR-DR01 Data (KNAVP v2 Logic)...")
    print("=" * 60)

    hospitals = get_hospital_list(sample_only=True)
    if not hospitals:
        print("ERROR: No hospitals found in sample!")
        return

    print(f"Loaded {len(hospitals)} sample hospitals.")

    df_ind = load_individual_data()
    if df_ind is None or df_ind.empty:
        print("ERROR: No individual data found!")
        return

    # Reset existing data
    conn = get_audit_db()
    c = conn.cursor()
    c.execute("DELETE FROM kkr_dr01")
    conn.commit()
    conn.close()
    print("Cleared existing kkr_dr01 records.")

    total_generated = 0
    total_onsite    = 0
    total_sampling  = 0
    total_monitor   = 0

    conn = get_audit_db()

    for idx, hs in enumerate(hospitals):
        kode_rs  = hs['kode_rs']
        nama_rs  = hs.get('nama_rs', kode_rs)
        rs_data  = df_ind[df_ind['kode_rs'] == str(kode_rs)].copy()

        if rs_data.empty:
            print(f"  [{idx+1}] {kode_rs}: No data, skip.")
            continue

        print(f"\n[{idx+1}/{len(hospitals)}] {kode_rs} - {nama_rs} ({len(rs_data)} kasus)")

        # Validasi semua kasus
        rs_data['_rules']     = rs_data.apply(lambda r: validate_case(r.to_dict()), axis=1)
        rs_data['_skor']      = rs_data['_rules'].apply(calculate_knavp_score)

        # Ambil 50 kasus pertama secara natural agar hasil LHA benar-benar
        # mencerminkan output dari logic audit (tanpa rekayasa rasio).
        target_cases = rs_data.head(50).to_dict('records')

        for case in target_cases:
            sep             = case['sep']
            triggered_rules = case.get('_rules', [])
            total_skor      = case.get('_skor', 0) or calculate_knavp_score(triggered_rules)

            # Dual coding discrepancy
            try:
                dc_result         = check_dual_coding_discrepancy(case)
                jumlah_beda_total = dc_result.get('jumlah_beda_total', 0)
            except Exception:
                dc_result         = {}
                jumlah_beda_total = 0

            # KNAVP recommendation
            knavp_result = determine_recommendation_knavp(total_skor, jumlah_beda_total)
            tingkat      = knavp_result['tingkat_risiko']
            keputusan    = knavp_result['keputusan_sistem']

            # CCL
            ccl_label = _parse_ccl(case.get('idrg_code'))

            # Statistik output
            if 'On-Site' in keputusan:
                total_onsite += 1
            elif 'Sampling' in keputusan:
                total_sampling += 1
            else:
                total_monitor += 1

            reviewer = random.choice(REVIEWER_NAMES)
            tgl      = generate_random_date()

            keputusan_sistem_val = knavp_result['keputusan_sistem']
            if 'Tidak perlu tindak lanjut' in keputusan_sistem_val:
                analisis = ("Berdasarkan hasil validasi otomatis sistem (KNAVP), tidak ditemukan potensi "
                            "ketidaksesuaian koding. Kode INA-CBG dan iDRG juga konsisten. "
                            "Klaim dinilai aman.")
                keputusan_reviewer = "Sesuai (Terbukti Valid)"
            else:
                analisis = (
                    f"Berdasarkan hasil validasi KNAVP, terdapat {len(triggered_rules)} rule terindikasi "
                    f"dengan total skor {total_skor}. "
                    f"Terdapat {jumlah_beda_total} perbedaan kode pada dual coding (INA-CBG vs iDRG). "
                    f"Tingkat risiko: {tingkat}. Rekomendasi: {keputusan_sistem_val}."
                )
                keputusan_reviewer = "Tidak Sesuai (Terindikasi Fraud/Error)"

            data = {
                'kode_rs':                 str(kode_rs),
                'nama_rs':                 nama_rs,
                'reviewer_name':           reviewer,
                # KNAVP fields (baru)
                'knavp_skor':              total_skor,
                'tingkat_risiko':          tingkat,
                'keputusan_sistem':        keputusan,
                'jumlah_beda_dual_coding': jumlah_beda_total,
                'ccl_label':               ccl_label,
                # Lama (kompatibilitas)
                'analisis_reviewer':       analisis,
                'keputusan_reviewer':      keputusan_reviewer,
                'keputusan':              keputusan,
                'tingkat_keyakinan':      'Tinggi (Berdasarkan KNAVP Otomatis)',
                'alasan_keputusan':       (
                    f"Total Skor KNAVP: {total_skor} | Tingkat Risiko: {tingkat} | "
                    f"Perbedaan Dual Coding: {jumlah_beda_total}"
                ),
                'rekomendasi_lanjut':     keputusan,
                'kategori_perubahan_tarif': ('Tidak Berubah' if len(triggered_rules) == 0 else 'Turun'),
            }

            save_kkr_dr01(sep, data)

            # Backdate timestamp
            c = conn.cursor()
            c.execute("UPDATE kkr_dr01 SET updated_at = ? WHERE sep = ?", (tgl, sep))
            conn.commit()

            total_generated += 1

        print(f"  -> {len(target_cases)} kasus diproses.")

    conn.close()

    print("\n" + "=" * 60)
    print(f"SELESAI! {total_generated} record KKR-DR01 berhasil dibuat.")
    print(f"  • Rekomendasi On-Site Audit : {total_onsite}")
    print(f"  • Rekomendasi Audit Sampling: {total_sampling}")
    print(f"  • Rekomendasi Monitoring    : {total_monitor}")
    print("=" * 60)


if __name__ == '__main__':
    generate_dummy_data()
