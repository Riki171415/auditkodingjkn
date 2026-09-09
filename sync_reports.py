def sync_reports():
    # 1. Fix Lampiran 2 sampling count in export_generator.py
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    bad_samp = "sampling = ss.get('sampling', sum(1 for c in cases if 'Sampling' in str(c.get('keputusan_sistem', ''))))"
    good_samp = "sampling = ss.get('sampling', sum(1 for c in cases if 'Sampling' in str(c.get('keputusan_sistem', '')) and 'On-Site' not in str(c.get('keputusan_sistem', ''))))"
    if bad_samp in content:
        content = content.replace(bad_samp, good_samp)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed Lampiran 2 sampling count.")
    
    # 2. Fix 'vs' in generate_excel_reports_per_rs.py
    with open('generate_excel_reports_per_rs.py', 'r', encoding='utf-8') as f:
        excel_content = f.read()
        
    excel_bad = """                for r in dc_res.get('diag_rows', []):
                    if not r.get('sesuai'):
                        diag_diff_texts.append(f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}")
                for r in dc_res.get('proc_rows', []):
                    if not r.get('sesuai'):
                        proc_diff_texts.append(f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}")"""
                        
    excel_good = """                def format_dc_text(r):
                    ina = r.get('ina_code') or '-'
                    idrg = r.get('idrg_code') or '-'
                    ket = r.get('keterangan', '')
                    if ina == '-' and idrg != '-': return f"[+] {idrg} (iDRG): {ket}"
                    if idrg == '-' and ina != '-': return f"[-] {ina} (INA): {ket}"
                    return f"{ina} → {idrg}: {ket}"

                for r in dc_res.get('diag_rows', []):
                    if not r.get('sesuai'):
                        diag_diff_texts.append(format_dc_text(r))
                for r in dc_res.get('proc_rows', []):
                    if not r.get('sesuai'):
                        proc_diff_texts.append(format_dc_text(r))"""
                        
    if excel_bad in excel_content:
        excel_content = excel_content.replace(excel_bad, excel_good)
        with open('generate_excel_reports_per_rs.py', 'w', encoding='utf-8') as f:
            f.write(excel_content)
        print("Fixed vs in generate_excel_reports_per_rs.py")
        
    # 3. Fix 'vs' in generate_laporan_akhir_nasional.py
    with open('generate_laporan_akhir_nasional.py', 'r', encoding='utf-8') as f:
        nat_content = f.read()
        
    nat_bad = """                for r in dc_res.get('diag_rows', []):
                    if not r.get('sesuai'):
                        diag_diff_texts.append(f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}")
                for r in dc_res.get('proc_rows', []):
                    if not r.get('sesuai'):
                        proc_diff_texts.append(f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}")"""
                        
    if nat_bad in nat_content:
        nat_content = nat_content.replace(nat_bad, excel_good)
        with open('generate_laporan_akhir_nasional.py', 'w', encoding='utf-8') as f:
            f.write(nat_content)
        print("Fixed vs in generate_laporan_akhir_nasional.py")

if __name__ == '__main__':
    sync_reports()
