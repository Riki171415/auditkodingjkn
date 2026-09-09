import os
import re

def fix_narasi():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # The target to replace is:
    # f"Berdasarkan hasil validasi KNAVP terhadap {len(cases)} kasus yang direviu pada {rs_name}, "\n                f"kelompok temuan paling dominan adalah {dom_label} sebanyak {dom_count} temuan. "
    
    # We will replace it with:
    # f"Berdasarkan hasil validasi KNAVP terhadap {len(cases)} kasus yang direviu pada {rs_name}, "\n                f"secara keseluruhan terdapat {total_temuan_all} temuan pelanggaran aturan. "\n                f"Dari seluruh pelanggaran tersebut, kelompok temuan paling dominan adalah {dom_label} sebanyak {dom_count} temuan. "

    target = r'f"Berdasarkan hasil validasi KNAVP terhadap \{len\(cases\)\} kasus yang direviu pada \{rs_name\}, "\s*\n\s*f"kelompok temuan paling dominan adalah \{dom_label\} sebanyak \{dom_count\} temuan\. "'
    
    replacement = (
        'f"Berdasarkan hasil validasi KNAVP terhadap {len(cases)} kasus yang direviu pada {rs_name}, secara keseluruhan terdapat {total_temuan_all} temuan pelanggaran aturan. "\\n'
        '                f"Dari seluruh pelanggaran tersebut, kelompok temuan paling dominan adalah {dom_label} sebanyak {dom_count} temuan. "'
    )

    new_content, count = re.subn(target, replacement, content)
    
    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Replaced {count} occurrences of the narrative.")

if __name__ == '__main__':
    fix_narasi()
