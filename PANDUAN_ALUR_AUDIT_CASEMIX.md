# PANDUAN LENGKAP & ALUR SISTEM AUDIT KODING INA-CBG & iDRG 2025

Dokumen ini menjelaskan alur kerja (*workflow*), arsitektur teknis, serta formula matematis dan logika bisnis yang diterapkan dalam **Aplikasi Audit Koding INA-CBG & iDRG 2025** mulai dari pengolahan data awal, identifikasi Outlier, penarikan sampel kasus, hingga pembuatan Kertas Kerja Rekapitulasi (KKR) dan Laporan Akhir.

---

## 1. Arsitektur Umum & Alur Tahapan Audit

Sistem ini dirancang untuk melakukan pengawasan dan verifikasi klaim pelayanan kesehatan JKN melalui pendekatan analisis data (*data-driven casemix analysis*) yang terbagi menjadi 5 Tahapan Utama:

```
[Tahap 1: Analisis Casemix & Outlier]
            │
            ▼
[Tahap 2: Penetapan 40 RS Sampel Outlier]
            │
            ▼
[Tahap 3: Perhitungan Sampel Kasus (Cochran's Formula)]
            │
            ▼
[Tahap 4: Audit Desk Review & Penilaian KNAVP (KKR-DR01)]
            │
            ▼
[Tahap 5: Audit On-Site & Ekspor Laporan Akhir (KKR-OS01, PDF, Excel, Word)]
```

---

## 2. Pembangkitan & Manajemen Data (*Data Generation & Loader*)

### A. Penyimpanan Data (`data.db`)
Aplikasi menggunakan basis data **SQLite (`data.db`)** yang ringan dan teroptimasi untuk lingkungan server seperti PythonAnywhere maupun intranet lokal. Basis data ini terdiri dari dua tabel utama:
1. **`cmi_data`**: Menyimpan rekapitulasi data per Rumah Sakit (Kode RS, Nama RS, Kelas, Regional, Total Kasus, CMI, ALOS, Tarif INA-CBG, Tarif RS, Status Audit 2SD & IQR).
2. **`individual_data`**: Menyimpan rincian klaim per episode pasien/SEP (*Surat Eligibilitas Peserta*), termasuk diagnosis utama, diagnosis sekunder (`diaglist`), prosedur (`proclist`), serta koding internal RS (`diaglist_idrg`, `proclist_idrg`).

### B. Modul Pembangkitan Data (`generate_dummy_dr.py` & `init_db.py`)
- **`generate_dummy_dr.py`**: Digunakan untuk mengonversi data dari spreadsheet Excel mentah menjadi format SQLite (`data.db`) atau membangkitkan data simulasi klaim apabila diperlukan untuk pengujian.
- **`data_loader.py`**: Bertindak sebagai *Data Access Layer* yang memproses query optimasi memori untuk ditampilkan pada grafik *Scatter Plot* dan *Scorecard CMI*.

---

## 3. Tahap 1: Analisis Casemix & Identifikasi Outlier

Pada dasbor utama (*Tahap 1*), sistem membandingkan tingkat keparahan kasus yang ditangani (*Case Mix Index* / CMI) dengan rata-rata lama rawat (*Average Length of Stay* / ALOS).

### A. Perhitungan Statistik Dasar
Rata-rata nasional CMI ($\mu$) dan Standar Deviasi ($\sigma$) dihitung dari seluruh populasi rumah sakit yang aktif:

$$\mu = \frac{\sum \text{CMI}_i}{N}, \quad \sigma = \sqrt{\frac{\sum (\text{CMI}_i - \mu)^2}{N}}$$

### B. Pendekatan Batas Kewajaran (*Outlier Detection*)
Sistem menerapkan 2 metode statistik untuk mendeteksi anomali koding atau intensitas klaim:

1. **Metode 2SD (Standar Deviasi)**
   - **Batas Atas 2SD** $= \mu + (2 \times \sigma)$
   - **Batas Bawah 2SD** $= \mu - (2 \times \sigma)$
   - *Kriteria Outlier*: RS dengan nilai $\text{CMI} > \text{Batas Atas 2SD}$ diklasifikasikan sebagai **Outlier 2SD** (Warna Merah).

