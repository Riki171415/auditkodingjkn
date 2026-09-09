# Konsistensi keluaran laporan

Semua rekomendasi laporan memakai `modules/report_data.py` (saved-review-v1).
Keputusan sistem yang tersimpan menjadi acuan, bukan penilaian ulang menggunakan
ambang skor berbeda. Jika kosong, hanya label tindak lanjut eksplisit dari reviewer
yang boleh menjadi fallback. Keputusan validitas reviewer dipertahankan terpisah.

Monitoring mencakup monitoring dan tidak perlu tindak lanjut. Dual coding memakai
jumlah perbedaan yang tersimpan pada KKR, bukan perbedaan kode grup INA-CBG/iDRG.
Jumlah kasus dengan perbedaan dan jumlah perbedaan ditampilkan terpisah.
Rata-rata menggunakan pembulatan half-up dua desimal, sesuai Excel ROUND.

Ekspor bersama: jalankan `scripts/build_consistent_reports.py --output <folder>`
untuk snapshot, lalu skrip yang sama dengan `--word` dan
`.report_work/build_excel.mjs --output <folder>` untuk seluruh Excel.
Gunakan Python/Node dari runtime workspace. Penulis Excel menggunakan
`@oai/artifact-tool`, dengan junction `.report_work/node_modules` ke paket runtime.
`REPORT_NODE_BIN` dapat mengatur lokasi Node pada host lain. Tidak ada instalasi
paket atau panggilan AI eksternal dalam jalur laporan yang telah disatukan.

Template Word: `Template_Laporan_RS.docx`. Angka naratif, lampiran, dan gambar
grafik dibuat ulang dari snapshot. Narasi AI/metadata lama tidak dipakai untuk
angka. Word nasional merangkum seluruh RS dan seluruh kasus prioritas; rincian
seluruh SEP terdapat di Excel nasional dan Word/Excel per RS. Gambar grafik
Word bersifat statis untuk menjaga kesamaan dengan snapshot.

Excel mempertahankan kolom rinci laporan terdahulu, menambahkan sumber keputusan
asli, dan mengganti ringkasan dengan rumus serta kontrol selisih nol. Writer
menolak ekspor jika daftar kasus template Excel berbeda dengan snapshot; jika
cakupan data bertambah, template rincian harus diperbarui terlebih dahulu.

Validasi: `scripts/test_report_data.py` dan `scripts/verify_consistent_reports.py`.
Verifikasi mencocokkan rekomendasi seluruh SEP, total tiap RS, agregat nasional,
jumlah prioritas, jumlah perbedaan, dan kesalahan formula Excel. File lama serta
data review tidak ditimpa. Server yang sedang berjalan perlu memuat ulang kode
sebelum memakai jalur ekspor baru; berkas lama di daftar unduhan tetap arsip.

Keterbatasan QA Word pada host ini: LibreOffice tidak tersedia, sehingga belum
ada pemeriksaan visual pagination/clipping. Pemeriksaan tabel/struktur dilakukan.

## Kertas kerja PDF

`modules/report_pdf.py` memakai kontrak keputusan yang sama. PDF menampilkan
keputusan reviewer asli, keputusan sistem tersimpan, dan rekomendasi rekap
sebagai tiga kolom berbeda. Identitas dibaca dari nama field asli `Nama_Pasien`,
`SEX`, dan `Birth_date`; tidak ada fallback nama/nomor/umur/DPJP acak. Tidak ada
tanda tangan atau persetujuan reviewer baru yang ditambahkan pada salinan ini.

Endpoint `/api/export/dr01/pdf/<sep>` melewati PDF/JSON cache lama dan mengekspor
review yang sudah tersimpan. Kasus tanpa review tersimpan ditolak, bukan dinilai
ulang secara diam-diam. Ekspor PDF lama pada `modules/export_generator.py` juga
diarahkan ke jalur ini. Fungsi berakhiran `_legacy` disimpan hanya sebagai arsip
implementasi dan tidak dipakai oleh endpoint aktif.

`scripts/check_pdf_recap_consistency.py` membaca seluruh PDF lama;
`scripts/build_consistent_kkr_pdf.py` membuat salinan per kasus dari snapshot
rekap, kemudian `scripts/verify_and_package_kkr_pdf.py` memeriksa nilai tercetak
terhadap file Excel, memastikan batas teks halaman, dan menggabungkan per RS
dengan bookmark Nomor SEP. Jalankan `scripts/test_pdf_report_contract.py` untuk
uji regresi pemisahan keputusan, data kosong, identitas, dan ekspor tersimpan.
