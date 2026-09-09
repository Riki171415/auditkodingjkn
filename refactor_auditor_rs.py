import os
import re

def refactor_export_generator():
    file_path = "modules/export_generator.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. FIX PRIORITY CASES SORTING
    old_sorting = "priority_cases = cases_with_rules + cases_dc_only"
    new_sorting = """def _risk_weight(c):
        r = str(c.get('tingkat_risiko', '')).lower()
        if r == 'tinggi': return 3
        if r == 'sedang': return 2
        return 1
    priority_cases = sorted(cases_with_rules + cases_dc_only, key=lambda x: (-_risk_weight(x), -float(x.get('knavp_skor', 0) or 0)))"""
    content = content.replace(old_sorting, new_sorting)

    # 2. REWRITE NARASI GB (A. Gambaran Data)
    old_narasi_gb = """narasi_gb = (
        f"Berdasarkan hasil rekapitulasi data klaim {rs_name}, fasilitas kesehatan ini memiliki "
        f"total populasi sebanyak {total_rs:,} kasus. Dari populasi tersebut, ditarik sampel sebanyak "
        f"{len(cases)} kasus untuk dilakukan verifikasi melalui Kertas Kerja Review (KKR-DR01). "
        f"Setelah proses validasi selesai, didapatkan {onsite} kasus yang direkomendasikan untuk "
        f"pelaksanaan On-Site Audit, dan {sampling} kasus untuk Audit Sampling (Klarifikasi Administratif). "
        f"Sisa {monitor} kasus lainnya lolos validasi tanpa catatan khusus."
    )"""
    new_narasi_gb = """narasi_gb = (
        "1. FAKTA\\n"
        f"Populasi klaim elektronik {rs_name} berjumlah {total_rs:,} kasus. Sampel Cochran ditarik sebesar {len(cases)} kasus untuk dianalisis melalui instrumen KKR-DR01.\\n\\n"
        "2. HASIL TRIASE KNAVP\\n"
        f"Mesin validasi mengklasifikasikan hasil menjadi tiga luaran: {onsite} kasus direkomendasikan On-Site Audit, {sampling} kasus Audit Sampling, dan {monitor} kasus lolos validasi."
    )"""
    content = content.replace(old_narasi_gb, new_narasi_gb)
    
    # 3. REWRITE INTRO TEXT & NARASI MAP (C. Analisis Temuan)
    old_intro_text = """    if total_temuan_all > 0:
        top_rules = [k for k, v in sorted_rules if v == sorted_rules[0][1]]
        if len(top_rules) > 1:
            dominant_str = " dan ".join([", ".join(top_rules[:-1]), top_rules[-1]]) if len(top_rules) > 2 else " dan ".join(top_rules)
            dominant_count_str = f"masing-masing sebanyak {sorted_rules[0][1]} temuan"
        else:
            dominant_str = top_rules[0]
            dominant_count_str = f"sebanyak {sorted_rules[0][1]} temuan"
            
        other_rules = [f"{k} sebanyak {v} temuan" for k, v in sorted_rules if v < sorted_rules[0][1]]
        if other_rules:
            if len(other_rules) > 1:
                other_str = ", diikuti oleh " + ", ".join(other_rules[:-1]) + " dan " + other_rules[-1]
            else:
                other_str = ", diikuti oleh " + other_rules[0]
        else:
            other_str = ""
            
        intro_text = f"Mengevaluasi struktur peringatan (alerts) yang diterbitkan oleh sistem KNAVP dari {len(cases)} baris data elektronik yang dievaluasi pada {rs_name}, secara keseluruhan terdapat {total_temuan_all} peringatan ketidakwajaran. Dari seluruh peringatan tersebut, indikasi anomali yang paling dominan adalah {dominant_str} dengan {dominant_count_str}{other_str}. "
    else:
        intro_text = f"Berdasarkan hasil validasi elektronik KNAVP terhadap {len(cases)} kasus yang dievaluasi pada {rs_name}, tidak ditemukan adanya peringatan (alerts) pelanggaran logika sistem. "

    _narasi_map = {
        'mutually_exclusive':
            intro_text + "Peringatan ini mengindikasikan adanya input pengodean diagnosis yang secara eksplisit sudah termasuk (Includes) atau "
            "dikecualikan (Excludes) dalam kode lain berdasarkan logika sistem. "
            "Kondisi ini memerlukan pembuktian dokumen rekam medis fisik untuk menelusuri penegakan kaidah Includes/Excludes sesuai ICS.",
        'underlying_manifestation':
            intro_text + "Peringatan ini mengindikasikan adanya input kode manifestasi yang terekam tanpa underlying cause yang tepat secara sistem. "
            "Kondisi ini berpotensi memicu bias kompleksitas kasus yang dapat mempengaruhi akurasi grouping jika tidak diklarifikasi melalui bukti medis.",
        'procedure_validation':
            intro_text + "Peringatan ini mengindikasikan bahwa tindakan/prosedur medis diinput tanpa disertai kode diagnosis indikasi yang sepadan. "
            "Diperlukan verifikasi faktual terhadap laporan operasi untuk memastikan kelayakan tindakan yang diklaim.",
        'unbundling':
            intro_text + "Peringatan ini secara tipikal berkorelasi dengan sinyalemen pemecahan (unbundling) paket tindakan operasional. "
            "Karena tahap ini adalah Desk Review, kepastian terjadinya double-billing baru dapat disimpulkan setelah membandingkan data ini dengan laporan tindakan di lapangan.",
        'medical_evidence':
            intro_text + "Peringatan ini muncul akibat adanya klaim kode diagnosis berbobot tinggi (komplikasi/komorbiditas). "
            "Sistem mengindikasikan perlunya On-Site Audit guna memverifikasi apakah pencantuman kode berat tersebut benar-benar ditopang oleh hasil laboratorium dan anamnesis di lembar rekam medis pasien.",
        'administrative_validation':
            intro_text + "Peringatan ini mendeteksi anomali antara kode diagnosis klinis dengan data demografi administratif pasien (jenis kelamin/umur) di sistem elektronik. "
            "Diperlukan konfirmasi keabsahan identitas dan kesesuaian berkas administratif.",
        'age_validation':
            intro_text + "Peringatan ini mengindikasikan ketidaksinkronan kode diagnosis terhadap rentang kelompok umur pasien secara sistem. "
            "Diperlukan validasi administratif tanggal lahir pasien.",
        'los_validation':
            intro_text + "Peringatan ini menyoroti lama rawat (LOS) yang terekam melebihi ambang batas kewajaran algoritma. "
            "Hal ini melahirkan pertanyaan krusial yang harus dijawab di lapangan mengenai ada tidaknya justifikasi medis tertulis yang memperpanjang masa rawat.",
    }
    _default_narasi = (
        intro_text + "Karena Desk Review tidak memiliki otoritas untuk melihat wujud fisik rekam medis, peringatan ini tidak lantas membuktikan rumah sakit bersalah, melainkan mengarahkan fokus investigasi lanjutan."
    )
    add_p(_narasi_map.get(dom_kat, _default_narasi), align=3, size_pt=12, space_after_pt=6)
    add_p(
        "Secara agregat, sebaran peringatan elektronik ini berpotensi merugikan ketahanan dana JKN akibat pergeseran tingkat keparahan (CCL/PCCL). "
        "Berdasarkan hal tersebut, temuan data ini akan menjadi acuan utama bagi auditor dalam meminta dokumen pembuktian (medical evidence) dari manajemen rumah sakit pada tahap lanjutan.",
        align=3, size_pt=12, space_after_pt=8
    )"""

    new_intro_text = """    if total_temuan_all > 0:
        top_rules = [k for k, v in sorted_rules if v == sorted_rules[0][1]]
        dominant_str = top_rules[0] if len(top_rules) > 0 else "-"
        dominant_count = sorted_rules[0][1] if len(sorted_rules) > 0 else 0
        intro_text = (
            "1. FAKTA\\n"
            f"Eksekusi algoritma KNAVP pada {len(cases)} kasus sampel elektronik {rs_name} mengidentifikasi {total_temuan_all} rekaman peringatan anomali koding. "
            f"Klaster temuan tertinggi terdapat pada aturan {dominant_str} ({dominant_count} kejadian).\\n\\n"
        )
    else:
        intro_text = (
            "1. FAKTA\\n"
            f"Algoritma KNAVP tidak mengidentifikasi adanya peringatan (0 anomali koding) pada {len(cases)} kasus elektronik yang dievaluasi.\\n\\n"
        )

    _narasi_map = {
        'mutually_exclusive':
            "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
            "Anomali Mutually Exclusive menunjukkan pencatatan kode diagnosis sekunder yang secara kaidah ICD (Includes/Excludes) seharusnya terintegrasi dengan diagnosis primer. Hal ini mengindikasikan ketidaksesuaian input administratif dengan pedoman ICS.\\n\\n"
            "3. IMPLIKASI AUDIT\\n"
            "Adanya anomali ini menimbulkan risiko over-coding yang dapat merubah struktur PCCL. Validasi absolut mensyaratkan pencocokan dokumen fisik (On-Site Audit) guna memastikan apakah komorbiditas benar-benar dirawat sesuai sumber daya klinis.",
        
        'underlying_manifestation':
            "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
            "Anomali Manifestation mengindikasikan klaim atas kode diagnosis sekunder (manifestasi) tanpa disertai penyebab dasar (underlying cause) yang sah. Hal ini menyebabkan ketidaklengkapan syarat kelayakan administratif kode tersebut.\\n\\n"
            "3. IMPLIKASI AUDIT\\n"
            "Penggunaan kode manifestasi soliter berpotensi menimbulkan bias klaim. Rekam medis lapangan harus diperiksa untuk memverifikasi apakah manifestasi tersebut lahir dari penyakit kausal yang terdokumentasi (dagger & asterisk).",
            
        'procedure_validation':
            "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
            "Anomali Procedure mengisyaratkan adanya klaim tarif prosedur operasional/tindakan tanpa dukungan kode diagnosis medis yang menjustifikasi tindakan tersebut.\\n\\n"
            "3. IMPLIKASI AUDIT\\n"
            "Hal ini memunculkan risiko pembayaran yang tidak wajar. On-Site Audit diperlukan guna mengevaluasi kelengkapan Lembar Laporan Operasi dan asesmen DPJP sebagai basis penetapan urgensi tindakan medis.",
            
        'unbundling':
            "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
            "Anomali Unbundling menunjukkan praktik pemisahan tagihan dari sebuah paket tindakan medis ke dalam beberapa kode yang berdiri sendiri (komponen terpisah).\\n\\n"
            "3. IMPLIKASI AUDIT\\n"
            "Pemecahan paket ini berisiko tinggi terhadap duplikasi pembayaran klaim. Pemeriksaan mendalam pada Catatan Terintegrasi (CPPT) diperlukan guna membuktikan ada/tidaknya justifikasi medis yang membedakan tindakan tersebut.",
            
        'medical_evidence':
            "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
            "Anomali Medical Evidence terpicu ketika terdapat klaim berbobot tingkat keparahan (CCL/PCCL) tinggi namun profil logis pasien di sistem tidak sejalan dengan komorbiditas tersebut.\\n\\n"
            "3. IMPLIKASI AUDIT\\n"
            "Bukti laboratorium, patologi, maupun pemeriksaan penunjang lainnya dalam rekam medis fisik bersifat mutlak (mandatory) untuk diperiksa auditor guna mencegah kerugian dana JKN akibat Up-Coding tak berdasar.",
            
        'administrative_validation':
            "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
            "Anomali Administratif merekam ketidaksinkronan spesifik antara diagnosis klinis dengan jenis kelamin (seperti diagnosis maternal pada laki-laki).\\n\\n"
            "3. IMPLIKASI AUDIT\\n"
            "Ini mengisyaratkan kesalahan entri data (clerical error). Penyelesaian klaim hanya dapat dilanjutkan apabila RS melakukan perbaikan administrasi demografi yang terverifikasi.",
            
        'age_validation':
            "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
            "Anomali Age merekam ketidaksesuaian diagnosis penyakit terhadap rentang usia pasien (misalnya, diagnosis neonatal pada pasien dewasa).\\n\\n"
            "3. IMPLIKASI AUDIT\\n"
            "Fakta ini menghambat penyelesaian klaim secara logis. Perbaikan rekam administratif maupun verifikasi akta medis di lapangan diperlukan guna meluruskan identitas klinis.",
            
        'los_validation':
            "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
            "Anomali LOS menyoroti Length of Stay pasien yang secara algoritma jauh melampaui batasan masa rawat standar nasional (ALOS) tanpa justifikasi di diagnosis tambahan.\\n\\n"
            "3. IMPLIKASI AUDIT\\n"
            "Perpanjangan hari rawat meningkatkan biaya hoteling/tagihan tambahan. Auditor lapangan ditugaskan untuk menelusuri kelayakan medis yang menyebabkan durasi masa rawat pasien tersebut memanjang."
    }
    
    _default_narasi = (
        "2. HUBUNGAN DAN IMPLIKASI ADMINISTRATIF\\n"
        "Anomali elektronik terdeteksi, merepresentasikan kelemahan akurasi input data pada sistem INA-CBG yang belum sepenuhnya patuh terhadap panduan ICS.\\n\\n"
        "3. IMPLIKASI AUDIT\\n"
        "Batas verifikasi desk review (ketiadaan wujud fisik rekam medis) menempatkan temuan ini sebagai sinyal indikatif murni. Pemeriksaan silang di lapangan (On-Site Audit) diperlukan."
    )
    
    final_text = intro_text + _narasi_map.get(dom_kat, _default_narasi) if total_temuan_all > 0 else intro_text + "2. IMPLIKASI ADMINISTRATIF\\nKasus yang tidak memiliki anomali algoritma diproyeksikan aman secara administratif.\\n\\n3. IMPLIKASI AUDIT\\nTidak ada bukti sistemik yang mendesak untuk pelaksanaan On-Site Audit atas kasus-kasus tanpa peringatan KNAVP."
    
    # Split text into paragraphs based on double newlines
    paragraphs = final_text.split('\\n\\n')
    for p_text in paragraphs:
        if p_text.strip():
            add_p(p_text.strip(), align=3, size_pt=12, space_after_pt=8)"""
            
    content = content.replace(old_intro_text, new_intro_text)
    
    # 4. REWRITE BAB III (A. Kesimpulan)
    old_kesimpulan = """    if dom_kat == '-' or total_temuan_all == 0:
        add_p(f"Evaluasi Desk Review berbasis data elektronik terhadap {len(cases)} sampel klaim {rs_name} memberikan simpulan diagnostik awal bahwa data yang diinput ke sistem sebagian besar teridentifikasi tidak memiliki anomali logika. Namun validitas klinis absolut tetap bergantung pada ketersediaan dokumen fisik jika sewaktu-waktu dilakukan audit lapangan.", align=3, size_pt=12, space_after_pt=8)
    else:
        add_p(
            f"Evaluasi Desk Review berbasis data elektronik terhadap {len(cases)} sampel klaim {rs_name} menyimpulkan bahwa masih terdapat indikasi anomali logika klinis, terutama pada {dom_label}. "
            f"Dinamika ini diperparah oleh munculnya angka diskrepansi simulasi dual coding antara mesin INA-CBG dan iDRG. "
            f"{'Mengingat sebagian data terdeteksi memiliki profil risiko tinggi secara sistem, maka verifikasi absolut atas temuan ini kini bergantung sepenuhnya pada kehadiran dan keabsahan dokumen rekam medis fisik di rumah sakit saat On-Site Audit dilaksanakan kelak.' if onsite > 0 else 'Meskipun anomali sistemik bersifat administratif (risiko rendah), penyelarasan kompetensi koder tetap disyaratkan sebagai mitigasi kelengkapan dokumen pendukung.'}",
            align=3, size_pt=12, space_after_pt=8
        )"""
    new_kesimpulan = """    if dom_kat == '-' or total_temuan_all == 0:
        add_p(f"Analisis elektronik atas {len(cases)} sampel klaim {rs_name} membuktikan tidak adanya pelanggaran algoritma KNAVP. Fakta ini merepresentasikan kapatuhan awal yang memadai secara administratif. Meskipun demikian, simpulan diagnostik murni tidak dapat dilepaskan dari uji fisik lapangan, sehingga kesesuaian klinis di masa depan tetap harus dibuktikan jika diperlukan.", align=3, size_pt=12, space_after_pt=8)
    else:
        add_p(f"Hasil ekstraksi dan validasi data secara elektronik mengonfirmasi keberadaan {total_temuan_all} anomali koding, dengan pusat deviasi pada kelompok {dom_label}. Fakta ini memiliki hubungan kausal langsung dengan diskrepansi dual-coding sistem. Sebagai implikasi manajerial, temuan berisiko tinggi wajib ditindaklanjuti secara faktual guna menghindari pembayaran klaim yang tidak tepat sasaran.", align=3, size_pt=12, space_after_pt=8)"""
    content = content.replace(old_kesimpulan, new_kesimpulan)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
refactor_export_generator()
print("RS Generator narrative refactored successfully.")
