import json
import re

def rewrite_report_word():
    with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/modules/report_word.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 1. Add chart_info dictionary parsing
    parsing_code = '''
            if line.startswith('`chart') or line.endswith('`chart'):
                i += 1
                c_block = []
                while i < len(lines) and not lines[i].strip().startswith('`'):
                    c_block.append(lines[i].lstrip('>').strip())
                    i += 1
                c_text = '\\n'.join(c_block)
                c_id = 'unknown'
                c_labels = []
                c_values = []
                
                # simple regex parser
                m_id = re.search(r'id:\s*(\S+)', c_text)
                if m_id: c_id = m_id.group(1)
                
                m_labels = re.search(r'labels:(.*?)(?:values:|$)', c_text, re.DOTALL)
                if m_labels:
                    c_labels = [x.strip('- ') for x in m_labels.group(1).split('\\n') if x.strip().startswith('-')]
                
                m_values = re.search(r'values:(.*?)$', c_text, re.DOTALL)
                if m_values:
                    c_values = [int(x.strip('- ')) for x in m_values.group(1).split('\\n') if x.strip().startswith('-')]
                
                if c_id != 'unknown':
                    chart_info[c_id] = {'labels': c_labels, 'values': c_values}
                    
            elif line.startswith('`'):
'''
    code = code.replace("            if line.startswith('`'):", parsing_code)
    code = code.replace("blocks = []", "blocks = []\n    chart_info = {}")
    
    # 2. Update tables 5-8 logic to use chart_info
    chart_replacement = '''
    # Update Tables 5-8 in place to preserve Lampiran 5 template formatting
    c_pop = f"chart_{code}_004"
    c_rek = f"chart_{code}_001"
    c_kat = f"chart_{code}_002"
    c_mis = f"chart_{code}_003"
    
    table_mappings = [
        (5, c_pop),
        (6, c_rek),
        (7, c_kat),
        (8, c_mis)
    ]
    
    final_charts = []
    
    for t_idx, c_id in table_mappings:
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
        else:
            final_charts.append(([], []))
            
    from PIL import Image, ImageDraw, ImageFont
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(font_path), 20) if font_path.exists() else ImageFont.load_default()
    for p, (labels, values) in zip(chart_paragraphs, final_charts):
        if not labels:
            continue
'''
    
    idx_start = code.find("    # Update Tables 5-8 in place")
    idx_end = code.find("        img = Image.new('RGB', (1200, max(190, len(labels)*55+45)), 'white')")
    code = code[:idx_start] + chart_replacement + code[idx_end:]
    
    with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/modules/report_word.py', 'w', encoding='utf-8') as f:
        f.write(code)
    
    print("report_word.py rewritten successfully!")

rewrite_report_word()
