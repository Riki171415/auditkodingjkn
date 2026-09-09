import os

def insert_line(file_path, target, line_to_insert):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(file_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line)
            if target in line:
                # Calculate indentation
                indent = len(line) - len(line.lstrip())
                f.write(' ' * indent + line_to_insert + '\n')

# 1. Fix generate_word_lhr_per_rs.py
target_1 = "c_dict['knavp_skor'] = fd.get('knavp_skor'"
line_to_add_1 = "try: c_dict['triggered_rules'] = __import__('json').loads(c.get('triggered_rules_json') or '[]')\n" + \
                "            except: c_dict['triggered_rules'] = []"
insert_line("generate_word_lhr_per_rs.py", target_1, line_to_add_1)

# 2. Fix generate_adam_malik.py
insert_line("generate_adam_malik.py", target_1, line_to_add_1)

# 3. Fix generate_laporan_akhir_nasional.py
file_path_3 = "generate_laporan_akhir_nasional.py"
with open(file_path_3, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "triggered = r.get('triggered_rules', [])",
    "try:\n            triggered = json.loads(r.get('triggered_rules_json') or '[]')\n        except:\n            triggered = []"
)

with open(file_path_3, "w", encoding="utf-8") as f:
    f.write(content)

print("Pipeline JSON parser fixed!")
