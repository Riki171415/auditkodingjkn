"""
Bulk generate KKR-DR01 PDF (single-process).
Menggunakan logika dual coding discrepancy + KNAVP v2 dari rule_engine.
"""
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.db_manager import get_recap_desk_review
from modules.data_loader import get_case_by_sep
from modules.rule_engine import (
    validate_case,
    calculate_knavp_score,
    determine_recommendation_knavp,
    check_dual_coding_discrepancy,
)
from modules.export_generator import export_kkr_dr01_pdf, export_kkr_dr01_excel

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'kkr_forms')

CCL_MAP = {'0': 'No CC', '1': 'Mild CC', '2': 'Moderate CC',
           '3': 'Severe CC', '4': 'Catastrophic CC', '9': 'Merge CC'}


def _build_kkr_data(row, case, triggered_rules):
    """Assemble kkr_data dict with all KNAVP v2 fields."""
    total_skor = calculate_knavp_score(triggered_rules)

    try:
        dc = check_dual_coding_discrepancy(case)
        jumlah_beda = dc.get('jumlah_beda_total', 0)
    except Exception:
        dc = {}
        jumlah_beda = 0

    knavp = determine_recommendation_knavp(total_skor, jumlah_beda)

    idrg_raw = str(case.get('idrg_code', '') or '')
    ccl_digit = idrg_raw[-1] if idrg_raw else ''
    ccl_label = CCL_MAP.get(ccl_digit, '-')

    # Merge form_data from DB
    try:
        form_data = json.loads(row.get('tindakan_reviewer') or '{}')
    except Exception:
        form_data = {}

    kkr_data = {
        'sep':              row['sep'],
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

    return kkr_data


def bulk_generate_kkr_forms(mode='both'):
    """
    Generate KKR-DR01 forms in PDF and/or Excel.
    mode: 'pdf' | 'excel' | 'both'
    """
    print(f"Starting Bulk KKR-DR01 Generation (mode={mode})...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dr_data = get_recap_desk_review()
    print(f"Found {len(dr_data)} cases to generate.")

    count_pdf   = 0
    count_excel = 0
    errors      = 0

    for i, row in enumerate(dr_data, 1):
        sep  = row['sep']
        case = get_case_by_sep(sep)
        if not case:
            continue

        triggered_rules = validate_case(case)
        kkr_data        = _build_kkr_data(row, case, triggered_rules)
        validate_data   = {'triggered_rules': triggered_rules}

        # Build output folder per RS
        rs_code = str(case.get('kode_rs', 'UNKNOWN'))
        rs_name = str(case.get('nama_rs', 'RS')).replace(' ', '_').replace('/', '_')[:40]
        rs_dir  = os.path.join(OUTPUT_DIR, f"{rs_code}_{rs_name}")
        os.makedirs(rs_dir, exist_ok=True)

        sep_safe = str(sep).replace('/', '_').replace('\\', '_')[:20]

        # ── PDF ──
        if mode in ('pdf', 'both'):
            try:
                pdf_bytes   = export_kkr_dr01_pdf(kkr_data, validate_data)
                output_path = os.path.join(rs_dir, f"KKR-DR01_{sep_safe}.pdf")
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                count_pdf += 1
            except Exception as e:
                print(f"  [PDF ERROR] SEP {sep}: {e}")
                errors += 1

        # ── Excel ──
        if mode in ('excel', 'both'):
            try:
                xl_bytes    = export_kkr_dr01_excel(kkr_data, validate_data)
                output_path = os.path.join(rs_dir, f"KKR-DR01_{sep_safe}.xlsx")
                with open(output_path, 'wb') as f:
                    f.write(xl_bytes)
                count_excel += 1
            except Exception as e:
                print(f"  [EXCEL ERROR] SEP {sep}: {e}")
                errors += 1

        if i % 50 == 0:
            print(f"  Progress: {i}/{len(dr_data)} | PDF:{count_pdf} | Excel:{count_excel} | Error:{errors}")

    print(f"\nSELESAI! PDF: {count_pdf} | Excel: {count_excel} | Errors: {errors}")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Bulk generate KKR-DR01 forms')
    parser.add_argument('--mode', choices=['pdf', 'excel', 'both'], default='both',
                        help='Output format: pdf, excel, or both (default: both)')
    args = parser.parse_args()
    bulk_generate_kkr_forms(mode=args.mode)
