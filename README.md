# 🏥 SISTEM AUDIT KODING INA-CBG & iDRG 2025
**Aplikasi Analisis Casemix, Rule Engine Validasi Koding Klinis, dan Management Audit JKN Terintegrasi**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-Vite%20Frontend-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Generator-E34F26?style=for-the-badge)

---

## 📌 Deskripsi Singkat

**Sistem Audit Koding INA-CBG & iDRG 2025** adalah platform aplikasi berbasis web (*full-stack*) yang dirancang untuk mendukung tugas pengawasan, verifikasi, dan audit klaim pelayanan kesehatan program Jaminan Kesehatan Nasional (JKN). 

Sistem ini mengintegrasikan analisis statistik Casemix populasi nasional (*Outlier detection*), penetapan sampel klinis berdasarkan metode **Cochran**, pembandingan koding ganda (*Dual Coding INA-CBG vs iDRG internal RS*), penilaian otomatis bobot **KNAVP**, hingga ekspor massal instrumen Kertas Kerja Rekapitulasi (KKR) dan Laporan Akhir resmi.

---

## ✨ Fitur Utama Aplikasi

### 📊 1. Dasbor Analisis Casemix (Tahap 1)
- **Scatter Plot Interaktif**: Memetakan hubungan antara *Case Mix Index* (CMI) dan *Average Length of Stay* (ALOS) untuk seluruh Rumah Sakit di Indonesia.
- **Scorecard CMI**: Pemantauan rata-rata CMI nasional dan per kelas Rumah Sakit (Kelas A, B, C, D).
- **Deteksi Outlier Otomatis**: Klasifikasi otomatis RS anomali menggunakan 2 metode statistik:
  - **Outlier 2SD (Standar Deviasi)**: RS yang melampaui batas kewajaran $\mu \pm 2\sigma$ (Warna Merah).
  - **Outlier IQR (*Interquartile Range*)**: RS yang melampaui batas kewajaran $Q_3 + 1.5\text{IQR}$ (Warna Oranye).

### 🎯 2. Penetapan Sasaran & Perhitungan Sampel (Tahap 2 & 3)
- **40 RS Sampel Outlier**: Seleksi otomatis 40 RS dengan prioritas status Outlier CMI dan diskrepansi selisih tarif (*Tarif RS vs Tarif Klaim*) terbesar.
- **Kalkulator Cochran (1977)**: Perhitungan ukuran sampel kasus representatif secara otomatis menggunakan *Finite Population Correction* berdasarkan total klaim/SEP per RS.

### 📋 3. Audit Desk Review & Rule Engine KNAVP (Tahap 4)
- **ICD Rule Engine**: Validasi otomatis logika koding medis terhadap aturan *Combination Code*, *Dagger & Asterisk*, *Includes/Excludes*, dan *Unbundling*.
- **Dual Coding Discrepancy Checker**: Membandingkan baris per baris diagnosis dan prosedur antara klaim INA-CBG dengan koding internal RS (iDRG) dengan toleransi kecocokan klinis.
- **Skoring KNAVP & Rekomendasi Sistem**: Kalkulasi skor otomatis berdasarkan bobot pelanggaran (*Kelengkapan, Kejelasan, Spesifisitas, Keterbacaan, Konsistensi*) untuk menentukan tindak lanjut (*Monitoring*, *Audit Sampling*, atau *On-Site Audit*).

### 🏥 4. Audit On-Site & Verifikasi Rekam Medis (Tahap 5)
- **Form KKR-OS01 Digital**: Instrumen rekapitulasi audit lapangan untuk memverifikasi dokumen fisik rekam medis (Resume Medis, Laporan Operasi, Penunjang) terhadap temuan *Desk Review*.
- **Penetapan Kesimpulan Akhir**: Klasifikasi akhir klaim (*Layak*, *Tidak Layak / Pengembalian Selisih Tarif*, atau *Pembinaan Koding*).

### 📦 5. Generator Laporan & Ekspor Massal
- **PDF KKR-DR01 & KKR-OS01 (`generate_kkr_forms_fast.py`)**: Mesin cetak cepat dokumen PDF resmi yang dilengkapi rincian temuan, skoring KNAVP, dan kolom tanda tangan.
- **Rekapitulasi Excel (`generate_recap_desk_review.py`)**: Buku kerja spreadsheet `.xlsx` multi-sheet yang merangkum hasil audit dan kalkulasi total pengembalian tarif.
- **Laporan Eksekutif Word (`generate_word_reports.py`)**: Narasi resmi format `.docx` per RS yang siap disampaikan kepada manajemen RS dan BPJS Kesehatan.

---

## 📁 Struktur Direktori Proyek