2. **Metode IQR (*Interquartile Range*)**
   - Kuartil 1 ($Q_1$) = Kuantil 25%, Kuartil 3 ($Q_3$) = Kuantil 75%
   - $\text{IQR} = Q_3 - Q_1$
   - **Batas Atas IQR** $= Q_3 + (1.5 \times \text{IQR})$
   - **Batas Bawah IQR** $= Q_1 - (1.5 \times \text{IQR})$
   - *Kriteria Outlier*: RS dengan nilai $\text{CMI} > \text{Batas Atas IQR}$ diklasifikasikan sebagai **Outlier IQR** (Warna Oranye).

---

## 4. Tahap 2 & 3: Penetapan 40 RS Sampel & Perhitungan Ukuran Sampel

### A. Penetapan 40 RS Sampel (*Target Selection*)
Sistem menyeleksi **40 Rumah Sakit Sampel** yang memprioritaskan:
1. RS yang masuk dalam kategori **Outlier CMI** (2SD atau IQR).
2. RS dengan **Selisih Tarif terbesar** (Selisih antara Tarif Standar RS dengan Tarif Klaim INA-CBG yang dibayarkan).

### B. Perhitungan Jumlah Sampel Kasus (Rumus Cochran)

**Catatan Metodologi Cochran**

1. **Rumus Dasar Cochran ($n_0$):**
   $$n_0 = \frac{Z^2 \cdot p \cdot (1-p)}{e^2}$$
   - $Z = 1.96$ (Tingkat kepercayaan 95%)
   - $p = 0.5$ (Variabilitas maksimal/paling konservatif)
   - $e = 0.05$ (Margin of error 5%)
   - $n_0 = 384.16$

2. **Koreksi Populasi Terbatas (Finite Population Correction):**
   $$n = \frac{n_0}{1 + \frac{n_0 - 1}{N}}$$
   - Jika jumlah populasi ($N$) klaim pada suatu RS sangat besar (misal RJ $> 10.000$), jumlah sampel akan mendekati 385.
   - Jika populasi ($N$) kecil (misal RI $< 300$), rumus secara otomatis menyesuaikan jumlah sampel agar proporsional dan tidak melebihi populasi.

**Penjelasan Rumus Cochran < 60 Sampel**
Aturan Dasar: Jika batas atas sampel diinginkan tidak lebih dari 60, maka nilai $n_0$ diset ke 59.9 (atau nilai antara 50–59.9 tergantung tingkat presisi).
Formula Koreksi Populasinya (FPC):
$$n = \left\lceil \frac{1}{1 + \frac{59.9 - 1}{59.9}} \right\rceil$$ *(Catatan: Nilai disesuaikan berdasarkan rasio agar mendekati/maksimal 60 sampel).*
- Jika jumlah klaim ($N$) sangat melimpah (misal $>5.000$), nilai hasil pembagian mendekati 60 sampel.
- Jika jumlah klaim ($N$) kecil (misal hanya 40 kasus), nilai hasilnya akan otomatis terkoreksi menjadi $\le 40$ sampel (tidak melebihi total klaim yang ada).

---

## 5. Tahap 4: Audit Desk Review & Penilaian KNAVP (Form KKR-DR01)

Pada tahap *Desk Review*, setiap kasus sampel dievaluasi secara otomatis oleh **Rule Engine (`modules/rule_engine.py`)** dan divalidasi oleh auditor koding.

### A. Evaluasi Logika Koding (*Rule Engine*)
Sistem memeriksa pelanggaran koding berdasarkan aturan ICD-10 & ICD-9-CM, seperti:
- **Combination Code**: Penggabungan dua diagnosis menjadi satu kode kombinasi.
- **Dagger & Asterisk ($\dagger/\ast$)**: Aturan koding etiologi dan manifestasi.
- **Includes / Excludes**: Pengecekan kontradiksi diagnosis yang tidak boleh dikoding bersamaan.
- **Unbundling**: Pemecahan paket prosedur yang seharusnya dikoding dalam satu kode tunggal.

### B. Pengecekan Discrepancy Dual Coding (INA-CBG vs iDRG)
Sistem membandingkan kode INA-CBG yang diklaim dengan kode internal RS (iDRG) dengan aturan pencocokan (*matching rules*):
1. **Exact Match**: Kode persis sama (`A01.0` vs `A01.0`) $\rightarrow$ **Sesuai**.
2. **Specificity Tolerance**: Toleransi digit perluasan (`90.59` vs `90.599`) $\rightarrow$ **Sesuai**.
3. **Modifier Stripping**: Mengabaikan modifier tambahan iDRG (`99.04+2` $\rightarrow$ `99.04`) $\rightarrow$ **Sesuai**.
4. **Exclusion List**: Mengabaikan kode administratif non-klinis (`KG`, `HL`, `NL`, `G89`, `U82-U84`, `99.290`).

