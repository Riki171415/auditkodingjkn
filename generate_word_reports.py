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


# ── Helper normalisasi keputusan — IDENTIK dengan Excel ──────────────────────
def _normalize_keputusan(form_data):
    """
    Normalisasi nilai keputusan_sistem agar konsisten antara Word dan Excel.
    Nilai keputusan_sistem yang valid:
      - 'Direkomendasikan On-Site Audit'
      - 'Audit Sampling'
      - 'Monitoring (Tidak perlu tindak lanjut)' / 'Tidak perlu tindak lanjut'
    """
    kep_sis = form_data.get('keputusan_sistem', '')
    kep     = form_data.get('keputusan', '')

    if kep_sis and kep_sis not in ('', '-', None):
        return str(kep_sis)

    kep_str = str(kep or '')
    if 'Fraud' in kep_str or 'Tidak Sesuai' in kep_str:
        return 'Direkomendasikan On-Site Audit'
    if 'Sesuai' in kep_str or 'Valid' in kep_str:
        return 'Monitoring (Tidak perlu tindak lanjut)'
    return kep_sis or kep_str or '-'


def _is_onsite(keputusan_str):
    """Cek apakah rekomendasi adalah On-Site Audit (konsisten dengan Excel)."""
    return 'On-Site' in str(keputusan_str) or 'Direkomendasikan On-Site' in str(keputusan_str)


def _is_sampling(keputusan_str):
    """Cek apakah rekomendasi adalah Sampling/Klarifikasi (konsisten dengan Excel)."""
    s = str(keputusan_str)
    return ('Sampling' in s or 'Klarifikasi' in s) and 'On-Site' not in s
# ─────────────────────────────────────────────────────────────────────────────


def _enrich_row(row):
    """Add parsed KNAVP v2 fields to a DR row from form_data JSON."""
    try:
        fd = json.loads(row.get('tindakan_reviewer') or '{}')
    except Exception:
        fd = {}

    row['knavp_skor']             = fd.get('knavp_skor',             row.get('knavp_skor', 0))
    row['tingkat_risiko']         = fd.get('tingkat_risiko',         row.get('tingkat_risiko', '-'))
    # ── Gunakan normalisasi terpusat ──────────────────────────────────────────
    row['keputusan_sistem']       = _normalize_keputusan(fd)
    # ─────────────────────────────────────────────────────────────────────────
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

        # ── Hitung statistik ringkasan — gunakan helper yg sama dengan Excel ──
        total      = len(cases)
        onsite     = sum(1 for c in cases if _is_onsite(c.get('keputusan_sistem', '')))
        sampling   = sum(1 for c in cases if _is_sampling(c.get('keputusan_sistem', '')))
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
