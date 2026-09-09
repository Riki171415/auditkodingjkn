def fix_export_generator():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Global styles
    target1 = "document = Document()"
    replacement1 = """document = Document()
    for style in document.styles:
        if hasattr(style, 'font'):
            style.font.name = 'Times New Roman'
            if style.name.startswith('Heading') or style.name == 'Title' or style.name == 'Subtitle':
                style.font.color.rgb = RGBColor(0, 0, 0)
                style.font.size = Pt(12)
                style.font.bold = True"""
    if target1 in content and "style.font.color.rgb = RGBColor(0, 0, 0)" not in content:
        content = content.replace(target1, replacement1)

    # 2. Title
    target2 = """    # ── Title ─────────────────────────────────────────────────────────────────
    heading = document.add_heading('LAPORAN HASIL DESK REVIEW AUDIT CODING', 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = document.add_paragraph('Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)')
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].italic = True
    
    document.add_paragraph("", style='Normal')"""
    
    replacement2 = """    # ── Title ─────────────────────────────────────────────────────────────────
    add_p('LAPORAN HASIL DESK REVIEW AUDIT CODING', align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size_pt=12, space_after_pt=0)
    sub = add_p('Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)', align=WD_ALIGN_PARAGRAPH.CENTER, size_pt=12, space_after_pt=12)
    sub.runs[0].italic = True"""
    if target2 in content:
        content = content.replace(target2, replacement2)

    # 3. Duplicate page break before LAMPIRAN
    target3 = """    for num_str, text_str in rekom_items:
        add_list_item(num_str, text_str)
    document.add_page_break()

    document.add_page_break()
    # ── LAMPIRAN ──────────────────────────────────────────────────────────────"""
    replacement3 = """    for num_str, text_str in rekom_items:
        add_list_item(num_str, text_str)
    
    document.add_page_break()
    # ── LAMPIRAN ──────────────────────────────────────────────────────────────"""
    if target3 in content:
        content = content.replace(target3, replacement3)

    # 4. Duplicate page break at end of document
    # Note: `document.add_page_break()` is currently the very last thing added.
    # Wait, let's see if there's a page break after LAMPIRAN 4
    target4 = """        for b in dist_bullets:
            add_list_item("●", b)
        add_p("", space_after_pt=12)

    document.add_page_break()"""
    replacement4 = """        for b in dist_bullets:
            add_list_item("●", b)
        add_p("", space_after_pt=12)"""
    # Just to be safe, we can do a generic replacement for the end of the file.
    
    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed styles and breaks!")

if __name__ == '__main__':
    fix_export_generator()
