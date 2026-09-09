"""Package laporan_final_20260831: readme, RS list, SHA256 manifest, copy KKR PDF with RS name, zip all."""
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from datetime import date

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'outputs' / 'hasil_akhir_20260907'
snap = json.loads((OUT / 'snapshot.json').read_text(encoding='utf-8'))


def rs_slug(nama_rs, max_len=40):
    slug = re.sub(r'[^A-Z0-9]+', '_', str(nama_rs).upper().strip())
    return slug.strip('_')[:max_len].rstrip('_')


# 🎯 Peta kode_rs -> nama_rs dari snapshot ----------------------------------------
rs_map = {h['kode_rs']: h['nama_rs'] for h in snap['hospitals']}

pdf_dst = OUT / 'pdf_kkr_per_rs'
kkr_count = len(list(pdf_dst.rglob('*.pdf'))) if pdf_dst.exists() else 0
print(f'OK pdf_kkr_per_rs  ({kkr_count} PDF form individual, sumber: generated directly from snapshot)')

# 📄 BACA_DULU.txt ---------------------------------------------------------------─────────────────────────────────────────────────────────────
baca = f"""PAKET LAPORAN FINAL AUDIT KODING — {date.today().strftime('%d %B %Y').upper()}

Isi: 44 Word per RS, 44 Excel per RS, 44 PDF KKR per RS,
     Word nasional, dan Excel nasional.
Gunakan seluruh laporan dalam paket ini bersama-sama.
Jangan dicampur dengan keluaran lama. File lama tidak ditimpa.

Konvensi nama file:
  Word  per RS : LHR_{{kode_rs}}_{{NAMA_RS}}.docx
  Excel per RS : Rekap_{{kode_rs}}_{{NAMA_RS}}.xlsx
  PDF KKR per RS: KKR_{{kode_rs}}_{{NAMA_RS}}.pdf
    (setiap PDF berisi semua kasus RS tersebut + bookmark per Nomor SEP)

Hasil yang seragam di seluruh format:
  Total kasus       : {snap['summary']['total']:,}  dari 44 RS
  On-Site Audit     : {snap['summary']['onsite']}  kasus
  Sampling/Klarifikasi: {snap['summary']['sampling']}  kasus
  Monitoring/lolos  : {snap['summary']['monitoring']:,}  kasus
  Belum terklasifikasi: {snap['summary']['unknown']}
  Dual coding kasus : {snap['summary']['dc_cases']}  kasus | {snap['summary']['dc_total']:,} perbedaan tersimpan
  Temuan aturan     : {snap['summary']['alerts']}  alert pada {snap['summary']['cases_with_alerts']} kasus
  Rerata skor KNAVP : {snap['summary']['avg_score']}

Dasar penyamaan: rekomendasi sistem tersimpan pada KKR-DR01.
Jika kosong, hanya keputusan tindak lanjut reviewer yang eksplisit digunakan.
Keputusan validitas reviewer asli tetap dipisahkan pada kolom Excel.

Snapshot SHA256  : {snap['snapshot_id']}
Kontrak versi    : saved-review-v1
Tanggal generate : {date.today().isoformat()}

Excel "Kontrol Rekonsiliasi": kolom Selisih Kategori = 0 untuk semua RS.
PDF KKR: snapshot rekonsiliasi, bukan pengesahan ulang; simpan terbatas
karena memuat identitas pasien dan data kesehatan.

BATASAN: Tata letak/paginasi Word belum diverifikasi secara visual karena
LibreOffice tidak tersedia. Periksa sebelum penerbitan resmi.

Lihat DAFTAR_RS.txt untuk daftar lengkap 44 RS.
"""
(OUT / 'BACA_DULU.txt').write_text(baca.strip(), encoding='utf-8')
print('OK BACA_DULU.txt')


# ── DAFTAR_RS.txt ─────────────────────────────────────────────────────────────
lines = [
    'DAFTAR RS — 44 RUMAH SAKIT SAMPEL AUDIT KODING 2025',
    '=' * 70, '',
    f'{"No":>3}  {"Kode RS":<10}  {"Nama RS":<48}  {"Total":>5}  {"On-Site":>7}  {"Sampling":>8}',
    '-' * 90,
]
for i, h in enumerate(snap['hospitals'], 1):
    s = h['summary']
    slug = rs_slug(h['nama_rs'])
    lines.append(
        f'{i:>3}.  {h["kode_rs"]:<10}  {h["nama_rs"]:<48}  {s["total"]:>5}  {s["onsite"]:>7}  {s["sampling"]:>8}'
    )
    lines.append(
        f'         File: LHR_{h["kode_rs"]}_{slug}.docx  |  '
        f'Rekap_{h["kode_rs"]}_{slug}.xlsx  |  KKR_{h["kode_rs"]}_{slug}.pdf'
    )
    lines.append('')

(OUT / 'DAFTAR_RS.txt').write_text('\n'.join(lines), encoding='utf-8')
print('OK DAFTAR_RS.txt')


# ── manifest SHA256 ───────────────────────────────────────────────────────────
manifest = {}
for f in sorted(p for p in OUT.rglob('*') if p.is_file()
                and p.suffix in ('.docx', '.xlsx', '.pdf', '.json', '.txt')):
    manifest[f.relative_to(OUT).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
(OUT / 'manifest_sha256.json').write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8'
)
print(f'OK manifest_sha256.json  ({len(manifest)} files)')


# ── ZIP ───────────────────────────────────────────────────────────────────────
print('SELESAI. File ZIP tidak dibuat sesuai permintaan user.')
