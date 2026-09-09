import sys
sys.path.insert(0, './modules')
from rule_engine import load_rules
r = load_rules()
print('Loaded', len(r), 'rules')
