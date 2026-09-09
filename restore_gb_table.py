def restore_table():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target = "add_p(narasi_gb, align=3, size_pt=12, space_after_pt=12)"
    
    table_code = """add_p(narasi_gb, align=3, size_pt=12, space_after_pt=12)
    
    table_gb = document.add_table(rows=6, cols=2)
    gb_data = [
        ['Uraian', 'Jumlah'],
        ['Total Kasus Direview (Sampel)', str(len(cases))],
        ['Rawat Jalan', str(rj_rs)],
        ['Rawat Inap', str(ri_rs)],
        ['Rekomendasi On-Site Audit', str(onsite)],
        ['Rekomendasi Audit Sampling', str(sampling)]
    ]
    for i, row in enumerate(gb_data):
        table_gb.rows[i].cells[0].text = row[0]
        table_gb.rows[i].cells[1].text = row[1]
    format_table(table_gb, font_size_pt=12)
    add_p("", space_after_pt=12)"""

    if target in content and "table_gb = document.add_table" not in content.split("A. Gambaran Data")[1].split("B. Ringkasan Hasil Validasi")[0]:
        content = content.replace(target, table_code)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Table restored successfully!")
    else:
        print("Target not found or table already exists!")

if __name__ == '__main__':
    restore_table()
