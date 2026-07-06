import sys; sys.path.insert(0, '.')
from modules.data_loader import load_individual_data
from modules.rule_engine import check_dual_coding_discrepancy

df = load_individual_data()
sep_test = '0101R0010925V012262'
row = df[df['sep'] == sep_test].iloc[0]
case = row.to_dict()
res = check_dual_coding_discrepancy(case)
print(f"INA proc: {case.get('proclist')}")
print(f"iDRG proc: {case.get('proclist_idrg')}")
for r in res['diag_rows']:
    print(r)
for r in res['proc_rows']:
    print(r)
print(f"jumlah_beda_total: {res['jumlah_beda_total']}")
