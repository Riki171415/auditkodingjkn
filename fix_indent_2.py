def fix_indent():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    bad_text = """        row_cells[1].text = str(c.get('sep', ''))
                rules = c.get('triggered_rules')
        if rules and isinstance(rules, list):
            rule_texts = [f"• [{r.get('rule_id', '')}] {r.get('nama_aturan', '')}" for r in rules]
            row_cells[2].text = "\\n".join(rule_texts)
        else:
            row_cells[2].text = "Perbedaan Dual Coding Tinggi" 
        row_cells[3].text = str(c.get('tingkat_risiko', 'Tinggi'))"""
        
    good_text = """        row_cells[1].text = str(c.get('sep', ''))
        rules = c.get('triggered_rules')
        if rules and isinstance(rules, list):
            rule_texts = [f"• [{r.get('rule_id', '')}] {r.get('nama_aturan', '')}" for r in rules]
            row_cells[2].text = "\\n".join(rule_texts)
        else:
            row_cells[2].text = "Perbedaan Dual Coding Tinggi"
        row_cells[3].text = str(c.get('tingkat_risiko', 'Tinggi'))"""

    if bad_text in content:
        content = content.replace(bad_text, good_text)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Indentation fixed!")
    else:
        print("Target line not found!")

if __name__ == '__main__':
    fix_indent()
