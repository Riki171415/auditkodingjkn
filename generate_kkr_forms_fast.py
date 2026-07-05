"""
Bulk generate KKR-DR01 PDF (multiprocessing — fast mode).
Menggunakan logika dual coding discrepancy + KNAVP v2.
"""
import os
import json
import time
import sys
from multiprocessing import Pool, cpu_count

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'kkr_forms')

CCL_MAP = {'0': 'No CC', '1': 'Mild CC', '2': 'Moderate CC',
           '3': 'Severe CC', '4': 'Catastrophic CC', '9': 'Merge CC'}


def process_case(row):
    """
    Worker function — dijalankan tiap proses paralel.
    Menghasilkan PDF per kasus KKR-DR01.
    """
    from modules.data_loader import get_case_by_sep
    from modules.rule_engine import (
        validate_case, calculate_knavp_score,
        determine_recommendation_knavp, check_dual_coding_discrepancy,
    )
    from modules.export_generator import export_kkr_dr01_pdf

    sep  = row['sep']
    case = get_case_by_sep(sep)
    if not case:
        return False, sep, "Case not found"

    triggered_rules = validate_case(case)
    total_skor      = calculate_knavp_score(triggered_rules)

    try:
        dc          = check_dual_coding_discrepancy(case)
        jumlah_beda = dc.get('jumlah_beda_total', 0)
    except Exception:
        dc          = {}
        jumlah_beda = 0

    knavp     = determine_recommendation_knavp(total_skor, jumlah_beda)
    idrg_raw  = str(case.get('idrg_code', '') or '')
    ccl_digit = idrg_raw[-1] if idrg_raw else ''
    ccl_label = CCL_MAP.get(ccl_digit, '-')

    try:
        form_data = json.loads(row.get('tindakan_reviewer') or '{}')
    except Exception:
        form_data = {}

    kkr_data = {
        'sep':              sep,
        'kode_rs':          case.get('kode_rs'),
        'nama_rs':          case.get('nama_rs'),
        'inacbg':           case.get('inacbg'),
        'case':             case,
        'triggered_rules':  triggered_rules,
        'total_triggered':  len(triggered_rules),
        # KNAVP v2
        'knavp_skor':              total_skor,
        'tingkat_risiko':          knavp['tingkat_risiko'],
        'keputusan_sistem':        knavp['keputusan_sistem'],
        'jumlah_beda_dual_coding': jumlah_beda,
        'ccl_label':               ccl_label,
        'ccl_digit':               ccl_digit,
        'dual_coding':             dc,
        'knavp':                   knavp,
    }
    kkr_data.update(form_data)

    if row.get('reviewer_name'):
        kkr_data['reviewer_name'] = row['reviewer_name']

    if row.get('updated_at'):
        from datetime import datetime
        try:
            dt = datetime.strptime(str(row['updated_at']).split('.')[0], '%Y-%m-%d %H:%M:%S')
            kkr_data['tanggal_review'] = dt.strftime('%d/%m/%Y')
        except Exception:
            kkr_data['tanggal_review'] = str(row['updated_at']).split(' ')[0]

    validate_data = {'triggered_rules': triggered_rules}

    try:
        pdf_bytes = export_kkr_dr01_pdf(kkr_data, validate_data)

        rs_code  = str(case.get('kode_rs', 'UNKNOWN'))
        rs_name  = str(case.get('nama_rs', 'RS')).replace(' ', '_').replace('/', '_')[:40]
        rs_dir   = os.path.join(OUTPUT_DIR, f"{rs_code}_{rs_name}")
        os.makedirs(rs_dir, exist_ok=True)

        sep_safe = str(sep).replace('/', '_').replace('\\', '_')[:20]
        out_path = os.path.join(rs_dir, f"KKR-DR01_{sep_safe}.pdf")

        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)

        return True, sep, None
    except Exception as e:
        return False, sep, str(e)


if __name__ == '__main__':
    from modules.db_manager import get_recap_desk_review
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dr_data = get_recap_desk_review()
    print(f"Starting FAST Bulk Generation: {len(dr_data)} KKR-DR01 Forms (PDF)...")
    print(f"Output: {OUTPUT_DIR}")

    start_time = time.time()
    cores = min(cpu_count(), 8)  # cap at 8 untuk hindari memory overload
    print(f"Using {cores} CPU cores...\n")

    with Pool(cores) as p:
        results = p.map(process_case, dr_data)

    success = sum(1 for r in results if r[0])
    failed  = [(r[1], r[2]) for r in results if not r[0]]

    elapsed = time.time() - start_time
    print(f"\nSELESAI!")
    print(f"  Berhasil: {success} file")
    print(f"  Gagal   : {len(failed)} file")
    print(f"  Waktu   : {elapsed:.1f} detik")

    if failed:
        print("\nDaftar kegagalan:")
        for sep, err in failed[:10]:
            print(f"  • {sep}: {err}")
        if len(failed) > 10:
            print(f"  ... dan {len(failed)-10} kasus lainnya.")
