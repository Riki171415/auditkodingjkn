"""
Bulk generate Laporan Hasil Audit (LHA) per RS dalam format Word (.docx).
Menyertakan ringkasan KNAVP v2: skor, tingkat risiko, dual coding,
dan rekomendasi sistem per kasus.
"""
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.db_manager import get_audit_db, get_recap_desk_review, save_generated_report
from modules.export_generator import generate_lha_word

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'word_reports')


def _enrich_row(row):
    """Add parsed KNAVP v2 fields to a DR row from form_data JSON."""
    try:
        fd = json.loads(row.get('tindakan_reviewer') or '{}')
    except Exception:
        fd = {}

    row['knavp_skor']             = fd.get('knavp_skor',             row.get('knavp_skor', 0))
    row['tingkat_risiko']         = fd.get('tingkat_risiko',         row.get('tingkat_risiko', '-'))
    row['keputusan_sistem']       = (fd.get('keputusan_sistem') or fd.get('keputusan') or
                                     row.get('keputusan_sistem') or '-')
    row['jumlah_beda_dual_coding']= fd.get('jumlah_beda_dual_coding', row.get('jumlah_beda_dual_coding', 0))
    row['ccl_label']              = fd.get('ccl_label', row.get('ccl_label', '-'))
    row['alasan_keputusan']       = fd.get('alasan_keputusan', fd.get('analisis_reviewer', '-'))
    return row


def bulk_generate_word_reports():
    print("=" * 60)
    print("Generating Bulk Word Reports (LHA) per RS...")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dr_data = get_recap_desk_review()
    if not dr_data:
        print("Tidak ada data Desk Review ditemukan.")
        return

    # Enrich & group by RS
    rs_map = {}
    for row in dr_data:
        row = _enrich_row(row)
        kode_rs = row['kode_rs']
        if kode_rs not in rs_map:
            rs_map[kode_rs] = {'nama_rs': row.get('nama_rs', kode_rs), 'cases': []}
        rs_map[kode_rs]['cases'].append(row)

    print(f"Ditemukan {len(rs_map)} Rumah Sakit.\n")

    for kode_rs, data in rs_map.items():
        rs_name = data['nama_rs']
        cases   = data['cases']

        # Hitung statistik ringkasan untuk dimasukkan ke Word header
        total      = len(cases)
        onsite     = sum(1 for c in cases if 'On-Site' in str(c.get('keputusan_sistem', '')))
        sampling   = sum(1 for c in cases if 'Sampling' in str(c.get('keputusan_sistem', '')) and 'On-Site' not in str(c.get('keputusan_sistem', '')))
        monitor    = total - onsite - sampling
        avg_skor   = round(sum(float(c.get('knavp_skor', 0) or 0) for c in cases) / max(total, 1), 1)
        beda_dc    = sum(int(c.get('jumlah_beda_dual_coding', 0) or 0) for c in cases)

        print(f"  [{kode_rs}] {rs_name}")
        print(f"    -> {total} kasus | On-Site: {onsite} | Sampling: {sampling} | Monitor: {monitor} | Avg Skor: {avg_skor}")

        safe_name = rs_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
        filename  = f"LHA_{kode_rs}_{safe_name}.docx"
        out_path  = os.path.join(OUTPUT_DIR, filename)

        # Kirim summary_stats ke generate_lha_word sebagai metadata tambahan
        summary_stats = {
            'total_kasus':    total,
            'onsite':         onsite,
            'sampling':       sampling,
            'monitoring':     monitor,
            'avg_skor_knavp': avg_skor,
            'total_beda_dc':  beda_dc,
        }

        generate_lha_word(kode_rs, rs_name, cases, out_path, summary_stats=summary_stats)

        rel_path = f"exports/word_reports/{filename}"
        save_generated_report('LHA_WORD', filename, rel_path, kode_rs)

        print(f"    -> Tersimpan: {filename}")

    print(f"\nSELESAI! Semua LHA tersimpan di: {OUTPUT_DIR}")


if __name__ == '__main__':
    bulk_generate_word_reports()
