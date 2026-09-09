import re
with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

target_block_regex = re.compile(
    r'    add_p\("D\. Profil Akurasi Dual Coding \(INA-CBG vs iDRG Bersih\)", align=WD_ALIGN_PARAGRAPH\.LEFT, bold=True, size_pt=11\.5, space_after_pt=4\)\n.*?'
    r'    format_table\(table_dc, font_size_pt=9\.5\)\n'
    r'    add_p\("", space_after_pt=12\)',
    re.DOTALL
)

new_block = """    add_p("D. Rincian Kesesuaian Input (Discrepancy Koding)", align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, size_pt=11.5, space_after_pt=4)
    if len(detail_beda) > 0:
        tbl_dc = document.add_table(rows=1, cols=5)
        tbl_dc.style = 'Table Grid'
        h_cells = tbl_dc.rows[0].cells
        headers_dc = ['No', 'SEP', 'Kode INA-CBG', 'Kode iDRG', 'Keterangan']
        for i, h in enumerate(headers_dc):
            h_cells[i].text = h
            for r in h_cells[i].paragraphs[0].runs: 
                r.font.bold = True
                r.font.size = Pt(10)
            h_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        for i, b in enumerate(detail_beda, 1):
            row_cells = tbl_dc.add_row().cells
            row_cells[0].text = str(i)
            row_cells[1].text = str(b['sep'])
            row_cells[2].text = str(b['kode_ina'])
            row_cells[3].text = str(b['kode_idrg'])
            row_cells[4].text = str(b['keterangan'])
            for j in range(5):
                for run in row_cells[j].paragraphs[0].runs:
                    run.font.size = Pt(9)
                row_cells[j].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if j < 4 else WD_ALIGN_PARAGRAPH.LEFT
        format_table(tbl_dc, font_size_pt=9)
    else:
        add_p("Tidak ada perbedaan (discrepancy) kode klinis antara INA-CBG dan iDRG pada kasus sampel ini.", size_pt=10)
    add_p("", space_after_pt=12)"""

if target_block_regex.search(content):
    content = target_block_regex.sub(new_block, content)
    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced section D in Lampiran 4 with the detailed discrepancy table.")
else:
    print("Could not find the target block with regex.")
