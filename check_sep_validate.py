import sys
sys.path.insert(0, './modules')
from data_loader import get_case_by_sep
from rule_engine import validate_case
import json
case = get_case_by_sep('0201R0011125V014938')
rules = validate_case(case)
print('TRIGGERED:')
for r in rules: print('-', r['rule_id'], r['nama_aturan'])
