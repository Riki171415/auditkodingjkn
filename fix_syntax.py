import os
import re

def fix_syntax(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The exact string with bad indentation
    bad_str = "    try: c_dict['triggered_rules'] = __import__('json').loads(c.get('triggered_rules_json') or '[]')\n            except: c_dict['triggered_rules'] = []"
    good_str = "    try:\n        c_dict['triggered_rules'] = __import__('json').loads(c.get('triggered_rules_json') or '[]')\n    except:\n        c_dict['triggered_rules'] = []"
    
    content = content.replace(bad_str, good_str)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

fix_syntax("generate_adam_malik.py")
fix_syntax("generate_word_lhr_per_rs.py")
print("Syntax fixed!")
