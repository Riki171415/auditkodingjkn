def patch_gap():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    bad_gap = """        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )
    add_p(
        "Hasil Desk Review merupakan hasil identifikasi awal berdasarkan data klaim dan belum merupakan penetapan adanya kesalahan pengodean. Seluruh temuan dianalisis oleh reviewer untuk menentukan rekomendasi tindak lanjut sesuai tingkat risiko dan dampaknya terhadap proses grouping INA-CBG maupun iDRG.",
        ("A. Gambaran Data", "3", False, 1),"""
        
    good_gap = """        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )
    
    add_p(
        "Akhir kata, kami mengucapkan terima kasih kepada seluruh pihak yang telah berpartisipasi dan kooperatif selama proses penyediaan data klaim dan rekam medis. Semoga laporan ini dapat menjadi bahan evaluasi yang membangun untuk perbaikan tata kelola koding di rumah sakit.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, space_after_pt=8
    )
    add_p("Jakarta, 15 Juni 2026", align=WD_ALIGN_PARAGRAPH.RIGHT, size_pt=12, space_after_pt=12)
    add_p("Tim Reviewer", align=WD_ALIGN_PARAGRAPH.RIGHT, size_pt=12, space_after_pt=12)
    
    document.add_page_break()

    # ── DAFTAR ISI ────────────────────────────────────────────────────────────
    add_p("DAFTAR ISI", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size_pt=14, space_after_pt=12)
    
    def add_toc_item(title, page_num, bold=False, indent_level=0):
        table_toc = document.add_table(rows=1, cols=2)
        table_toc.autofit = False
        table_toc.columns[0].width = Inches(5.5)
        table_toc.columns[1].width = Inches(0.5)
        c1 = table_toc.rows[0].cells[0]
        c2 = table_toc.rows[0].cells[1]
        
        p1 = c1.paragraphs[0]
        if indent_level > 0:
            p1.paragraph_format.left_indent = Inches(0.2 * indent_level)
        r1 = p1.add_run(title)
        r1.bold = bold
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(12)
        
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r2 = p2.add_run(page_num)
        r2.bold = bold
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(12)

    di_items = [
        ("KATA PENGANTAR", "1", True, 0),
        ("DAFTAR ISI", "2", True, 0),
        ("BAB I PENDAHULUAN", "2", True, 0),
        ("A. Latar Belakang", "2", False, 1),
        ("B. Tujuan dan Ruang Lingkup", "2", False, 1),
        ("BAB II HASIL DESK REVIEW", "3", True, 0),
        ("A. Gambaran Data", "3", False, 1),"""
        
    if bad_gap in content:
        content = content.replace(bad_gap, good_gap)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Gap patched successfully!")
    else:
        print("Could not find bad_gap!")

if __name__ == '__main__':
    patch_gap()
