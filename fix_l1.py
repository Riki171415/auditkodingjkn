import re

def fix_all():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Part 1: Replace headers in Lampiran 1
    target_headers = "l1_hdrs = ['No', 'Nomor SEP', 'INA-CBG', 'iDRG / CCL', 'Skor KNAVP', 'Tingkat Risiko', 'Rekomendasi Reviewer', 'Discrepancy Diagnosa', 'Discrepancy Prosedur']"
    new_headers = "l1_hdrs = ['No', 'Nomor SEP', 'INA-CBG', 'iDRG / CCL', 'Skor KNAVP', 'Tingkat Risiko', 'Discrepancy Diagnosa', 'Discrepancy Prosedur', 'Rekomendasi Reviewer']"
    if target_headers in content:
        content = content.replace(target_headers, new_headers)
        print("Replaced Lampiran 1 headers")
    else:
        print("Failed to replace Lampiran 1 headers")

    # Part 2: Replace rows in Lampiran 1
    target_rows = "        row_cells[6].text = str(c.get('keputusan_sistem') or c.get('rekomendasi_lanjut', '-'))\n        row_cells[7].text = diag_diff_str\n        row_cells[8].text = proc_diff_str"
    new_rows = "        row_cells[6].text = diag_diff_str\n        row_cells[7].text = proc_diff_str\n        row_cells[8].text = str(c.get('keputusan_sistem') or c.get('rekomendasi_lanjut', '-'))"
    if target_rows in content:
        content = content.replace(target_rows, new_rows)
        print("Replaced Lampiran 1 rows")
    else:
        print("Failed to replace Lampiran 1 rows")

    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_all()
