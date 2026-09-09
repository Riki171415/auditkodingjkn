import os

def refactor():
    with open(r'd:\KERJAAN PUSBIKES\Audit Koding 2025\audit-app\modules\export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the Discrepancy Table in Lampiran 1
    # Find the headers for Lampiran 1
    target_hdr = "l1_hdrs = ['No', 'Nomor SEP', 'INA-CBG', 'iDRG / CCL', 'Skor KNAVP', 'Tingkat Risiko', 'Rekomendasi Reviewer']"
    new_hdr = "l1_hdrs = ['No', 'Nomor SEP', 'INA-CBG', 'iDRG / CCL', 'Skor KNAVP', 'Tingkat Risiko', 'Rekomendasi Reviewer', 'Discrepancy Diagnosa', 'Discrepancy Prosedur']"
    if target_hdr in content:
        content = content.replace(target_hdr, new_hdr)
    else:
        print("target_hdr not found")

    # Add discrepancy logic into the loop for Lampiran 1
    loop_target = """    for idx, c in enumerate(cases):
        row_cells = table_l1.add_row().cells"""
    loop_new = """    from modules.rule_engine import check_dual_coding_discrepancy
    for idx, c in enumerate(cases):
        _sep = str(c.get('sep', ''))
        _idrg_info = _idrg_lookup.get(_sep, {}) if '_idrg_lookup' in locals() else {}
        _case_dc = dict(c)
        _case_dc['diaglist_idrg'] = _idrg_info.get('diaglist_idrg', '')
        _case_dc['proclist_idrg'] = _idrg_info.get('proclist_idrg', '')
        
        diag_diff_texts = []
        proc_diff_texts = []
        try:
            dc_res = check_dual_coding_discrepancy(_case_dc)
            for r in dc_res.get('diag_rows', []):
                if not r.get('sesuai'):
                    diag_diff_texts.append(f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}")
            for r in dc_res.get('proc_rows', []):
                if not r.get('sesuai'):
                    proc_diff_texts.append(f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}")
        except:
            pass
            
        diag_diff_str = "\\n".join(diag_diff_texts) if diag_diff_texts else "-"
        proc_diff_str = "\\n".join(proc_diff_texts) if proc_diff_texts else "-"
        
        row_cells = table_l1.add_row().cells"""
    if loop_target in content:
        content = content.replace(loop_target, loop_new)
    else:
        print("loop_target not found")

    # Add the columns to the row assignments
    cols_target = """        row_cells[5].text = str(c.get('tingkat_risiko', '-'))
        row_cells[6].text = str(c.get('keputusan_sistem') or c.get('rekomendasi_lanjut', '-'))
    format_table(table_l1, font_size_pt=9.5)"""
    cols_new = """        row_cells[5].text = str(c.get('tingkat_risiko', '-'))
        row_cells[6].text = str(c.get('keputusan_sistem') or c.get('rekomendasi_lanjut', '-'))
        row_cells[7].text = diag_diff_str
        row_cells[8].text = proc_diff_str
    format_table(table_l1, font_size_pt=8)"""
    if cols_target in content:
        content = content.replace(cols_target, cols_new)
    else:
        print("cols_target not found")

    if "table_l1 = document.add_table(rows=1, cols=7)" in content:
        content = content.replace("table_l1 = document.add_table(rows=1, cols=7)", "table_l1 = document.add_table(rows=1, cols=9)")
    else:
        print("cols=7 not found")

    # Part 2: Reorder Bab II Sections
    import re
    # We will locate the block for Analisis Temuan (now C), Kasus Prioritas (now D), and Discrepancy (now E)
    # They are identified by their headings
    
    # We just need to rename the headings in the file content because the TOC is updated.
    # C. Analisis Kesesuaian Input (Discrepancy Dual Coding) -> E. Kesesuaian Input INACBG-iDRG (Discrepancy Koding)
    # D. Analisis Temuan -> C. Analisis Temuan
    # E. Kasus Prioritas -> D. Kasus Prioritas
    
    content = content.replace("'C. Analisis Kesesuaian Input (Discrepancy Dual Coding)'", "'E. Kesesuaian Input INACBG-iDRG (Discrepancy Koding)'")
    content = content.replace("'D. Analisis Temuan'", "'C. Analisis Temuan'")
    content = content.replace("'E. Kasus Prioritas'", "'D. Kasus Prioritas'")
    
    # Remove the detailed table in Discrepancy Dual Coding
    # Locate from "tbl_dc = document.add_table(rows=1, cols=5)" to "format_table(tbl_dc, font_size_pt=10)"
    tbl_regex = re.compile(r'tbl_dc = document\.add_table\(rows=1, cols=5\).*?format_table\(tbl_dc, font_size_pt=10\)', re.DOTALL)
    content = tbl_regex.sub('', content)
    
    with open(r'd:\KERJAAN PUSBIKES\Audit Koding 2025\audit-app\modules\export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Lampiran 1 and BAB II logic updated.")

if __name__ == '__main__':
    refactor()
