import sys
sys.path.insert(0, './modules')
from data_loader import get_case_by_sep
case = get_case_by_sep('0201R0011125V014938')
print('Diag:', case['diaglist'])
print('Proc:', case['proclist'])
