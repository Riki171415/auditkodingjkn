def fix_excel_generator():
    with open('generate_excel_reports_per_rs.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target_norm = """def _normalize_keputusan(form_data):
    kep_sis = form_data.get('keputusan_sistem', 'Tidak diperlukan tindak lanjut')
    kep = form_data.get('keputusan') or kep_sis
    
    kep_str = str(kep)
    if 'Fraud' in kep_str or 'Tidak Sesuai' in kep_str or 'On-Site' in kep_str:
        return 'Direkomendasikan On-Site Audit'
    if 'Monitoring' in kep_str:
        return 'Perlu Monitoring'
    if 'cukup' in kep_str.lower():
        return 'Data tidak cukup untuk dinilai'
    if 'Sesuai' in kep_str or 'Valid' in kep_str or 'Tidak perlu' in kep_str or 'Tidak diperlukan' in kep_str:
        return 'Tidak diperlukan tindak lanjut'
        
    return kep_str"""

    replacement_norm = """def _normalize_keputusan(c, form_data):
    # Logic disamakan persis dengan generator Word
    is_priority = bool(c.get('triggered_rules')) or int(c.get('jumlah_beda_dual_coding', 0)) > 0
    if is_priority:
        knavp_skor = form_data.get('knavp_skor', c.get('knavp_skor', 0)) or 0
        tingkat_risiko = form_data.get('tingkat_risiko', c.get('tingkat_risiko', '-')) or '-'
        is_tinggi = str(tingkat_risiko).lower() == 'tinggi' or float(knavp_skor) >= 4
        return 'Direkomendasikan On-Site Audit' if is_tinggi else 'Audit Sampling (Klarifikasi)'
    else:
        return 'Perlu Monitoring'"""

    if target_norm in content:
        content = content.replace(target_norm, replacement_norm)
        
    # Now replace the call to _normalize_keputusan
    target_call = "keputusan = _normalize_keputusan(form_data)"
    replacement_call = "keputusan = _normalize_keputusan(c, form_data)"
    
    if target_call in content:
        content = content.replace(target_call, replacement_call)

    # Now fix the red text in Excel
    target_format = """                for row in ws.iter_rows(min_row=2):
                    for cell in row:
                        cell.border = border
                        cell.font = Font(size=8)"""
                        
    replacement_format = """                for row in ws.iter_rows(min_row=2):
                    for cell in row:
                        cell.border = border
                        cell.font = Font(size=8)
                        if cell.value == 'Direkomendasikan On-Site Audit':
                            cell.font = Font(size=8, color='FF0000', bold=True)"""
                            
    if target_format in content:
        content = content.replace(target_format, replacement_format)

    with open('generate_excel_reports_per_rs.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed excel generator!")

if __name__ == '__main__':
    fix_excel_generator()
