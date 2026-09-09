def fix_end():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    idx = content.find("    document.add_heading('2. Rekapitulasi Hasil Validasi KNAVP', level=2)")
    if idx != -1:
        content = content[:idx] + """    document.add_heading('2. Rekapitulasi Hasil Validasi KNAVP', level=2)
    ss = summary_stats or {}
    onsite   = ss.get('onsite',   sum(1 for c in cases if 'On-Site' in str(c.get('keputusan_sistem', ''))))
    sampling = ss.get('sampling', sum(1 for c in cases if 'Sampling' in str(c.get('keputusan_sistem', ''))))
    monitor  = ss.get('monitoring', len(cases) - onsite - sampling)
    avg_skor = ss.get('avg_skor_knavp', round(sum(float(c.get('knavp_skor', 0) or 0) for c in cases) / max(len(cases), 1), 1))
    beda_dc  = ss.get('total_beda_dc', sum(int(c.get('jumlah_beda_dual_coding', 0) or 0) for c in cases))

    l2_bullets = [
        f"Total Kasus Di-Review: {len(cases)}",
        f"Rekomendasi Lanjut On-Site Audit: {onsite}",
        f"Rekomendasi Lanjut Sampling: {sampling}",
        f"Rekomendasi Monitoring (Lolos): {monitor}",
        f"Rata-rata Skor KNAVP: {avg_skor}",
        f"Total Perbedaan Dual Coding (INA-CBG vs iDRG): {beda_dc}",
        f"Status Pengelompokan iDRG: Terverifikasi Rule Engine"
    ]
    for b in l2_bullets:
        add_list_item("●", b)
    add_p("", space_after_pt=6)
    
    document.add_page_break()
    document.add_heading('3. Daftar Kasus Prioritas', level=2)
    table_l3 = document.add_table(rows=1, cols=4)
    l3_hdrs = ['No', 'Nomor SEP', 'Prioritas', 'Rekomendasi Lanjut']
    for i, h in enumerate(l3_hdrs):
        table_l3.rows[0].cells[i].text = h
    for idx, c in enumerate(priority_cases):
        row_cells = table_l3.add_row().cells
        row_cells[0].text = str(idx + 1)
        row_cells[1].text = str(c.get('sep', ''))
        row_cells[2].text = str(c.get('tingkat_risiko', 'Tinggi'))
        row_cells[3].text = "On-Site Audit / Klarifikasi"
    format_table(table_l3, font_size_pt=9)
    add_p("", space_after_pt=6)

    document.add_page_break()
    document.add_heading('4. Dashboard Hasil Validasi (Executive Summary KPI)', level=2)
    compliance_rate = (monitor / len(cases) * 100) if cases else 100
    outlier_rate = (onsite / len(cases) * 100) if cases else 0
    risk_class = "Tinggi" if avg_skor >= 4 else "Sedang" if avg_skor >= 2 else "Rendah"
    
    l4_bullets = [
        f"Tingkat Kepatuhan Koding (Compliance Rate): {round(compliance_rate,1)}% ({monitor} kasus lolos tanpa catatan/risiko minor)",
        f"Rasio Outlier (On-Site Audit Rate): {round(outlier_rate,1)}% ({onsite} kasus wajib diverifikasi fisik rekam medis)",
        f"Indeks Skor Risiko KNAVP RS: {avg_skor} / 10 (Klasifikasi Risiko {risk_class})"
    ]
    for b in l4_bullets:
        add_list_item("●", b)
        
    add_p("Distribusi Status & Rekomendasi Kasus:", bold=True, space_after_pt=4)
    samp_rate = (sampling / len(cases) * 100) if cases else 0
    dist_bullets = [
        f"Monitoring (Lolos / Risiko Rendah): {monitor} Kasus ({round(compliance_rate,1)}%)",
        f"Sampling / Klarifikasi (Risiko Sedang): {sampling} Kasus ({round(samp_rate,1)}%)",
        f"On-Site Audit (Risiko Tinggi >= 4.0): {onsite} Kasus ({round(outlier_rate,1)}%)",
        f"TOTAL KASUS SAMPEL: {len(cases)} Kasus (100%)"
    ]
    for b in dist_bullets:
        add_list_item("●", b)
    add_p("", space_after_pt=12)

    document.save(output_path)
    return output_path
"""
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("End fixed!")
    else:
        print("Could not find start of end block!")

if __name__ == '__main__':
    fix_end()
