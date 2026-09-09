def fix_priority_counts():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target_top = """    ss = summary_stats or {}
    onsite   = ss.get('onsite', sum(1 for c in cases if 'On-Site' in str(c.get('keputusan_sistem', ''))))
    sampling = ss.get('sampling', sum(1 for c in cases if 'Sampling' in str(c.get('keputusan_sistem', '')) and 'On-Site' not in str(c.get('keputusan_sistem', ''))))
    monitor  = ss.get('monitoring', len(cases) - onsite - sampling)"""

    replacement_top = """    ss = summary_stats or {}
    
    cases_with_rules = sorted(
        [c for c in cases if c.get('triggered_rules')],
        key=lambda x: float(x.get('knavp_skor', 0) or 0),
        reverse=True
    )
    cases_dc_only = [
        c for c in cases
        if not c.get('triggered_rules')
        and int(c.get('jumlah_beda_dual_coding', 0)) > 0
    ]
    priority_cases = cases_with_rules + cases_dc_only

    onsite   = ss.get('onsite', sum(1 for c in priority_cases if str(c.get('tingkat_risiko', '')).lower() == 'tinggi' or float(c.get('knavp_skor', 0) or 0) >= 4))
    sampling = ss.get('sampling', len(priority_cases) - onsite)
    monitor  = ss.get('monitoring', len(cases) - len(priority_cases))"""

    if target_top in content:
        content = content.replace(target_top, replacement_top)

    target_bottom = """    # Prioritas 1: kasus yang ADA triggered rules, diurutkan skor tertinggi
    cases_with_rules = sorted(
        [c for c in cases if c.get('triggered_rules')],
        key=lambda x: int(x.get('knavp_skor') or 0),
        reverse=True
    )
    # Prioritas 2: kasus dual-coding discrepancy tanpa rule, tingkat Sedang/Tinggi
    cases_dc_only = [
        c for c in cases
        if not c.get('triggered_rules')
        and int(c.get('jumlah_beda_dual_coding', 0)) > 0
    ]

    priority_cases = cases_with_rules + cases_dc_only
    
    for i, c in enumerate(priority_cases):
        row_cells = table_kp.add_row().cells
        row_cells[0].text = str(i + 1)
        row_cells[1].text = str(c.get('sep', ''))
        rules = c.get('triggered_rules')
        if rules and isinstance(rules, list):
            rule_texts = [f"• [{r.get('rule_id', '')}] {r.get('nama_aturan', '')}" for r in rules]
            row_cells[2].text = "\\n".join(rule_texts)
        else:
            row_cells[2].text = "Perbedaan Dual Coding Tinggi"
        row_cells[3].text = str(c.get('tingkat_risiko', 'Tinggi'))
        row_cells[4].text = "On-Site Audit / Klarifikasi"
"""

    replacement_bottom = """    # priority_cases sudah didefinisikan di atas
    
    for i, c in enumerate(priority_cases):
        row_cells = table_kp.add_row().cells
        row_cells[0].text = str(i + 1)
        row_cells[1].text = str(c.get('sep', ''))
        rules = c.get('triggered_rules')
        if rules and isinstance(rules, list):
            rule_texts = [f"• [{r.get('rule_id', '')}] {r.get('nama_aturan', '')}" for r in rules]
            row_cells[2].text = "\\n".join(rule_texts)
        else:
            row_cells[2].text = "Perbedaan Dual Coding Tinggi"
            
        is_tinggi = str(c.get('tingkat_risiko', '')).lower() == 'tinggi' or float(c.get('knavp_skor', 0) or 0) >= 4
        row_cells[3].text = "Tinggi" if is_tinggi else "Sedang"
        row_cells[4].text = "On-Site Audit" if is_tinggi else "Audit Sampling"
"""

    if target_bottom in content:
        content = content.replace(target_bottom, replacement_bottom)
        
    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed priority counts!")

if __name__ == '__main__':
    fix_priority_counts()
