import os

def refactor():
    with open('generate_laporan_akhir_nasional.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where Lampiran 2 headers are set
    target_headers = "    headers_os = ['No', 'No SEP', 'Nama RS', 'Diagnosis INA-CBG (Kode)', 'Tingkat Risiko', 'Pelanggaran / Keterangan']"
    new_headers = "    headers_os = ['No', 'No SEP', 'Nama RS', 'Diagnosis INA-CBG (Kode)', 'Tingkat Risiko', 'Pelanggaran / Keterangan', 'Discrepancy Diagnosa', 'Discrepancy Prosedur']"
    content = content.replace(target_headers, new_headers)

    # Change table_os = doc.add_table(rows=1, cols=6) to cols=8
    content = content.replace("table_os = doc.add_table(rows=1, cols=6)", "table_os = doc.add_table(rows=1, cols=8)")

    # Change the loop range(6) to range(8)
    # The loop looks like: for i in range(6):
    content = content.replace("for i in range(6):", "for i in range(8):")

    # Insert logic to fetch idrg data before the loop
    # We find: for idx_os, case in enumerate(onsite_cases, 1):
    target_loop = "    for idx_os, case in enumerate(onsite_cases, 1):"
    
    new_loop_prep = """
    import sqlite3
    _DATA_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.db')
    _idrg_lookup = {}
    try:
        _conn_dd = sqlite3.connect(_DATA_DB)
        _conn_dd.row_factory = sqlite3.Row
        _cur_dd = _conn_dd.cursor()
        _cur_dd.execute("SELECT sep, diaglist_idrg, proclist_idrg FROM individual_data")
        for _rr in _cur_dd.fetchall():
            _idrg_lookup[str(_rr['sep'])] = {
                'diaglist_idrg': _rr['diaglist_idrg'] or '',
                'proclist_idrg': _rr['proclist_idrg'] or '',
            }
        _conn_dd.close()
    except Exception:
        pass
        
    from modules.rule_engine import check_dual_coding_discrepancy
    for idx_os, case in enumerate(onsite_cases, 1):"""
    
    content = content.replace(target_loop, new_loop_prep)

    # Add the assignment for row_cells[6] and row_cells[7]
    target_assignments = "        row_cells[5].text = keterangan"
    
    new_assignments = """        row_cells[5].text = keterangan
        
        # Calculate discrepancy for this case
        _sep = str(case.get('sep', ''))
        _idrg_info = _idrg_lookup.get(_sep, {})
        _case_dc = dict(case)
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
        
        row_cells[6].text = diag_diff_str
        row_cells[7].text = proc_diff_str"""
    
    content = content.replace(target_assignments, new_assignments)
    
    with open('generate_laporan_akhir_nasional.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Nasional report script updated with columns.")

if __name__ == '__main__':
    refactor()
