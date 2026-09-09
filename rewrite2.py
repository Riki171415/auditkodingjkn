import sys
import re

def rewrite_fallback():
    with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/modules/report_word.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    fallback_code = '''    for t_idx, c_id in table_mappings:
        c_idx = [5,6,7,8].index(t_idx)
        c_labels, c_values = charts[c_idx]
        
        if len(doc.tables) > t_idx and c_id in chart_info:
            c_data = chart_info[c_id]
            final_charts.append((c_data['labels'], c_data['values']))
            table = doc.tables[t_idx]
            for row in table.rows[1:]:
                try:
                    k = row.cells[0].text.strip().lower()
                    for idx_lbl, lbl in enumerate(c_data['labels']):
                        if k in lbl.lower() or lbl.lower() in k:
                            row.cells[1].text = str(c_data['values'][idx_lbl])
                            break
                except Exception:
                    pass
        elif len(doc.tables) > t_idx:
            # Fallback to dynamically calculated charts
            final_charts.append((c_labels, c_values))
            label_to_val = {str(k).lower(): v for k, v in zip(c_labels, c_values)}
            table = doc.tables[t_idx]
            for row in table.rows[1:]:
                try:
                    k = row.cells[0].text.strip().lower()
                    for lbl, val in label_to_val.items():
                        if k in lbl or lbl in k:
                            row.cells[1].text = str(val)
                            break
                except Exception:
                    pass
        else:
            final_charts.append(([], []))'''
            
    # Find the loop over table_mappings
    start_str = "    for t_idx, c_id in table_mappings:"
    end_str = "    from PIL import Image, ImageDraw, ImageFont"
    
    idx_start = code.find(start_str)
    idx_end = code.find(end_str)
    
    if idx_start != -1 and idx_end != -1:
        code = code[:idx_start] + fallback_code + "\n" + code[idx_end:]
        with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/modules/report_word.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("Fallback updated successfully.")
    else:
        print("Could not find block.")

rewrite_fallback()
