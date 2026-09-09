import re

def fix_all():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Part 1: Replace the narrative in Kesesuaian Input
    target_block = """    else:
        add_p(
            f"Dari keseluruhan {total_kasus} tagihan pasien yang diperiksa di {rs_name}, ada {kasus_beda} tagihan "
            f"({round(kasus_beda/total_kasus*100,1)}%) yang catatan penyakit atau tindakannya berbeda antara yang "
            f"diklaimkan oleh rumah sakit (INA-CBG) dengan hasil evaluasi sistem (iDRG). "
            f"Secara keseluruhan, ditemukan {total_beda_kode} perbedaan kode medis.\\n"
            f"Sebaliknya, terdapat {kasus_sesuai} tagihan ({match_rate}%) yang sudah cocok sepenuhnya tanpa selisih.\\n\\n"
            f"Berikut adalah profil ringkas akurasi pengodean medis di rumah sakit ini:",
            align=3, size_pt=12, space_after_pt=6
        )

        tbl_summary = document.add_table(rows=4, cols=3)
        tbl_summary.style = 'Table Grid'
        
        h_cells = tbl_summary.rows[0].cells
        h_cells[0].text = "Parameter Dual Coding (Pengecualian Kode Admin KND, DH, HL)"
        h_cells[1].text = "Hasil Evaluasi"
        h_cells[2].text = "Analisis Dampak"
        for i in range(3):
            for run in h_cells[i].paragraphs[0].runs:
                run.bold = True
                run.font.size = Pt(10)
            h_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        r1 = tbl_summary.rows[1].cells
        r1[0].text = "Tingkat Kesesuaian Diagnosis Bersih (Clean Match Rate)"
        r1[1].text = f"{match_rate}% ({kasus_sesuai} Kasus)"
        r1[2].text = f"{kasus_sesuai} kasus selaras penuh (tanpa selisih diagnosis/prosedur klinis antara INA-CBG dan iDRG)"
        
        r2 = tbl_summary.rows[2].cells
        r2[0].text = "Kasus dengan Discrepancy Diagnosis Klinis"
        r2[1].text = f"{round(kasus_beda/total_kasus*100,1)}% ({kasus_beda} Kasus)"
        r2[2].text = f"Terdapat {total_beda_kode} total perbedaan kode klinis pada {kasus_beda} kasus yang memerlukan verifikasi dual coding"
        
        _berisiko_count = sum(1 for c in cases if str(c.get('tingkat_risiko', '')) == 'Tinggi' or 'On-Site' in str(c.get('keputusan_sistem', '')))
        _ccl_shift_count = 0
        perc_ccl = round(_ccl_shift_count / _berisiko_count * 100, 1) if _berisiko_count > 0 else 0.0
        
        r3 = tbl_summary.rows[3].cells
        r3[0].text = "Proyeksi Pergeseran Tingkat Keparahan (Severity Level)"
        r3[1].text = f"{perc_ccl}% ({_ccl_shift_count} dari {_berisiko_count} Kasus Berisiko)"
        r3[2].text = "Berpotensi turun tingkat keparahan jika diagnosis tambahan (komorbid/komplikasi) tidak terbukti saat On-Site Audit"
        
        for row in tbl_summary.rows[1:]:
            for i in range(3):
                for run in row.cells[i].paragraphs[0].runs:
                    run.font.size = Pt(10)
                if i == 1:
                    row.cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        add_p("", space_after_pt=12)"""

    new_block = """    else:
        add_p(
            f"Berdasarkan hasil evaluasi terhadap {total_kasus} tagihan pasien di {rs_name}, ditemukan sebanyak {kasus_beda} tagihan atau {round(kasus_beda/total_kasus*100,1)}% yang mengalami ketidaksesuaian antara input diagnosis atau tindakan pada sistem INACBG dan iDRG, dengan total keseluruhan mencapai {total_beda_kode} perbedaan kode medis. Sebaliknya, sebanyak {kasus_sesuai} tagihan atau {match_rate}% sisanya telah menunjukkan kesesuaian data input antara kedua sistem tersebut.",
            align=3, size_pt=12, space_after_pt=6
        )
        add_p(
            "Dari hasil pengecekan terhadap catatan medis di rumah sakit ini (setelah mengesampingkan kode administrasi), berikut adalah gambaran tingkat ketelitian dan kesesuaian kodenya:",
            align=3, size_pt=12, space_after_pt=6
        )

        _berisiko_count = sum(1 for c in cases if str(c.get('tingkat_risiko', '')) == 'Tinggi' or 'On-Site' in str(c.get('keputusan_sistem', '')))
        _ccl_shift_count = 0
        perc_ccl = round(_ccl_shift_count / _berisiko_count * 100, 1) if _berisiko_count > 0 else 0.0

        p1 = document.add_paragraph()
        p1.add_run(f"Kasus yang Sudah Cocok ({match_rate}% atau {kasus_sesuai} pasien): ").bold = True
        p1.add_run("Penulisan kode penyakit dan tindakan untuk pasien-pasien ini sudah sinkron dan benar sepenuhnya antara sistem INA-CBG dan iDRG tanpa ada perbedaan sama sekali.")
        p1.style = 'List Bullet'
        for r in p1.runs: r.font.size = Pt(12)

        p2 = document.add_paragraph()
        p2.add_run(f"Kasus yang Perlu Dicek Ulang ({round(kasus_beda/total_kasus*100,1)}% atau {kasus_beda} pasien): ").bold = True
        p2.add_run(f"Pada kelompok ini ditemukan perbedaan kode penyakit atau tindakan antara kedua sistem. Secara keseluruhan, ada {total_beda_kode} titik perbedaan kode yang harus diperiksa kembali kebenarannya.")
        p2.style = 'List Bullet'
        for r in p2.runs: r.font.size = Pt(12)

        p3 = document.add_paragraph()
        p3.add_run(f"Potensi Perubahan Tingkat Keparahan ({perc_ccl}%): ").bold = True
        p3.add_run("Belum ada temuan kasus yang berisiko mengalami penurunan kelas keparahan penyakit (misalnya dari parah menjadi ringan) akibat kurangnya catatan penyakit penyerta, berdasarkan pemeriksaan sejauh ini.")
        p3.style = 'List Bullet'
        for r in p3.runs: r.font.size = Pt(12)

        add_p("", space_after_pt=12)"""

    if target_block in content:
        content = content.replace(target_block, new_block)
        print("Replaced Part 1 exactly.")
    else:
        print("Target 1 not found. Trying regex.")
        target_rx = re.compile(r'    else:\n\s+add_p\(\n\s+f"Dari keseluruhan \{total_kasus\}.*?add_p\("", space_after_pt=12\)', re.DOTALL)
        if target_rx.search(content):
            content = target_rx.sub(new_block, content)
            print("Replaced Part 1 via regex.")
        else:
            print("Failed to replace Part 1.")

    # Part 2: Fix headers and row assignments in Lampiran 1
    # Current headers logic:
    # headers_l1 = ['No', 'Nomor SEP', 'INA-CBG', 'iDRG / CCL', 'Skor KNAVP', 'Tingkat Risiko', 'Rekomendasi Reviewer', 'Discrepancy Diagnosa', 'Discrepancy Prosedur']
    # And row cells:
    #             row_cells[0].text = str(i)
    #             row_cells[1].text = str(c.get('sep', ''))
    #             row_cells[2].text = str(c.get('ina_code_str', ''))
    #             row_cells[3].text = str(c.get('idrg_code_str', ''))
    #             row_cells[4].text = str(c.get('skor_knavp', ''))
    #             row_cells[5].text = str(c.get('tingkat_risiko', ''))
    #             row_cells[6].text = rekom_clean
    #             row_cells[7].text = str(c.get('discrepancy_diagnosa', '-'))
    #             row_cells[8].text = str(c.get('discrepancy_prosedur', '-'))

    target_headers = "headers_l1 = ['No', 'Nomor SEP', 'INA-CBG', 'iDRG / CCL', 'Skor KNAVP', 'Tingkat Risiko', 'Rekomendasi Reviewer', 'Discrepancy Diagnosa', 'Discrepancy Prosedur']"
    new_headers = "headers_l1 = ['No', 'Nomor SEP', 'INA-CBG', 'iDRG / CCL', 'Skor KNAVP', 'Tingkat Risiko', 'Discrepancy Diagnosa', 'Discrepancy Prosedur', 'Rekomendasi Reviewer']"
    
    if target_headers in content:
        content = content.replace(target_headers, new_headers)
        print("Replaced Part 2 (headers) exactly.")
    else:
        print("Failed to replace Part 2 headers.")

    target_rows = """            row_cells[6].text = rekom_clean
            row_cells[7].text = str(c.get('discrepancy_diagnosa', '-'))
            row_cells[8].text = str(c.get('discrepancy_prosedur', '-'))"""
    
    new_rows = """            row_cells[6].text = str(c.get('discrepancy_diagnosa', '-'))
            row_cells[7].text = str(c.get('discrepancy_prosedur', '-'))
            row_cells[8].text = rekom_clean"""

    if target_rows in content:
        content = content.replace(target_rows, new_rows)
        print("Replaced Part 2 (rows) exactly.")
    else:
        print("Failed to replace Part 2 rows.")

    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_all()