*(Catatan khusus: Jika posisi kode utama/sekunder berbeda antara INA-CBG dan iDRG namun kode tersebut tetap ditemukan di kedua daftar, sistem menganggapnya **Sesuai** sesuai logika toleransi klinis).*

### C. Penilaian KNAVP & Rekomendasi Sistem
Setiap temuan pelanggaran diberikan bobot skor berdasarkan kriteria **KNAVP** (*Kelengkapan, Kejelasan, Spesifisitas, Keterbacaan, Konsistensi*):

| Total Skor KNAVP | Tingkat Risiko | Keputusan / Rekomendasi Sistem |
| :---: | :---: | :--- |
| **0** | Rendah | Tidak perlu tindak lanjut |
| **1 - 3** | Rendah | Monitoring (Tidak perlu tindak lanjut) |
| **4 - 7** | Sedang | Audit Sampling |
| **$\ge$ 8** | Tinggi | **Direkomendasikan On-Site Audit** |

---

## 6. Tahap 5: Audit On-Site & Ekspor Output (KKR-OS01 & Laporan)

Kasus-kasus yang direkomendasikan untuk audit lanjutan dilanjutkan ke verifikasi lapangan (*On-Site Audit*) menggunakan instrumen **KKR-OS01**.

### A. Instrumen KKR-OS01
Auditor melakukan verifikasi bukti fisik rekam medis (Resume Medis, Laporan Operasi, Hasil Laboratorium/Radiologi) dan menetapkan kesimpulan akhir:
- **Klaim Layak (Sesuai)**
- **Klaim Tidak Layak / Pengembalian Selisih Tarif**
- **Pembinaan Koding RS**

### B. Modul Ekspor & Generator Output Massal
Sistem dilengkapi modul pembuatan laporan otomatis yang siap cetak:
1. **Generator PDF Form KKR (`generate_kkr_forms_fast.py`)**:
   - Membangkitkan ribuan dokumen PDF Form **KKR-DR01** dan **KKR-OS01** secara cepat menggunakan *ReportLab*.
   - Terisi lengkap dengan data identitas pasien, diagnosis/prosedur INA-CBG vs iDRG, temuan aturan yang dilanggar, skor KNAVP, serta kolom tanda tangan auditor dan pihak rumah sakit.
2. **Rekapitulasi Excel (`generate_recap_desk_review.py`)**:
   - Menghasilkan buku kerja Excel multi-sheet yang berisi ringkasan seluruh sampel, rincian temuan per kasus, dan kalkulasi total selisih tarif yang direkomendasikan untuk dikembalikan.
3. **Laporan Eksekutif Word (`generate_word_reports.py`)**:
   - Membuat narasi laporan resmi format `.docx` per Rumah Sakit yang mencakup analisis latar belakang, temuan Desk Review & On-Site, serta rekomendasi kebijakan untuk manajemen RS dan BPJS Kesehatan.

---

## 7. Ringkasan File Utama Kode Sumber

| Path File | Fungsi Utama |
| :--- | :--- |
| `app.py` | Controller utama Flask backend (API endpoints & *static file server*). |
| `modules/data_loader.py` | Memuat data Casemix (`cmi_data`), data individu, dan perhitungan statistik Outlier. |
| `modules/rule_engine.py` | Mesin validasi koding ICD, pembanding Dual Coding, dan kalkulator skor KNAVP. |
| `modules/db_manager.py` | Manajemen koneksi SQLite dan operasi CRUD hasil audit. |
| `generate_kkr_forms_fast.py` | Generator PDF super cepat untuk mencetak Form KKR-DR01 & KKR-OS01 massal. |
| `generate_recap_desk_review.py` | Generator laporan rekapitulasi format spreadsheet Excel (`.xlsx`). |
| `generate_word_reports.py` | Generator laporan eksekutif resmi format Microsoft Word (`.docx`). |
| `frontend/src/pages/` | Tampilan antarmuka React (Dashboard, Desk Review, On-Site, KKR Forms, Reports). |
