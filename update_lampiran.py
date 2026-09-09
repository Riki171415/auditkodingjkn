import re

def fix_all():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Part 1: Replace Lampiran 2 (Rekapitulasi Hasil Validasi KNAVP) table with bullet points
    target_l2 = """    document.add_heading('2. Rekapitulasi Hasil Validasi KNAVP', level=2)
    table_l2 = document.add_table(rows=8, cols=2)
    ss = summary_stats or {}
    # ── Hitung ulang menggunakan helper terpusat — konsisten dengan Excel ───────
    onsite   = ss.get('onsite',   sum(1 for c in cases if _lha_is_onsite(c.get('keputusan_sistem', ''))))
    sampling = ss.get('sampling', sum(1 for c in cases if _lha_is_sampling(c.get('keputusan_sistem', ''))))
    monitor  = ss.get('monitoring', len(cases) - onsite - sampling)
    # ──────────────────────────────────
    l2_data = [
        ['Total Kasus Di-Review', str(len(cases))],
        ['Rekomendasi Lanjut On-Site Audit', str(onsite)],
        ['Rekomendasi Lanjut Sampling', str(sampling)],
        ['Rekomendasi Monitoring (Lolos)', str(monitor)],
        ['Rata-rata Skor KNAVP', str(round(sum(float(c.get('knavp_skor', 0) or 0) for c in cases)/max(1, len(cases)), 2))],
        ['Total Perbedaan Dual Coding (INA-CBG vs iDRG)', str(sum(int(c.get('jumlah_beda_dual_coding', 0) or 0) for c in cases))],
        ['Status Pengelompokan iDRG', 'Terverifikasi Rule Engine']
    ]
    for r_idx, row_dat in enumerate(l2_data):
        table_l2.rows[r_idx].cells[0].text = row_dat[0]
        table_l2.rows[r_idx].cells[1].text = row_dat[1]
    format_table(table_l2, font_size_pt=9)
    add_p("", space_after_pt=12)"""

    new_l2 = """    document.add_heading('2. Rekapitulasi Hasil Validasi KNAVP', level=2)
    ss = summary_stats or {}
    onsite   = ss.get('onsite',   sum(1 for c in cases if _lha_is_onsite(c.get('keputusan_sistem', ''))))
    sampling = ss.get('sampling', sum(1 for c in cases if _lha_is_sampling(c.get('keputusan_sistem', ''))))
    monitor  = ss.get('monitoring', len(cases) - onsite - sampling)
    avg_skor = round(sum(float(c.get('knavp_skor', 0) or 0) for c in cases)/max(1, len(cases)), 2)
    tot_beda = sum(int(c.get('jumlah_beda_dual_coding', 0) or 0) for c in cases)
    
    l2_bullets = [
        f"Total Kasus Di-Review: {len(cases)}",
        f"Rekomendasi Lanjut On-Site Audit: {onsite}",
        f"Rekomendasi Lanjut Sampling: {sampling}",
        f"Rekomendasi Monitoring (Lolos): {monitor}",
        f"Rata-rata Skor KNAVP: {avg_skor}",
        f"Total Perbedaan Dual Coding (INA-CBG vs iDRG): {tot_beda}",
        f"Status Pengelompokan iDRG: Terverifikasi Rule Engine"
    ]
    for b in l2_bullets:
        add_list_item("●", b)
    add_p("", space_after_pt=12)"""

    if target_l2 in content:
        content = content.replace(target_l2, new_l2)
        print("Replaced Lampiran 2 with bullet points")
    else:
        print("Failed to find Lampiran 2 target")


    # Part 2: Replace Lampiran 4 (Dashboard Hasil Validasi) table with bullet points
    target_l4 = """    document.add_heading('4. Dashboard Hasil Validasi (Executive Summary KPI)', level=2)
    table_l4 = document.add_table(rows=3, cols=2)
    compliance_rate = (monitor / len(cases) * 100) if cases else 100
    outlier_rate = (onsite / len(cases) * 100) if cases else 0
    l4_data = [
        ['Tingkat Kepatuhan Koding (Compliance Rate)', f"{round(compliance_rate,1)}% ({monitor} kasus lolos tanpa catatan/risiko minor)"],
        ['Rasio Outlier (On-Site Audit Rate)', f"{round(outlier_rate,1)}% ({onsite} kasus wajib diverifikasi fisik rekam medis)"],
        ['Indeks Skor Risiko KNAVP RS', f"{avg_skor} / 10 (Klasifikasi Risiko {risk_class})"]
    ]
    for r_idx, row_dat in enumerate(l4_data):
        table_l4.rows[r_idx].cells[0].text = row_dat[0]
        table_l4.rows[r_idx].cells[1].text = row_dat[1]
    format_table(table_l4, font_size_pt=9)
    add_p("", space_after_pt=6)"""

    new_l4 = """    document.add_heading('4. Dashboard Hasil Validasi (Executive Summary KPI)', level=2)
    compliance_rate = (monitor / len(cases) * 100) if cases else 100
    outlier_rate = (onsite / len(cases) * 100) if cases else 0
    
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
        f"On-Site Audit (Risiko Tinggi ≥ 4.0): {onsite} Kasus ({round(outlier_rate,1)}%)",
        f"TOTAL KASUS SAMPEL: {len(cases)} Kasus (100%)"
    ]
    for b in dist_bullets:
        add_list_item("●", b)
    add_p("", space_after_pt=12)"""

    if target_l4 in content:
        content = content.replace(target_l4, new_l4)
        print("Replaced Lampiran 4 with bullet points")
    else:
        print("Failed to find Lampiran 4 target")

    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_all()
