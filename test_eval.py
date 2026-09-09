import sys
sys.path.insert(0, './modules')
from rule_engine import evaluate_rule, load_rules, parse_codes
from data_loader import get_case_by_sep
case=get_case_by_sep('0201R0011125V014938')
rules = load_rules()
diags = parse_codes(case['diaglist'])
procs = parse_codes(case['proclist'])
for r in rules:
    if r['rule_id'] in ('AUDIT-COD-39', 'AUDIT-COD-76'):
        res = evaluate_rule(r, diags, procs, case)
        print(r['rule_id'], res)
