def fix_gambaran_and_font():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update font size defaults in functions
    content = content.replace("def add_p(text, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, size_pt=10, space_after_pt=0):",
                              "def add_p(text, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, size_pt=12, space_after_pt=0):")
    
    content = content.replace("def add_list_item(bullet, text, size_pt=10, space_after_pt=0):",
                              "def add_list_item(bullet, text, size_pt=12, space_after_pt=0):")
                              
    content = content.replace("def format_table(table, font_size_pt=10):",
                              "def format_table(table, font_size_pt=12):")

    # 2. Update explicit font_size_pt=10 calls to font_size_pt=12
    content = content.replace("font_size_pt=10", "font_size_pt=12")

    # 3. Replace Gambaran Data Table with Narrative
    bad_gb = """    table_gb = document.add_table(rows=7, cols=2)
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
    format_table(table_gb, font_size_pt=12)
    add_p("", space_after_pt=12)"""

    good_gb = """    narasi_gb = (
        f"Berdasarkan data Kertas Kerja Review (KKR-DR01), total kasus sampel yang direviu "
        f"pada {rs_name} berjumlah {len(cases)} kasus, yang mencakup {rj_rs} kasus rawat jalan dan {ri_rs} kasus rawat inap. "
        f"Dari hasil analisis reviewer terhadap indikasi ketidaksesuaian pengodean, "
        f"terdapat {onsite} kasus yang direkomendasikan untuk pelaksanaan On-Site Audit, "
        f"dan {sampling} kasus untuk Audit Sampling / Klarifikasi Administratif. "
        f"Sisa {monitor} kasus lainnya dinyatakan lolos validasi tanpa catatan khusus."
    )
    add_p(narasi_gb, align=3, size_pt=12, space_after_pt=12)"""

    # Note: `bad_gb` has `font_size_pt=12` because the previous replace changed it!
    if bad_gb in content:
        content = content.replace(bad_gb, good_gb)
        print("Gambaran Data replaced successfully!")
    else:
        print("Gambaran Data block NOT FOUND! (might have already been replaced)")

    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)
        print("Saved export_generator.py")

if __name__ == '__main__':
    fix_gambaran_and_font()