```
audit-app/
├── app.py                      # Controller utama Flask API & static file server
├── data.db                     # Database SQLite utama (cmi_data & individual_data)
├── jalankan_server.bat         # Script launcher satu klik untuk OS Windows
├── PANDUAN_ALUR_AUDIT_CASEMIX.md # Dokumentasi teknis & formula matematis audit
├── requirements.txt            # Daftar pustaka Python backend
├── modules/
│   ├── data_loader.py          # Access layer SQLite & kalkulator statistik Outlier
│   ├── rule_engine.py          # Mesin validasi koding & skoring KNAVP
│   ├── db_manager.py           # Manajemen koneksi & CRUD hasil audit
│   └── export_service.py       # Layanan ekspor data
├── rules/                      # Definisi aturan koding ICD & iDRG
├── frontend/                   # Proyek frontend React + Vite + Recharts
│   ├── dist/                   # Hasil build produksi React (disajikan oleh Flask)
│   ├── src/                    # Kode sumber komponen React JSX & CSS
│   └── package.json            # Konfigurasi dependensi Node.js
└── exports/                    # Folder keluaran file PDF, Excel, dan Word
```

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi Lokal

### Cara 1: Mode Pengguna / Produksi Lokal (Paling Mudah)
Cara ini cocok untuk menjalankan aplikasi secara langsung tanpa perlu menyalakan *compiler* React:
1. Pastikan **Python 3.10+** telah terinstal di komputer.
2. Buka terminal di folder root proyek dan instal pustaka pendukung:
   ```bash
   pip install -r requirements.txt
   ```
3. Di sistem operasi Windows, cukup klik ganda (*double-click*) file **`jalankan_server.bat`**. Atau jalankan lewat terminal:
   ```bash
   python app.py
   ```
4. Buka browser dan akses alamat:
   👉 **`http://localhost:5000`**

---

### Cara 2: Mode Pengembangan (*Developer Dev Mode*)
Gunakan cara ini apabila Anda ingin memodifikasi kode tampilan frontend (`.jsx` / `.css`) agar perubahan langsung terlihat secara *Hot-Reload*:

1. **Jalankan Backend Flask (Port 5000):**
   Buka terminal pertama di root folder:
   ```bash
   python app.py
   ```
2. **Jalankan Frontend Vite React (Port 5173):**
   Buka terminal kedua dan masuk ke folder `frontend`:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Buka browser dan akses alamat dev server:
   👉 **`http://localhost:5173`**

*(Catatan: `vite.config.js` sudah dilengkapi proxy otomatis yang mengarahkan seluruh rute `/api/*` ke port 5000).*

---

## ☁️ Panduan Deployment di PythonAnywhere

Aplikasi ini siap di-deploy dan dijalankan pada layanan hosting cloud **PythonAnywhere**:

1. **Perbarui Kode dari Repository GitHub:**
   Buka **Bash Console** di PythonAnywhere, lalu jalankan:
   ```bash
   cd audit-app
   git reset --hard HEAD
   git pull origin main
   ```

2. **Tips Menghemat Kuota Storage (512 MB Free Tier):**
   Karena PythonAnywhere hanya menyajikan file produksi di `frontend/dist`, Anda dapat menghapus folder `node_modules` serta file spreadsheet mentah agar kuota tetap lega:
   ```bash
   rm -rf frontend/node_modules/
   rm -f *.xlsx
   ```

3. **Penanganan Database (`data.db`):**
   Jika ukuran `data.db` melebihi batas upload web 100 MB, kompres menjadi `data.zip` di komputer lokal, upload `data.zip` via menu **Files**, lalu ekstrak di Bash Console:
   ```bash
   unzip data.zip
   rm -f data.zip
   ```

4. **Muat Ulang Aplikasi (*Reload Web App*):**
   Masuk ke menu **Web** di dasbor PythonAnywhere, lalu klik tombol hijau besar:  
   👉 **`Reload riki17.pythonanywhere.com`**

---

## 📚 Tautan Dokumentasi Terkait

Untuk mendalami alur bisnis, formula matematis batas 2SD/IQR, perhitungan ukuran sampel **Cochran**, dan logika koding skoring **KNAVP**, silakan baca dokumen teknis lengkap di bawah ini:
👉 **[Panduan Lengkap Alur & Formula Audit Casemix (`PANDUAN_ALUR_AUDIT_CASEMIX.md`)](file:///d:/KERJAAN%20PUSBIKES/Audit%20Koding%202025/audit-app/PANDUAN_ALUR_AUDIT_CASEMIX.md)**

---
*Dibuat untuk Tim Audit Koding Pusbikes & BPJS Kesehatan — 2025*
