def fix_gap():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    bad_gap = """    document.add_heading('A. Gambaran Data', level=2)
    table_gb = document.add_table(rows=7, cols=2)
    gb_data = [
        ['Uraian', 'Jumlah'],
                f"Dari seluruh pelanggaran tersebut, kelompok temuan paling dominan adalah {dom_label} sebanyak {dom_count} temuan. \""""
                
    good_gap = """    document.add_heading('A. Gambaran Data', level=2)
    
    ss = summary_stats or {}
    onsite   = ss.get('onsite', sum(1 for c in cases if 'On-Site' in str(c.get('keputusan_sistem', ''))))
    sampling = ss.get('sampling', sum(1 for c in cases if 'Sampling' in str(c.get('keputusan_sistem', '')) and 'On-Site' not in str(c.get('keputusan_sistem', ''))))
    monitor  = ss.get('monitoring', len(cases) - onsite - sampling)
    avg_skor = ss.get('avg_skor_knavp', round(sum(float(c.get('knavp_skor', 0) or 0) for c in cases) / max(len(cases), 1), 1))
    beda_dc  = ss.get('total_beda_dc', sum(int(c.get('jumlah_beda_dual_coding', 0) or 0) for c in cases))
    
    conn = get_audit_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as total, "
        "SUM(CASE WHEN inacbg LIKE '%-0' THEN 1 ELSE 0 END) as rj, "
        "SUM(CASE WHEN inacbg NOT LIKE '%-0' THEN 1 ELSE 0 END) as ri "
        "FROM datadb.individual_data WHERE kode_rs = ?",
        (kode_rs,)
    )
    rs_stats = cursor.fetchone()
    total_rs = rs_stats['total']
    rj_rs = rs_stats['rj'] or 0
    ri_rs = rs_stats['ri'] or 0
    
    table_gb = document.add_table(rows=7, cols=2)
    gb_data = [
        ['Uraian', 'Jumlah'],
        ['Total Populasi Kasus RS', str(total_rs)],
        ['Rawat Jalan', str(rj_rs)],
        ['Rawat Inap', str(ri_rs)],
        ['Total Kasus Direview', str(len(cases))],
        ['Kasus On-Site Audit', str(onsite)],
        ['Kasus Audit Sampling', str(sampling)]
    ]
    for i, row in enumerate(gb_data):
        table_gb.rows[i].cells[0].text = row[0]
        table_gb.rows[i].cells[1].text = row[1]
    format_table(table_gb, font_size_pt=10)
    add_p("", space_after_pt=12)
    
    document.add_heading('B. Ringkasan Hasil Validasi KNAVP (Otomatis)', level=2)
    knavp_tbl = document.add_table(rows=8, cols=2)
    knavp_rows = [
        ['Parameter KNAVP', 'Nilai'],
        ['Total Kasus Divalidasi', str(len(cases))],
        ['Rekomendasi On-Site Audit', str(onsite)],
        ['Rekomendasi Audit Sampling', str(sampling)],
        ['Rekomendasi Monitoring', str(monitor)],
        ['Rata-rata Skor KNAVP', str(avg_skor)],
        ['Total Perbedaan Dual Coding (INA-CBG vs iDRG)', str(beda_dc)],
        ['Metode Matching Dual Coding', 'Exact / Prefix / Modifier (+X)'],
    ]
    for i, row in enumerate(knavp_rows):
        knavp_tbl.rows[i].cells[0].text = row[0]
        knavp_tbl.rows[i].cells[1].text = row[1]
    format_table(knavp_tbl, font_size_pt=10)
    add_p("", space_after_pt=12)
    
    document.add_heading('C. Analisis Temuan', level=2)
    from modules.rule_engine import GROUPED_RULES
    rule_counts = {}
    total_temuan_all = 0
    for c in cases:
        for rt in c.get('triggered_rules', []):
            total_temuan_all += 1
            cat_found = False
            for c_id, c_info in GROUPED_RULES.items():
                if any(r_code in rt for r_code in c_info['rules']):
                    rule_counts[c_id] = rule_counts.get(c_id, 0) + 1
                    cat_found = True
                    break
            if not cat_found:
                rule_counts['lainnya'] = rule_counts.get('lainnya, 0') + 1

    dom_kat, dom_count = max(rule_counts.items(), key=lambda x: x[1]) if rule_counts else ("-", 0)
    dom_label = dom_kat
    if dom_kat != "-":
        dom_label = GROUPED_RULES.get(dom_kat, {}).get('title', dom_kat)

    _narasi_map = {
        'mutually_exclusive':
            f"Berdasarkan hasil validasi KNAVP terhadap {len(cases)} kasus yang direviu pada {rs_name}, secara keseluruhan terdapat {total_temuan_all} temuan pelanggaran aturan. "
            f"Dari seluruh pelanggaran tersebut, kelompok temuan paling dominan adalah {dom_label} sebanyak {dom_count} temuan. \""""
            
    if bad_gap in content:
        content = content.replace(bad_gap, good_gap)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Missing BAB II A and B filled!")
    else:
        print("Bad gap not found!")

if __name__ == '__main__':
    fix_gap()
