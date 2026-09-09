def fix_typo():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    bad_string = "rule_counts['lainnya'] = rule_counts.get('lainnya, 0') + 1"
    good_string = "rule_counts['lainnya'] = rule_counts.get('lainnya', 0) + 1"
    
    if bad_string in content:
        content = content.replace(bad_string, good_string)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Typo fixed!")
    else:
        print("Could not find typo!")

if __name__ == '__main__':
    fix_typo()
