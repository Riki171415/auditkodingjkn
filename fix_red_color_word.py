def fix_red_color():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target = """        is_tinggi = str(c.get('tingkat_risiko', '')).lower() == 'tinggi' or float(c.get('knavp_skor', 0) or 0) >= 4
        row_cells[3].text = "Tinggi" if is_tinggi else "Sedang"
        row_cells[4].text = "On-Site Audit" if is_tinggi else "Audit Sampling"
"""

    replacement = """        is_tinggi = str(c.get('tingkat_risiko', '')).lower() == 'tinggi' or float(c.get('knavp_skor', 0) or 0) >= 4
        row_cells[3].text = "Tinggi" if is_tinggi else "Sedang"
        
        row_cells[4].text = ""
        run = row_cells[4].paragraphs[0].add_run("On-Site Audit" if is_tinggi else "Audit Sampling")
        if is_tinggi:
            from docx.shared import RGBColor
            run.font.color.rgb = RGBColor(255, 0, 0)
"""

    if target in content:
        content = content.replace(target, replacement)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed red color in word generator!")
    else:
        print("Target not found in word generator!")

if __name__ == '__main__':
    fix_red_color()
