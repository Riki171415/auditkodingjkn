def fix_lampiran_indent():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    bad_string = "document.add_page_break()\n    # ── BAB III KESIMPULAN DAN REKOMENDASI"
    good_string = "    document.add_page_break()\n    # ── BAB III KESIMPULAN DAN REKOMENDASI"
    
    if bad_string in content:
        content = content.replace(bad_string, good_string)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Lampiran indent fixed!")
    else:
        print("bad_string not found!")

if __name__ == '__main__':
    fix_lampiran_indent()
