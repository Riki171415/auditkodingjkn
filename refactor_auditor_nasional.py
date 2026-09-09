import os

def refactor_nasional():
    file_path = "generate_laporan_akhir_nasional.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Rewrite Gambaran Casemix (Intro)
    old_casemix = """    add_p("a. Gambaran Casemix dan Penentuan Sampel", bold=True)
    add_p(f"Casemix Index (CMI) merupakan indikator krusial yang merepresentasikan rata-rata tingkat keparahan (case weight) dari seluruh kasus yang ditangani oleh rumah sakit. Nilai CMI dihitung secara sistematis dengan membagi total bobot (case weight) seluruh kasus dengan total jumlah kasus yang ada di rumah sakit tersebut. Pergeseran nilai CMI yang terdeteksi secara signifikan—terutama jika ditandai dengan peningkatan proporsi Severity Level (CCL/PCCL) yang tidak wajar dan berada di luar batas distribusi normal (batas atas)—menjadi landasan utama (red flag) dalam penentuan prioritas sampel audit koding.")
    
    add_p(f"Berdasarkan analisis populasi nasional terhadap parameter CMI tersebut, telah diekstraksi kasus sampel dari {len(rs_data)} Rumah Sakit (FPKTL). Rumah sakit ini terpilih sebagai lokus evaluasi mendalam menggunakan instrumen KKR-DR01. Berikut adalah rincian populasi kasus, jumlah sampel yang ditarik untuk Desk Review, dan Nilai CMI dari masing-masing rumah sakit terpilih:")"""
    
    new_casemix = """    add_p("a. Analisis Casemix Index (CMI) dan Penarikan Sampel", bold=True)
    add_p("1. FAKTA")
    add_p(f"Berdasarkan distribusi nilai CMI nasional, teridentifikasi {len(rs_data)} fasilitas kesehatan (RS) yang menempati posisi di atas ambang batas (upper control limit) +2 Standar Deviasi. Atas dasar tersebut, sistem mengekstraksi data klaim elektronik dari {len(rs_data)} RS terpilih sebagai populasi sampel audit Desk Review.")
    add_p("2. HUBUNGAN DAN IMPLIKASI")
    add_p("Deviasi positif pada nilai CMI mengindikasikan lonjakan rata-rata bobot tingkat keparahan kasus (PCCL) yang diklaim oleh RS. Lonjakan ini berkorelasi langsung dengan potensi over-coding yang dapat membebani resiliensi pembiayaan JKN.")
    add_p("3. TINDAK LANJUT")
    add_p("Dilakukan penarikan sampel Cochran pada masing-masing RS guna memvalidasi justifikasi medis dari tingginya bobot kasus tersebut.")"""
    
    content = content.replace(old_casemix, new_casemix)
    
    # 2. Rewrite Matriks Pelanggaran KNAVP
    old_top = """        add_p(f"Berdasarkan hasil validasi, kelompok temuan paling dominan secara nasional adalah {dom_cat} ({dom_cnt} temuan atau {round(dom_cnt / total_rules_triggered * 100, 1)}% dari seluruh ketidaksesuaian pengodean). "
              "Kondisi tersebut mengindikasikan kelemahan pada penerapan kaidah Includes/Excludes, penggunaan kode manifestasi tanpa underlying cause yang tepat, serta ketidakselarasan antara kode diagnosis primer dengan prosedur medis. "
              "Seluruh temuan ini mensyaratkan klarifikasi administratif dan verifikasi dokumen rekam medis fisik guna memastikan kepatuhan terhadap pedoman ICS.")"""
              
    new_top = """        add_p("1. FAKTA")
        add_p(f"Kumulasi validasi KNAVP nasional menghasilkan {total_rules_triggered} rekaman anomali, dengan konsentrasi anomali tertinggi pada kelompok {dom_cat} sejumlah {dom_cnt} kejadian ({round(dom_cnt / total_rules_triggered * 100, 1)}%).")
        add_p("2. HUBUNGAN")
        add_p(f"Tingginya anomali {dom_cat} merepresentasikan kegagalan integrasi antara standar koding (ICS) dengan dokumentasi riil medis.")
        add_p("3. IMPLIKASI AUDIT")
        add_p("Temuan berskala nasional ini menetapkan landasan audit yang kuat bahwa prioritas verifikasi lapangan (On-Site Audit) mutlak difokuskan pada pengujian kelengkapan medical evidence pendukung kode terkait.")"""
        
    content = content.replace(old_top, new_top)
    
    # 3. Rewrite Rekomendasi
    old_rekom = """    add_p("c. Rekomendasi Tindak Lanjut dan Kasus Prioritas", bold=True)
    add_p(f"Berdasarkan hasil analisis terhadap {total_kasus:,} kasus, direkomendasikan tindak lanjut berdasarkan stratifikasi risiko sebagai berikut:")
    add_list_item(f"Penyelesaian proses klaim bagi {keputusan_counts['Lolos/Monitoring']:,} kasus (Lolos/Monitoring Terjadwal) yang terverifikasi selaras dengan pedoman ICS.", bullet=True)
    add_list_item(f"Klarifikasi Administratif (Audit Sampling) terhadap {keputusan_counts['Audit Sampling']:,} kasus untuk menelusuri kelengkapan dokumen administratif di fasilitas kesehatan.", bullet=True)
    add_list_item(f"Pelaksanaan On-Site Audit terhadap {keputusan_counts['Direkomendasikan On-Site Audit']:,} kasus prioritas ({perc_onsite}%) guna memverifikasi kesesuaian klaim dengan bukti fisik rekam medis pasien, khususnya pada kasus yang berpotensi menyebabkan pergeseran tingkat keparahan (CCL/PCCL).", bullet=True)"""
    
    new_rekom = """    add_p("c. Stratifikasi Keputusan Triase Nasional", bold=True)
    add_p("1. FAKTA")
    add_p(f"Dari total {total_kasus:,} kasus nasional yang divalidasi, sistem menerbitkan tiga klaster luaran: {keputusan_counts['Lolos/Monitoring']:,} kasus Lolos/Monitoring, {keputusan_counts['Audit Sampling']:,} kasus Audit Sampling, dan {keputusan_counts['Direkomendasikan On-Site Audit']:,} kasus On-Site Audit.")
    add_p("2. IMPLIKASI ADMINISTRATIF")
    add_p("Mayoritas kasus berstatus Lolos memenuhi prasyarat pembayaran secara administratif.")
    add_p("3. IMPLIKASI AUDIT")
    add_p(f"Terdapat {keputusan_counts['Direkomendasikan On-Site Audit']:,} kasus berisiko tinggi yang secara definitif direkomendasikan untuk uji validitas fisik di lokasi RS, dan {keputusan_counts['Audit Sampling']:,} kasus untuk konfirmasi rekam administratif.")"""
    
    content = content.replace(old_rekom, new_rekom)
    
    # 4. Rewrite Discrepancy Dual Coding
    old_disc = """    add_p("d. Analisis Kesesuaian Input (Discrepancy Dual Coding)", bold=True)
    add_p(f"Evaluasi kesesuaian input pengodean antara sistem INA-CBG dan iDRG dari total {total_kasus:,} berkas klaim nasional menunjukkan hasil sebagai berikut:")
    add_p(f"Terdapat {discrepancy_count:,} berkas klaim ({perc_discrepancy}%) yang menunjukkan diskrepansi pengodean, meliputi perbedaan input diagnosis atau prosedur medis. "
          f"Sebaliknya, sebanyak {total_kasus - discrepancy_count:,} berkas klaim ({round(100-perc_discrepancy, 1)}%) terverifikasi sinkron antar kedua sistem tersebut.")
    add_p("Selisih pengodean ini dipengaruhi oleh perbedaan ketetapan diagnosis utama dan pengabaian kaidah penggabungan diagnosis (multiple coding), "
          "sehingga berpotensi menggeser akurasi pengelompokan tingkat keparahan pada implementasi iDRG.")"""
          
    new_disc = """    add_p("d. Analisis Diskrepansi (Dual Coding)", bold=True)
    add_p("1. FAKTA")
    add_p(f"Komparasi input sistem INA-CBG versus iDRG menemukan diskrepansi (perbedaan) kode pada {discrepancy_count:,} berkas klaim ({perc_discrepancy}% dari populasi {total_kasus:,}).")
    add_p("2. HUBUNGAN DAN IMPLIKASI")
    add_p("Terjadinya selisih pengodean ini bersumber dari inkonsistensi penetapan diagnosis utama maupun pengabaian aturan penggabungan kode.")
    add_p("3. REKOMENDASI")
    add_p("Data selisih kode ini wajib diangkat sebagai materi investigasi prioritas pada fase On-Site Audit guna mencegah potensi up-coding yang akan mendistorsi beban iDRG.")"""
    
    content = content.replace(old_disc, new_disc)

    # 5. Fix Kasus Prioritas sorting for National report
    # We need to sort `onsite_cases` by tingkat risiko.
    # In generate_laporan_akhir_nasional.py around line 435: `for idx_os, case in enumerate(onsite_cases, 1):`
    old_onsite_loop = "for idx_os, case in enumerate(onsite_cases, 1):"
    new_onsite_loop = """def _risk_w(c):
        tr = str(c.get('tingkat_risiko', '')).lower()
        if tr == 'tinggi': return 3
        if tr == 'sedang': return 2
        return 1
    
    onsite_cases_sorted = sorted(onsite_cases, key=lambda x: (-_risk_w(x), str(x.get('nama_rs', ''))))
    for idx_os, case in enumerate(onsite_cases_sorted, 1):"""
    content = content.replace(old_onsite_loop, new_onsite_loop)
    
    # 6. Change column "Tingkat Risiko" fetching logic so it works if it's stored in tindakan_reviewer
    old_tk_risiko = "row_cells[4].text = str(fd_os.get('tingkat_risiko', case.get('tingkat_risiko', 'Tinggi')) or 'Tinggi')"
    new_tk_risiko = """
        tingkat_risk_val = str(fd_os.get('tingkat_risiko', case.get('tingkat_risiko', '')))
        if not tingkat_risk_val or tingkat_risk_val == '-': tingkat_risk_val = 'Tinggi'
        row_cells[4].text = tingkat_risk_val"""
    content = content.replace(old_tk_risiko, new_tk_risiko)


    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

refactor_nasional()
print("National Generator narrative refactored successfully.")
