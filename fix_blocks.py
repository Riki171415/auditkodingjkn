import re
with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
    text = f.read()

marker_E = "    document.add_heading('E. Kesesuaian Input INACBG-iDRG (Discrepancy Koding)', level=2)"
marker_C = "    document.add_heading('C. Analisis Temuan', level=2)"
marker_D = "    document.add_heading('D. Kasus Prioritas', level=2)"
marker_end = "    # ── BAB III KESIMPULAN DAN REKOMENDASI"

pos_E_header = text.find("    # ── C. Analisis Kesesuaian Input")
if pos_E_header == -1: pos_E_header = text.find(marker_E)

pos_C_header = text.find(marker_C)
pos_D_header = text.find(marker_D)
pos_end = text.find(marker_end)

if -1 not in [pos_E_header, pos_C_header, pos_D_header, pos_end]:
    # Determine the order in the file currently
    # Right now it's E (which was originally C), C (was D), D (was E)
    block_E = text[pos_E_header:pos_C_header]
    block_C = text[pos_C_header:pos_D_header]
    block_D = text[pos_D_header:pos_end]
    
    # Reassemble: C -> D -> E
    new_text = text[:pos_E_header] + block_C + block_D + block_E + text[pos_end:]
    
    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Blocks reordered successfully.")
else:
    print(f"Could not find all markers: E:{pos_E_header}, C:{pos_C_header}, D:{pos_D_header}, End:{pos_end}")
