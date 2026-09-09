import re
import os

def refactor():
    with open('generate_excel_reports_per_rs.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add lookup loading from data.db
    target_lookup = "    print(f\"Ditemukan {len(rs_map)} Rumah Sakit.\")"
    new_lookup = """    print(f"Ditemukan {len(rs_map)} Rumah Sakit.")

    # Ambil diaglist_idrg & proclist_idrg dari individual_data (data.db)
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
        pass"""
    content = content.replace(target_lookup, new_lookup)
    
    # 2. Add discrepancy computation before rows_sep.append
    target_append = "            rows_sep.append({"
    new_append = """            # Cek discrepancy
            from modules.rule_engine import check_dual_coding_discrepancy
            _idrg_info = _idrg_lookup.get(sep_val, {})
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

            rows_sep.append({"""
    content = content.replace(target_append, new_append)

    # 3. Add columns to rows_sep appending
    target_cols = "                'Tanggal Review': '15 Juni 2026'                                    # col 15"
    new_cols = "                'Tanggal Review': '15 Juni 2026',                                   # col 15\n                'Temuan Discrepancy Diagnosa': diag_diff_str,\n                'Temuan Discrepancy Prosedur': proc_diff_str"
    content = content.replace(target_cols, new_cols)

    with open('generate_excel_reports_per_rs.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Excel report script updated.")

if __name__ == '__main__':
    refactor()
