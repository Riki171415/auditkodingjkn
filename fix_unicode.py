import re

with open('run_framework_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace special unicode chars with ASCII equivalents
replacements = [
    ('\u2500', '-'), ('\u2501', '-'), ('\u2502', '|'),
    ('\u2190', '<-'), ('\u2192', '->'), ('\u2014', '--'), ('\u2013', '-'),
    ('\u2018', "'"), ('\u2019', "'"), ('\u201c', '"'), ('\u201d', '"'),
    ('\u2551', '|'), ('\u2550', '='), ('\u2560', '+'), ('\u2563', '+'),
    ('\u2566', '+'), ('\u2569', '+'), ('\u2554', '+'), ('\u2557', '+'),
    ('\u255a', '+'), ('\u255d', '+'), ('\u2588', '#'), ('\u2591', '-'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Also fix em-dash and similar
content = re.sub(r'[\u2010-\u2015]', '-', content)
content = re.sub(r'[\u2018-\u201f]', '"', content)
content = re.sub(r'[\u2192-\u21ff]', '->', content)

with open('run_framework_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - unicode chars replaced in run_framework_v2.py')
