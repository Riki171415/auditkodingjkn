def fix_array():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    bad_string = """    cases_dc_only = [
        c for c in cases
        if not c.get('triggered_rules')
        and int(c.get('jumlah_beda_dual_coding', 0)) > 0

    priority_cases = cases_with_rules + cases_dc_only"""
    
    good_string = """    cases_dc_only = [
        c for c in cases
        if not c.get('triggered_rules')
        and int(c.get('jumlah_beda_dual_coding', 0)) > 0
    ]

    priority_cases = cases_with_rules + cases_dc_only"""
    
    if bad_string in content:
        content = content.replace(bad_string, good_string)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Array fixed!")
    else:
        print("bad_string not found for array!")

if __name__ == '__main__':
    fix_array()
