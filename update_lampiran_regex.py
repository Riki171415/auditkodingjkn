import re

def fix_all():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Part 1: Lampiran 2
    match_l2 = re.search(r"document\.add_heading\('2\. Rekapitulasi Hasil Validasi KNAVP', level=2\)(.*?)add_p\(\"\", space_after_pt=6\)", content, re.DOTALL)
    if match_l2:
        new_l2 = """document.add_heading('2. Rekapitulasi Hasil Validasi KNAVP', level=2)
    ss = summary_stats or {}
    onsite   = ss.get('onsite',   sum(1 for c in cases if _lha_is_onsite(c.get('keputusan_sistem', ''))))
    sampling = ss.get('sampling', sum(1 for c in cases if _lha_is_sampling(c.get('keputusan_sistem', ''))))
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
    add_p("", space_after_pt=6)"""
        content = content[:match_l2.start()] + new_l2 + content[match_l2.end():]
        print("Replaced Lampiran 2")

    # Part 2: Lampiran 4
    match_l4 = re.search(r"document\.add_heading\('4\. Dashboard Hasil Validasi.*?level=2\)(.*?)(?=document\.add_page_break\(\)\s*# ── Lampiran 4 D|else:\s*add_p\(\"Tidak ada perbedaan)", content, re.DOTALL)
    if match_l4:
        new_l4 = """document.add_heading('4. Dashboard Hasil Validasi (Executive Summary KPI)', level=2)
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
    add_p("", space_after_pt=12)
    
    """
        content = content[:match_l4.start()] + new_l4 + content[match_l4.end():]
        print("Replaced Lampiran 4")

    # Also rename '4. Dashboard Hasil Validasi' in TOC to '2. Dashboard Hasil Validasi (Executive Summary KPI)'?
    # Actually wait, the user's prompt listed it as "2. Dashboard Hasil Validasi".
    # And Lampiran 2 as "1. Rekapitulasi Hasil Validasi KNAVP".
    # This implies they really DID want to remove Ringkasan KKR-DR01!
    # Let's just change the headings in Lampiran 2 and 4 to match the new text, but keep the numbering as is for now, OR renumber them?
    # I'll just change the content first.

    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_all()
