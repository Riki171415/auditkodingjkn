import json
import sys
import io
import os
import pypdfium2 as pdfium
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from modules.export_generator import _export_kkr_dr01_pdf_legacy

CCL_MAP = {'0': 'No CC', '1': 'Mild CC', '2': 'Moderate CC',
           '3': 'Severe CC', '4': 'Catastrophic CC', '9': 'Merge CC'}

def test_generate_legacy_kkr():
    snap_path = BASE / 'outputs' / 'laporan_final_20260831' / 'snapshot.json'
    snap = json.loads(snap_path.read_text(encoding='utf-8'))
    case = snap['cases'][0]
    
    idrg_raw = str(case.get('idrg_code', '') or '')
    ccl_digit = idrg_raw[-1] if idrg_raw else ''
    ccl_label = CCL_MAP.get(ccl_digit, '-')
    
    try:
        form_data = json.loads(case.get('tindakan_reviewer') or '{}')
    except Exception:
        form_data = {}
        
    kkr_data = {
        'sep': case['sep'],
        'kode_rs': case['kode_rs'],
        'nama_rs': case['nama_rs'],
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
    
    try:
        pdf_bytes = _export_kkr_dr01_pdf_legacy(kkr_data)
        out_path = BASE / 'test_kkr_legacy.pdf'
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)
        print("Success! Created test_kkr_legacy.pdf")
        doc = pdfium.PdfDocument(str(out_path))
        print("Pages:", len(doc))
        page = doc.get_page(0)
        print(page.get_textpage().get_text_range()[:1000])
    except Exception as e:
        print("Error:", str(e))

if __name__ == '__main__':
    test_generate_legacy_kkr()
