def fix_landscape():
    # 1. Fix export_generator.py
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target1 = """    document.add_page_break()
    # ── LAMPIRAN ──────────────────────────────────────────────────────────────"""
    replacement1 = """    from docx.enum.section import WD_ORIENT
    from docx.shared import Inches
    new_section = document.add_section()
    new_section.orientation = WD_ORIENT.LANDSCAPE
    new_section.page_width = Inches(11.69)
    new_section.page_height = Inches(8.27)
    # ── LAMPIRAN ──────────────────────────────────────────────────────────────"""
    
    if target1 in content:
        content = content.replace(target1, replacement1)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed export_generator.py landscape!")
    else:
        print("Target 1 not found!")

    # 2. Fix generate_laporan_akhir_nasional.py
    with open('generate_laporan_akhir_nasional.py', 'r', encoding='utf-8') as f:
        content_nasional = f.read()
        
    target2 = """    doc.add_heading('Lampiran 1: Tabel Agregasi Rumah Sakit Sampel', level=2)"""
    replacement2 = """    from docx.enum.section import WD_ORIENT
    from docx.shared import Inches
    new_section = doc.add_section()
    new_section.orientation = WD_ORIENT.LANDSCAPE
    new_section.page_width = Inches(11.69)
    new_section.page_height = Inches(8.27)
    
    doc.add_heading('Lampiran 1: Tabel Agregasi Rumah Sakit Sampel', level=2)"""
    
    if target2 in content_nasional:
        content_nasional = content_nasional.replace(target2, replacement2)
        with open('generate_laporan_akhir_nasional.py', 'w', encoding='utf-8') as f:
            f.write(content_nasional)
        print("Fixed generate_laporan_akhir_nasional.py landscape!")
    else:
        print("Target 2 not found!")

if __name__ == '__main__':
    fix_landscape()
