def fix_recap_generator():
    with open('generate_recap_desk_review.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Part 1: Update the logic
    target_logic = """        # Consistent Keputusan Sistem and Reviewer
        keputusan_sistem = form_data.get('keputusan_sistem')
        if not keputusan_sistem:
            keputusan_sistem = 'Tidak diperlukan tindak lanjut'
            
        keputusan_reviewer = form_data.get('keputusan') or keputusan_sistem"""
        
    replacement_logic = """        # Logic keputusan disamakan persis dengan generator Word dan Excel per RS
        is_priority = bool(row.get('triggered_rules_json')) and row.get('triggered_rules_json') != '[]'
        if not is_priority:
            is_priority = (jumlah_beda_dc > 0)
            
        if is_priority:
            is_tinggi = str(tingkat_risiko).lower() == 'tinggi' or float(knavp_skor) >= 4
            keputusan_reviewer = 'Direkomendasikan On-Site Audit' if is_tinggi else 'Audit Sampling (Klarifikasi)'
        else:
            keputusan_reviewer = 'Perlu Monitoring'
            
        keputusan_sistem = keputusan_reviewer # Disinkronkan
"""
    if target_logic in content:
        content = content.replace(target_logic, replacement_logic)

    # Part 2: Add the red font
    target_font = """                    # Colour-code risiko rows
                    if sheet_name == 'Master Data (Rincian)':"""
                    
    replacement_font = """                    if cell.value == 'Direkomendasikan On-Site Audit':
                        cell.font = Font(size=8, color='FF0000', bold=True)
                        
                    # Colour-code risiko rows
                    if sheet_name == 'Master Data (Rincian)':"""
                    
    if target_font in content:
        content = content.replace(target_font, replacement_font)

    with open('generate_recap_desk_review.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed recap generator!")

if __name__ == '__main__':
    fix_recap_generator()
