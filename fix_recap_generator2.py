def fix_recap_generator2():
    with open('generate_recap_desk_review.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target = """        # Logic keputusan disamakan persis dengan generator Word dan Excel per RS
        is_priority = bool(row.get('triggered_rules_json')) and row.get('triggered_rules_json') != '[]'
        if not is_priority:
            is_priority = (jumlah_beda_dc > 0)
            
        if is_priority:
            is_tinggi = str(tingkat_risiko).lower() == 'tinggi' or float(knavp_skor) >= 4
            keputusan_reviewer = 'Direkomendasikan On-Site Audit' if is_tinggi else 'Audit Sampling (Klarifikasi)'
        else:
            keputusan_reviewer = 'Perlu Monitoring'
            
        keputusan_sistem = keputusan_reviewer # Disinkronkan"""
        
    replacement = """        # Move incbg and idrg_code up to calculate jumlah_beda_dc
        incbg = row.get('inacbg', '')
        idrg_code = str(row.get('idrg_code', '') or form_data.get('idrg_code', '') or '')
        jumlah_beda_dc = 1 if (incbg and idrg_code and incbg != idrg_code) else 0
        
        # Logic keputusan disamakan persis dengan generator Word dan Excel per RS
        is_priority = bool(row.get('triggered_rules_json')) and row.get('triggered_rules_json') != '[]'
        if not is_priority:
            is_priority = (jumlah_beda_dc > 0)
            
        if is_priority:
            is_tinggi = str(tingkat_risiko).lower() == 'tinggi' or float(knavp_skor) >= 4
            keputusan_reviewer = 'Direkomendasikan On-Site Audit' if is_tinggi else 'Audit Sampling (Klarifikasi)'
        else:
            keputusan_reviewer = 'Perlu Monitoring'
            
        keputusan_sistem = keputusan_reviewer # Disinkronkan"""
        
    if target in content:
        content = content.replace(target, replacement)
        with open('generate_recap_desk_review.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed recap generator 2!")

if __name__ == '__main__':
    fix_recap_generator2()
