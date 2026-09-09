import os

file_path = "modules/export_generator.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace KATA PENGANTAR (Line 1105+)
old_kp_1 = '''add_p(
        "Puji syukur kami panjatkan ke hadirat Tuhan Yang Maha Esa atas rahmat-Nya, sehingga Laporan Hasil Desk Review Audit Coding ini dapat diselesaikan. Laporan ini merupakan wujud nyata upaya monitoring dan evaluasi terhadap kualitas pengodean medis di tingkat fasilitas kesehatan yang melayani peserta JKN.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
new_kp_1 = '''add_p(
        "Puji syukur senantiasa dihaturkan ke hadirat Tuhan Yang Maha Esa atas rahmat dan karunia-Nya, sehingga penyusunan Laporan Hasil Desk Review Audit Coding: Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG) dapat diselesaikan sesuai dengan tata waktu yang ditetapkan. Dokumen ini merupakan instrumen strategis Kementerian Kesehatan Republik Indonesia dalam mengawal akuntabilitas penyelenggaraan Jaminan Kesehatan Nasional (JKN), khususnya pada fase krusial transisi sistem pembiayaan fasilitas kesehatan tingkat lanjut.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
content = content.replace(old_kp_1, new_kp_1)

old_kp_2 = '''add_p(
        "Laporan ini menyajikan analisis komprehensif terkait kesesuaian klaim elektronik dengan kaidah baku Indonesian Coding Standard (ICS), serta aturan validasi yang tercantum dalam Katalog Nasional Aturan Validasi Pengodean (KNAVP).",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
new_kp_2 = '''add_p(
        "Laporan ini memuat hasil penelaahan tahap awal (Desk Review) yang murni bersumber pada evaluasi data klaim elektronik, tanpa melakukan validasi terhadap dokumen fisik rekam medis. Melalui pemanfaatan mesin aturan Katalog Nasional Aturan Validasi Pengodean (KNAVP), tim reviewer telah memetakan profil indikasi risiko, mendeteksi anomali pengodean secara sistem, serta menganalisis diskrepansi dual coding antara sistem INA-CBG eksisting dengan simulasi iDRG. Hasil analisis data ini berfungsi sebagai early warning system dan dasar penetapan skala prioritas bagi pelaksanaan verifikasi lanjutan.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
content = content.replace(old_kp_2, new_kp_2)

old_kp_3 = '''add_p(
        "Akhir kata, kami mengucapkan terima kasih kepada seluruh pihak yang telah berpartisipasi dan kooperatif selama proses penyediaan data klaim dan rekam medis. Semoga laporan ini dapat menjadi bahan evaluasi yang membangun untuk perbaikan tata kelola koding di rumah sakit.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
new_kp_3 = '''add_p(
        "Apresiasi yang tinggi disampaikan kepada seluruh jajaran manajemen rumah sakit atas kooperativitas pengiriman data secara digital. Laporan ini diharapkan mampu memberikan gambaran awal berbasis bukti administratif guna memformulasikan arah investigasi lanjutan melalui On-Site Audit, serta mengoptimalkan kesiapan fasilitas kesehatan dalam menyongsong implementasi penuh sistem iDRG.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
content = content.replace(old_kp_3, new_kp_3)

# Replace BAB I PENDAHULUAN
old_latar = '''add_p(
        "Dalam masa transisi sistem penjaminan dari INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG), keakuratan pengodean diagnosis dan prosedur oleh perekam medis dan informasi kesehatan (PMIK) menjadi pilar utama pengelolaan pembiayaan kesehatan. Untuk memastikan kualitas data klaim serta mencegah ketidaksesuaian pengodean, dilakukan verifikasi tahap awal melalui metode Desk Review.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
new_latar = '''add_p(
        "Transformasi arsitektur sistem pembiayaan kesehatan nasional dari INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG) mensyaratkan tingkat akurasi dan granularitas data klinis yang sangat tinggi. Sistem iDRG dirancang untuk lebih sensitif dalam menangkap kompleksitas morbiditas pasien, sehingga setiap penambahan kode diagnosis sekunder maupun prosedur akan memiliki probabilitas besar untuk menggeser level keparahan klinis (PCCL) dan besaran tarif kompensasi. Di tengah fase transisi ini, kualitas pengodean medis (clinical coding) yang tercatat pada database fasilitas kesehatan menjadi parameter paling fundamental untuk memproyeksikan efisiensi alokasi dana Jaminan Kesehatan Nasional (JKN).",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )
    add_p(
        "Kementerian Kesehatan Republik Indonesia, melalui Pusat Pembiayaan Kesehatan, memiliki mandat krusial untuk memetakan integritas data klaim tersebut secara dini. Sebagai instrumen penyaringan awal (screening), mekanisme Audit Koding berbasis Desk Review diselenggarakan untuk menganalisis data secara elektronik guna mendeteksi tren anomali penagihan sebelum auditor diterjunkan ke lapangan. Evaluasi ini diperlukan untuk memastikan kelancaran tahap On-Site Audit kelak, dengan memetakan terlebih dahulu data mana saja yang memiliki indikasi ketidakselarasan logika medis berdasarkan sistem.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
content = content.replace(old_latar, new_latar)

old_tujuan_4 = '''("d.", "merumuskan rekomendasi perbaikan kualitas pengodean di tingkat fasilitas kesehatan.")'''
new_tujuan_4 = '''("d.", "menetapkan stratifikasi risiko atas populasi sampel untuk memandu target dan ruang lingkup pelaksanaan penelusuran dokumen fisik (On-Site Audit) di tahap selanjutnya.")'''
content = content.replace(old_tujuan_4, new_tujuan_4)


old_ruang_lingkup = '''add_p(
        f"Ruang lingkup pelaksanaan Desk Review pada {rs_name} (Kode RS: {kode_rs}) mencakup data klaim pelayanan "
        f"kesehatan periode Januari - Desember 2025. Total kasus klaim keseluruhan adalah {ri_rs:,} kasus Rawat Inap "
        f"dan {rj_rs:,} kasus Rawat Jalan, dengan sampel Cochran yang direviu sebanyak {sample_cochran_ri} kasus Rawat Inap "
        f"dan {sample_cochran_rj} kasus Rawat Jalan (total sampel: {sample_cochran_ri + sample_cochran_rj} kasus).",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
new_ruang_lingkup = '''add_p(
        f"Objek penelaahan dalam laporan ini secara mutlak dibatasi pada pangkalan data klaim JKN elektronik (Rawat Jalan dan Rawat Inap) yang diterbitkan oleh {rs_name} (Kode RS: {kode_rs}) selama periode layanan 1 Januari hingga 31 Desember 2025. Total populasi klaim adalah {ri_rs:,} kasus Rawat Inap dan {rj_rs:,} kasus Rawat Jalan, dengan sampel Cochran sejumlah {sample_cochran_ri + sample_cochran_rj} kasus.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )
    add_p(
        "Laporan ini merupakan hasil evaluasi sekunder (desk review) yang murni menelaah kewajaran relasi antara kode diagnosis dan kode prosedur secara elektronik. Pada tahapan ini, auditor sama sekali belum melakukan tinjauan terhadap dokumen fisik rekam medis pasien di fasilitas kesehatan. Oleh karena itu, seluruh temuan dalam laporan ini berstatus sebagai 'indikasi anomali' yang memerlukan klarifikasi dan validasi faktual lebih lanjut.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )'''
content = content.replace(old_ruang_lingkup, new_ruang_lingkup)


# BAB II A. Gambaran Data
old_gambaran_data = '''narasi_gb = (
        f"Total sampel yang direviu di {rs_name} berjumlah {len(cases)} kasus, "
        f"yang terdiri atas {sampel_rj} kasus Rawat Jalan dan {sampel_ri} kasus Rawat Inap. "
        "Seluruh kasus tersebut telah melalui tahap verifikasi sistem KNAVP guna menilai kepatuhan terhadap kaidah koding nasional."
    )
    add_p(narasi_gb, align=3, size_pt=12, space_after_pt=12)'''
new_gambaran_data = '''narasi_gb_1 = (
        f"Langkah inisial dari pelaksanaan Desk Review adalah menyerap postur beban klaim digital yang dikelola oleh {rs_name}. "
        f"Pada periode evaluasi tahun 2025, rumah sakit mencatatkan volume pelayanan Rawat Jalan sebanyak {rj_rs:,} kasus dan Rawat Inap sebanyak {ri_rs:,} kasus. "
        "Kepadatan lalu lintas data ini niscaya membawa risiko clerical error atau kesalahan input apabila kendali mutu rumah sakit tidak berjalan spartan."
    )
    narasi_gb_2 = (
        f"Untuk mendapatkan parameter awal terkait kualitas data tersebut, tim verifikator mengekstraksi sampel uji petik sebanyak {len(cases)} kasus ({sampel_rj} Rawat Jalan, {sampel_ri} Rawat Inap). "
        "Pemilihan sampel ini dikalkulasi untuk memberikan gambaran baseline terkait probabilitas galat pengodean elektronik pada seluruh spektrum layanan. "
        "Auditor menggunakan sampel ini untuk menilai sejauh mana data yang diinput ke sistem INA-CBG secara logis masuk akal sebelum dicocokkan dengan lembar observasi riil pasien kelak."
    )
    add_p(narasi_gb_1, align=3, size_pt=12, space_after_pt=6)
    add_p(narasi_gb_2, align=3, size_pt=12, space_after_pt=12)'''
content = content.replace(old_gambaran_data, new_gambaran_data)

# BAB II B. Hasil Validasi
old_hasil_validasi = '''add_p(
        f"Berdasarkan evaluasi sistem KNAVP terhadap {len(cases)} berkas klaim, "
        f"sebanyak {onsite} kasus direkomendasikan untuk On-Site Audit, {sampling} kasus untuk Audit Sampling, "
        f"serta {monitor} kasus lolos validasi tanpa anomali. Rincian stratifikasi ini menjadi dasar penentuan tindak lanjut.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=12
    )'''
new_hasil_validasi = '''add_p(
        f"Setelah {len(cases)} baris data sampel dilewatkan pada instrumen KNAVP, sistem mengeksekusi fungsi triase untuk memetakan profil risiko. "
        f"Data dengan kekosongan parameter administratif diarahkan pada Audit Sampling ({sampling} kasus), "
        f"data yang menunjukkan kombinasi kode tidak lazim dieskalasi secara mandatory menuju On-Site Audit ({onsite} kasus), "
        f"dan data yang lolos uji logika diarahkan pada Monitoring ({monitor} kasus).",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )
    add_p(
        "Sistem triase ini memastikan auditor di lapangan kelak tidak menghabiskan waktu pada kasus yang wajar, melainkan fokus pada berkas yang menunjukkan indikasi red flag secara elektronik.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=12
    )'''
content = content.replace(old_hasil_validasi, new_hasil_validasi)

# BAB II C. Analisis Temuan
old_analisis_temuan = '''add_p(
        f"Hasil validasi KNAVP terhadap {len(cases)} kasus yang direviu pada {rs_name}, "
        f"secara keseluruhan terdapat {total_temuan_all} temuan pelanggaran aturan. "
        f"Dari seluruh pelanggaran tersebut, kelompok temuan paling dominan adalah {dom_label} sebanyak {dom_count} temuan. "
        "Temuan-temuan ini memerlukan klarifikasi lebih lanjut terhadap rekam medis dan pengodean sesuai panduan ICS dan kaidah koding nasional yang berlaku.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=12
    )'''
new_analisis_temuan = '''add_p(
        f"Membongkar struktur peringatan (alerts) yang diterbitkan oleh sistem KNAVP dari {len(cases)} baris data yang dievaluasi pada {rs_name}, "
        f"terdapat {total_temuan_all} peringatan ketidakwajaran yang terlontar. "
        f"Indikasi pelanggaran paling dominan terdeteksi pada aturan {dom_label} dengan {dom_count} peringatan. "
        "Karena Desk Review tidak memiliki otoritas untuk melihat wujud fisik rekam medis, peringatan ini tidak lantas membuktikan rumah sakit bersalah, melainkan melahirkan pertanyaan krusial yang harus dijawab di lapangan.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=12
    )'''
content = content.replace(old_analisis_temuan, new_analisis_temuan)

old_tindak_lanjut = '''add_p(
        "Temuan-temuan ini memiliki dampak langsung terhadap ketepatan pengelompokan INA-CBG maupun simulasi iDRG "
        "(termasuk penentuan tingkat keparahan CCL/PCCL). Oleh karena itu, diperlukan tindak lanjut terarah "
        "berupa verifikasi langsung maupun pembinaan berkelanjutan terhadap petugas koder dan pemberi layanan.",
        align=3, size_pt=12, space_after_pt=12
    )'''
new_tindak_lanjut = '''add_p(
        "Secara agregat, sebaran peringatan elektronik ini berpotensi merugikan ketahanan dana JKN akibat ilusi kompleksitas kasus. "
        "Oleh sebab itu, temuan data ini akan menjadi 'buku panduan' utama bagi auditor medis dalam meminta dokumen pembuktian (medical evidence) dari manajemen rumah sakit pada tahapan On-Site Audit selanjutnya.",
        align=3, size_pt=12, space_after_pt=12
    )'''
content = content.replace(old_tindak_lanjut, new_tindak_lanjut)

# BAB II D. Kasus Prioritas
old_kasus_prioritas = '''add_p(
        f"Berdasarkan analisis risiko, ditetapkan {onsite} berkas klaim sebagai Kasus Prioritas yang diwajibkan untuk "
        "menjalani On-Site Audit. Kasus dalam kategori ini terindikasi melakukan penyimpangan pengodean berat "
        "yang dapat memengaruhi eskalasi tarif secara manipulatif. Pembuktian dokumen medis fisik sangat krusial "
        "untuk menindaklanjuti temuan ini.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=12
    )'''
new_kasus_prioritas = '''add_p(
        f"Berdasarkan stratifikasi risiko sistem, {onsite} data klaim terkategori sebagai Kasus Prioritas Tingkat Tinggi. "
        "Data elektronik pada kasus ini menunjukkan profil penyusunan kode yang sangat tidak lazim. "
        "Sebagai tahapan Desk Review, tim verifikator tidak diperkenankan menarik kesimpulan absolut atas niat fasilitas kesehatan. "
        "Oleh karena itu, kasus prioritas ini ditetapkan sebagai mandatory requirement untuk dibuktikan faktanya melalui On-Site Audit.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )
    add_p(
        "Di lapangan kelak, lembar observasi dan resume medis pasien akan disandingkan secara head-to-head dengan deretan kode yang diinput di dalam sistem. "
        "Jika bukti medis riil tersedia secara valid, status anomali akan digugurkan. Sebaliknya, ketiadaan bukti akan berujung pada tindakan korektif pembiayaan.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=12
    )'''
content = content.replace(old_kasus_prioritas, new_kasus_prioritas)

# BAB II E. Discrepancy Dual Coding
old_discrepancy = '''narasi_e = (
        f"Berdasarkan hasil evaluasi terhadap {len(cases)} berkas klaim di {rs_name}, "
        f"ditemukan sebanyak {dc_count} klaim atau {dc_perc}% yang mengalami ketidaksesuaian antara "
        f"input diagnosis atau tindakan pada sistem INA-CBG dan iDRG, dengan total keseluruhan mencapai {total_dc_beda} perbedaan kode medis. "
        f"Sebaliknya, sebanyak {len(cases)-dc_count} klaim atau {round(100-dc_perc, 1)}% sisanya telah menunjukkan kesesuaian data input antara kedua sistem tersebut."
    )
    add_p(narasi_e, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8)'''
new_discrepancy = '''narasi_e_1 = (
        "Merespons agenda transisi menuju metode pembiayaan iDRG, instrumen Desk Review ini turut melakukan simulasi beban ganda (dual coding) untuk mengukur tingkat ekuilibrium sistem. "
        "Uji ini dilakukan secara statis dengan menandingkan deretan kode ICD yang ditransmisikan rumah sakit di platform INA-CBG terhadap algoritma restriktif dari grouper iDRG."
    )
    narasi_e_2 = (
        f"Hasil analisis menyingkap bahwa dari total {len(cases)} data sampel di {rs_name}, sebanyak {dc_count} rangkaian data klaim ({dc_perc}%) "
        f"mengalami diskrepansi penolakan atau eskalasi berbeda oleh sistem iDRG (akumulasi {total_dc_beda} perbedaan kode medis). "
        f"Sementara itu, hanya {len(cases)-dc_count} kasus ({round(100-dc_perc, 1)}%) yang berhasil dikelompokkan dengan sinkron. "
        "Tingginya diskrepansi ini menyingkap tabir bahwa grouper iDRG mendeteksi adanya kode sekunder yang dinilai tidak relevan atau kekurangan spesifisitas dibanding saat melewati saringan INA-CBG."
    )
    add_p(narasi_e_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=6)
    add_p(narasi_e_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8)'''
content = content.replace(old_discrepancy, new_discrepancy)

# BAB III Kesimpulan
old_kesimpulan_1 = '''add_p(f"Pelaksanaan Desk Review terhadap data klaim {rs_name} menyimpulkan bahwa dari {len(cases)} kasus sampel yang diperiksa, kualitas pengodean telah terbukti sangat baik dan mematuhi aturan standar tanpa ada deteksi ketidaksesuaian berarti.", align=3, size_pt=12, space_after_pt=8)'''
new_kesimpulan_1 = '''add_p(f"Evaluasi Desk Review berbasis data elektronik terhadap {len(cases)} sampel klaim {rs_name} memberikan simpulan diagnostik awal bahwa data yang diinput ke sistem sebagian besar teridentifikasi tidak memiliki anomali logika. Namun validitas klinis absolut tetap bergantung pada ketersediaan dokumen fisik jika sewaktu-waktu dilakukan audit lapangan.", align=3, size_pt=12, space_after_pt=8)'''
content = content.replace(old_kesimpulan_1, new_kesimpulan_1)

old_kesimpulan_2 = '''add_p(
            f"Pelaksanaan Desk Review terhadap data klaim {rs_name} menyimpulkan bahwa dari {len(cases)} kasus sampel yang diperiksa, terdapat indikasi ketidaksesuaian pengodean yang memerlukan perhatian khusus, terutama pada kelompok aturan {dom_label}. "
            f"{'Sebagian kasus memiliki tingkat risiko tinggi terhadap kewajaran tarif dan pengelompokan iDRG, sehingga validasi lanjutan mutlak diperlukan untuk memastikan kesesuaian antara klaim dengan dokumen rekam medis pasien.' if onsite > 0 else 'Mayoritas kasus dikategorikan ke dalam risiko rendah atau lolos validasi, namun perbaikan dan pembinaan koding tetap diperlukan.'}",
            align=3, size_pt=12, space_after_pt=8
        )'''
new_kesimpulan_2 = '''add_p(
            f"Evaluasi Desk Review berbasis data elektronik terhadap {len(cases)} sampel klaim {rs_name} menyimpulkan bahwa masih terdapat indikasi anomali logika klinis, terutama pada {dom_label}. "
            f"Dinamika ini diperparah oleh munculnya angka diskrepansi simulasi dual coding antara mesin INA-CBG dan iDRG. "
            f"{'Mengingat sebagian data terdeteksi memiliki profil risiko tinggi secara sistem, maka verifikasi absolut atas temuan ini kini bergantung sepenuhnya pada kehadiran dan keabsahan dokumen rekam medis fisik di rumah sakit saat On-Site Audit dilaksanakan kelak.' if onsite > 0 else 'Meskipun anomali sistemik bersifat administratif (risiko rendah), penyelarasan kompetensi koder tetap disyaratkan sebagai mitigasi kelengkapan dokumen pendukung.'}",
            align=3, size_pt=12, space_after_pt=8
        )'''
content = content.replace(old_kesimpulan_2, new_kesimpulan_2)

# BAB III Rekomendasi
old_rekomendasi_1 = '''rekom_items = [
        ("●", "tidak diperlukan tindak lanjut bagi kasus yang lolos validasi tanpa catatan;")
    ]'''
new_rekomendasi_1 = '''rekom_items = [
        ("●", "penyelesaian proses administratif klaim lanjutan bagi kasus yang teridentifikasi bersih dari anomali logika sistem;")
    ]'''
content = content.replace(old_rekomendasi_1, new_rekomendasi_1)

old_rekomendasi_2 = '''rekom_items.append(("●", "klarifikasi kepada DPJP terkait kelengkapan bukti medis penunjang diagnosis secondary/komplikasi serta validitas tindakan;"))'''
new_rekomendasi_2 = '''rekom_items.append(("●", "penugasan Tim Casemix untuk menyediakan bukti konfirmasi ketersediaan medical evidence di rekam medis fisik guna menutupi celah peringatan (alerts) sistem;"))'''
content = content.replace(old_rekomendasi_2, new_rekomendasi_2)

old_rekomendasi_3 = '''rekom_items.append(("●", "pelaksanaan On-Site Audit segera terhadap kasus-kasus prioritas untuk memastikan kesesuaian dokumen medis fisik."))'''
new_rekomendasi_3 = '''rekom_items.append(("●", "pengerahan auditor lapangan (On-Site) untuk membedah rekam medis fisik dari kasus-kasus prioritas tinggi, guna membuktikan secara faktual kebenaran klaim yang terdeteksi anomali oleh sistem."))'''
content = content.replace(old_rekomendasi_3, new_rekomendasi_3)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("File updated successfully.")
