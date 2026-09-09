import re
import os

def fix_table():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # We will replace the text in the "else:" block of Kesesuaian Input
    target_block = """    else:
        add_p(
            f"Dari {total_kasus} kasus yang direviu pada {rs_name}, terdapat {kasus_beda} kasus "
            f"({round(kasus_beda/total_kasus*100,1)}%) yang memiliki perbedaan kode (discrepancy) "
            f"antara input sistem INA-CBG dan iDRG, dengan total {total_beda_kode} perbedaan kode klinis. "
            f"Tingkat kesesuaian bersih mencapai {match_rate}% ({kasus_sesuai} kasus selaras penuh). "
            "Rincian seluruh kode yang berbeda disajikan pada tabel berikut:",
            align=3, size_pt=12, space_after_pt=6
        )

        # Tabel rinci: No | SEP | Kode INA-CBG | Kode iDRG | Keterangan
        

        if len(detail_beda) > 30:
            add_p(
                f"*) Tabel di atas menampilkan 30 dari {len(detail_beda)} total perbedaan kode. "
                "Detail lengkap tersedia pada KKR-DR01 masing-masing kasus.",
                align=0, size_pt=9, space_after_pt=4
            )"""
            
    new_block = """    else:
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

    if target_block in content:
        content = content.replace(target_block, new_block)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Table successfully updated in export_generator.py")
    else:
        print("Target block not found. Trying regex.")
        # fallback regex if spaces mismatched
        rx = re.compile(r'    else:\n\s+add_p\(\n\s+f"Dari \{total_kasus\}.*?Detail lengkap tersedia pada KKR-DR01 masing-masing kasus\.",\n\s+align=0, size_pt=9, space_after_pt=4\n\s+\)', re.DOTALL)
        if rx.search(content):
            content = rx.sub(new_block, content)
            with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Table successfully updated via regex in export_generator.py")
        else:
            print("Failed to find target block via regex too.")

if __name__ == '__main__':
    fix_table()
