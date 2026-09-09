import os
import re

def fix_indent(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for i in range(len(lines)):
        if "c_dict['triggered_rules'] = __import__('json')" in lines[i]:
            lines[i] = "                c_dict['triggered_rules'] = __import__('json').loads(c.get('triggered_rules_json') or '[]')\n"
        elif "except:" in lines[i] and "c_dict" not in lines[i]:
            lines[i] = "            except:\n"
        elif "c_dict['triggered_rules'] = []" in lines[i]:
            lines[i] = "                c_dict['triggered_rules'] = []\n"
            
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

fix_indent("generate_word_lhr_per_rs.py")
fix_indent("generate_adam_malik.py")
print("Indentation fixed.")
