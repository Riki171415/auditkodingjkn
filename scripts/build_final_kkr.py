import json
import sys
import io
import os
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from modules.export_generator import _export_kkr_dr01_pdf_legacy

CCL_MAP = {'0': 'No CC', '1': 'Mild CC', '2': 'Moderate CC',
           '3': 'Severe CC', '4': 'Catastrophic CC', '9': 'Merge CC'}

def rs_slug(nama_rs, max_len=40):
    slug = re.sub(r'[^A-Z0-9]+', '_', str(nama_rs).upper().strip())
    return slug.strip('_')[:max_len].rstrip('_')

def build_pdfs_for_rs(args):
    h, out_dir_str = args
    out_dir_base = Path(out_dir_str)
    kode_rs = h['kode_rs']
    nama_rs = h['nama_rs']
    slug = rs_slug(nama_rs)
    
    # Create folder per RS
    rs_folder = out_dir_base / f"{kode_rs}_{slug}"
    rs_folder.mkdir(parents=True, exist_ok=True)
    
    for case in h['cases']:
        sep = case['sep']
        out_path = rs_folder / f'KKR-DR01_{sep}.pdf'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        idrg_raw = str(case.get('idrg_code', '') or '')
        ccl_digit = idrg_raw[-1] if idrg_raw else ''
        ccl_label = CCL_MAP.get(ccl_digit, '-')
        
        try:
            form_data = json.loads(case.get('tindakan_reviewer') or '{}')
        except Exception:
            form_data = {}
            
        kkr_data = {
            'sep': sep,
            'kode_rs': kode_rs,
            'nama_rs': nama_rs,
            'inacbg': case['inacbg'],
            'case': case,
            'triggered_rules': case.get('triggered_rules', []),
            'total_triggered': len(case.get('triggered_rules', [])),
            'knavp_skor': case.get('knavp_skor', 0.0),
            'tingkat_risiko': case.get('tingkat_risiko', '-'),
            'keputusan_sistem': case.get('keputusan_sistem', '-'),
            'jumlah_beda_dual_coding': case.get('jumlah_beda_dual_coding', 0),
            'ccl_label': ccl_label,
            'ccl_digit': ccl_digit,
            'dual_coding': {},
            'knavp': {},
            'reviewer_name': case.get('reviewer_name', ''),
            'tanggal_review': case.get('tanggal_review', '15 Juni 2026'),
            'tanggal_ketua': '15 Juni 2026'
        }
        kkr_data.update(form_data)
        
        pdf_bytes = _export_kkr_dr01_pdf_legacy(kkr_data)
        out_path.write_bytes(pdf_bytes)
            
    return f"Generated {rs_folder.name} ({len(h['cases'])} SEPs individual)"

def main():
    snap_path = BASE / 'outputs' / 'laporan_final_20260831' / 'snapshot.json'
    snap = json.loads(snap_path.read_text(encoding='utf-8'))
    
    out_dir = BASE / 'outputs' / 'laporan_final_20260831' / 'pdf_kkr_per_rs'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Optional: clean up old merged PDFs
    for old_pdf in out_dir.glob('KKR_*.pdf'):
        old_pdf.unlink()
    
    args_list = [(h, str(out_dir)) for h in snap['hospitals']]
    
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(build_pdfs_for_rs, arg) for arg in args_list]
        for future in as_completed(futures):
            print(future.result())

if __name__ == '__main__':
    main()
