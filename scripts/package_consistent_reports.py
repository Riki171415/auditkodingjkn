"""Package verified deliverables only; never include patient-level snapshot intermediates."""
from pathlib import Path
import json
import hashlib
import zipfile

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'outputs/rekonsiliasi_20260831'
snapshot=json.loads((OUT/'snapshot.json').read_text(encoding='utf-8'))
check=json.loads((OUT/'verifikasi.json').read_text(encoding='utf-8'))
assert check['status']=='PASS' and check['files']=={'word':45,'excel':45}
text='''PAKET KOREKSI DAN REKONSILIASI LAPORAN — 31 AGUSTUS 2026

Isi: 44 Word per RS, 44 Excel per RS, Word nasional, dan Excel nasional.
Gunakan keempat jenis laporan dalam paket ini bersama-sama. Jangan dicampur
dengan keluaran lama. Berkas lama dan database review tidak ditimpa.

Hasil yang sama di seluruh format:
- Total 5.206 kasus dari 44 RS.
- On-Site Audit 7 kasus.
- Sampling/Klarifikasi 79 kasus.
- Monitoring/tidak perlu tindak lanjut 5.120 kasus.
- Dual coding: 608 kasus dengan 1.047 perbedaan tersimpan.
- Temuan aturan: 384 alert pada 364 kasus.

Dasar penyamaan: rekomendasi sistem tersimpan pada KKR-DR01. Jika kosong,
hanya keputusan tindak lanjut reviewer yang eksplisit digunakan. Keputusan
validitas reviewer asli tetap dipisahkan pada Excel. Tidak dilakukan audit
klinis ulang; monitoring bukan bukti bahwa pengodean pasti benar.

Narasi statistik, lampiran dan grafik Word dibuat ulang dari satu snapshot
data memakai Template_Laporan_RS.docx. Grafik Word berupa gambar statis agar
tidak menyimpan data grafik lama. Word nasional menampilkan agregat seluruh
RS; rincian seluruh SEP terdapat dalam Excel nasional dan Word/Excel per RS.

Excel memiliki sheet Kontrol Rekonsiliasi; Selisih Kategori harus 0.
Jumlah kategori mencakup Sampling. Rata-rata memakai pembulatan yang sama.
Nomor klaim yang tidak ada di sumber rekap ditandai tidak tersedia, bukan
diisi angka buatan seperti pada generator lama.

Validasi data: LULUS untuk 90 keluaran dan rekomendasi seluruh 5.206 kasus.
QA visual Excel dilakukan pada area perwakilan semua sheet.
BATASAN: tata letak/paginasi Word belum diverifikasi secara visual karena
LibreOffice tidak tersedia. Periksa tata letak Word sebelum penerbitan resmi;
field nomor halaman disetel untuk diperbarui saat membuka dokumen di Word.

Lihat DAFTAR_RS.txt untuk pemetaan kode RS ke nama file. Perubahan kode
ekspor juga telah disimpan di proyek; server yang masih berjalan perlu
memuat ulang kode. Daftar unduhan lama di aplikasi tetap berisi arsip lama.
'''
(OUT/'BACA_DULU.txt').write_text(text,encoding='utf-8')
(OUT/'DAFTAR_RS.txt').write_text('\n'.join(f'{h["kode_rs"]} | {h["nama_rs"]} | {h["summary"]["total"]} kasus' for h in snapshot['hospitals']),encoding='utf-8')
files=sorted(OUT.rglob('*.docx'))+sorted(OUT.rglob('*.xlsx'))
manifest={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(OUT/'manifest_sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=OUT.parent/'Paket_Laporan_Konsisten_20260831.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[OUT/'BACA_DULU.txt',OUT/'DAFTAR_RS.txt',OUT/'manifest_sha256.json',OUT/'verifikasi.json']:
        z.write(p,str(p.relative_to(OUT)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==94
print(str(archive))
print('ZIP verified:',archive.stat().st_size,'bytes, 90 reports + 4 notes/verification files')
