# Lampiran Laporan Akhir Desk Review Validasi Koding

## Lampiran A: Metodologi dan Proses Audit Koding (Desk Review)

Proses audit koding ini dilakukan dengan pendekatan kombinasi antara penapis algoritmik (Rule-Based Engine) dan ajudikasi ahli (Human-in-the-Loop Review). Rangkaian proses ini dirancang untuk memaksimalkan cakupan audit tanpa mengorbankan spesifisitas penilaian klinis.

### 1. Ekstraksi dan Pembersihan Data (Data Ingestion)
Sampel klaim ditarik secara acak (stratified random sampling) dari database klaim INA-CBG yang telah dibayarkan. Data ini kemudian dienkripsi (pseudonymization) untuk menjaga privasi pasien sebelum dimasukkan ke dalam *pipeline* analisis.

### 2. Algorithmic Screening (KNAVP Engine)
Setiap kasus dievaluasi secara otomatis menggunakan **Katalog Nasional Aturan Validasi Pengodean (KNAVP)** edisi terkini. *Engine* ini akan:
* Melakukan validasi *Dual Coding* (INA-CBG vs iDRG).
* Menguji silang *Diagnosis* dan *Procedure* terhadap puluhan aturan medis (contoh: koherensi diagnosis utama vs umur/jenis kelamin, aturan manifestasi *Dagger-Asterisk*, dan validitas prosedur mayor).
* Menghitung **Skor KNAVP** berdasarkan bobot keparahan (*severity*) setiap anomali yang ditemukan.
* Mengeluarkan rekomendasi sistem otomatis (Lolos, Sampling, atau On-Site Audit).

### 3. Ajudikasi Manual (Expert Review)
Kasus-kasus yang ditandai (flagged) oleh sistem algoritma akan diteruskan ke antarmuka aplikasi *Desk Review* untuk divalidasi ulang secara visual oleh Tim Reviewer Koding independen.
* Reviewer menelaah rekam medis elektronik ringkas, kesesuaian tindakan, serta kronologis klaim.
* Mengesampingkan klaim palsu (*false positive*) dari KNAVP jika terdapat *evidence* klinis yang dapat dibenarkan.
* Menetapkan **Keputusan Reviewer Final** yang bersifat mengikat (Tidak Diperlukan Tindak Lanjut, Perlu Monitoring, atau Direkomendasikan On-Site Audit).

### 4. Agregasi dan Laporan
Data keputusan dari seluruh reviewer dikonsolidasikan, disaring dari duplikasi, lalu ditabulasikan ke dalam struktur agregat seperti Laporan Eksekutif ini untuk diteruskan kepada jajaran eksekutif faskes.

---

﻿## Lampiran B: Daftar Distribusi Keputusan per Rumah Sakit
Tabel berikut menyajikan rincian akumulasi volume sampel per fasilitas kesehatan beserta hasil ajudikasi akhir (Keputusan Reviewer).\n
| No | Nama Rumah Sakit | Total Kasus | Lolos (Tidak Perlu Tindak Lanjut) | Direkomendasikan On-Site Audit |
|:---|:---|---:|---:|---:|
| 1 | RSU SANTOSA HOSPITAL BANDUNG CENTRAL | 120 | 120 | 0 |
| 2 | RSU DR. HASAN SADIKIN | 120 | 119 | 1 |
| 3 | RSU DR. M.DJAMIL PADANG | 120 | 120 | 0 |
| 4 | RSU DR. KARIADI | 120 | 117 | 3 |
| 5 | RSUD DR. SOETOMO | 120 | 118 | 2 |
| 6 | RSU H. ADAM MALIK | 120 | 116 | 4 |
| 7 | RSUP DR. SARDJITO | 120 | 120 | 0 |
| 8 | RSU DR. W. SUDIROHUSODO | 120 | 117 | 3 |
| 9 | RSUP FATMAWATI | 120 | 120 | 0 |
| 10 | RS AWAL BROS PEKANBARU | 120 | 118 | 2 |
| 11 | RSUP SANGLAH DENPASAR | 120 | 120 | 0 |
| 12 | RSU TARAKAN | 120 | 120 | 0 |
| 13 | RS PAD GATOT SOEBROTO | 120 | 120 | 0 |
| 14 | RSU DR. MOEWARDI SURAKARTA | 120 | 116 | 4 |
| 15 | RS DR. SAIFUL ANWAR | 120 | 120 | 0 |
| 16 | RSU TANGERANG | 120 | 120 | 0 |
| 17 | RSU DR. MOHAMMAD HOESIN | 120 | 115 | 5 |
| 18 | RSUP PERSAHABATAN | 120 | 117 | 3 |
| 19 | RSIA HERMINA BEKASI | 120 | 119 | 1 |
| 20 | RSU PROF.DR. R.D KANDOU MANADO | 120 | 116 | 4 |
| 21 | RSUP DR. SOERADJI TIRTONEGORO KLATEN | 120 | 113 | 7 |
| 22 | RSUD ARIFIN ACHMAD | 120 | 117 | 3 |
| 23 | RS PRIMAYA TANGERANG | 119 | 117 | 2 |
| 24 | RS PRIMAYA BEKASI BARAT | 119 | 115 | 4 |
| 25 | RS SENTRA MEDIKA CIBINONG | 119 | 119 | 0 |
| 26 | RS PANTI RAPIH | 119 | 119 | 0 |
| 27 | RUMAH SAKIT AKADEMIK UNIVERSITAS GADJAH MADA | 119 | 116 | 3 |
| 28 | RS SENTRA MEDIKA | 119 | 119 | 0 |
| 29 | RSU PROV. NTB | 119 | 118 | 1 |
| 30 | RS SILOAM INTERNATIONAL HOSPITAL | 119 | 119 | 0 |
| 31 | RS SULTAN AGUNG SEMARANG | 119 | 119 | 0 |
| 32 | RS UNIVERSITAS ANDALAS | 118 | 117 | 1 |
| 33 | RS EKA HOSPITAL PEKANBARU | 118 | 118 | 0 |
| 34 | RS PKU MUHAMMADIYAH YOGYAKARTA | 118 | 118 | 0 |
| 35 | RS PHC | 118 | 115 | 3 |
| 36 | RS EMC TANGERANG | 117 | 110 | 7 |
| 37 | RS TELOGOREJO | 117 | 117 | 0 |
| 38 | RS MAYAPADA | 117 | 117 | 0 |
| 39 | RSUP SURABAYA | 115 | 97 | 18 |
| 40 | RS SILOAM BALI | 114 | 112 | 2 |
| 41 | RS EMC PULOMAS | 113 | 113 | 0 |
| 42 | RS HERMINA MADIUN | 113 | 113 | 0 |
| 43 | RS SILOAM HOSPITALS SURABAYA | 109 | 109 | 0 |
| 44 | RS EMC ALAM SUTERA | 108 | 105 | 3 |

