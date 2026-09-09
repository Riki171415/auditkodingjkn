import sys

lines = open('modules/export_generator.py', encoding='utf-8').readlines()
lampiran_lines = []
for i, l in enumerate(lines):
    if 'LAMPIRAN' in l or 'Lampiran' in l.lower() or 'di_items' in l:
        lampiran_lines.append(f"{i+1}: {l.strip()}")

with open('temp_lampiran.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lampiran_lines))
