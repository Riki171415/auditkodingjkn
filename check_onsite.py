import sys, json
sys.path.insert(0, '.')
from modules.db_manager import get_recap_desk_review

data = get_recap_desk_review()

# Filter kasus On-Site
onsite = []
for r in data:
    try:
        fd = json.loads(r.get('tindakan_reviewer') or '{}')
    except:
        fd = {}
    kep = fd.get('keputusan_sistem', '')
    if kep == 'Direkomendasikan On-Site Audit':
        r['_fd'] = fd
        onsite.append(r)

print(f'Total On-Site cases: {len(onsite)}')
print()
for c in onsite:
    rules = c.get('triggered_rules', [])
    fd = c.get('_fd', {})
    rule_ids = [r.get('rule_id','') for r in rules]
    sep = c['sep']
    nama_rs = c.get('nama_rs', '')
    diaglist = str(c.get('diaglist', ''))[:60]
    knavp = fd.get('knavp_skor', 0)
    risiko = fd.get('tingkat_risiko', '')
    beda_dc = fd.get('jumlah_beda_dual_coding', 0)
    print(f"SEP: {sep}")
    print(f"  RS: {nama_rs}")
    print(f"  triggered_rules count: {len(rules)}")
    print(f"  rule_ids: {rule_ids}")
    print(f"  knavp_skor: {knavp}")
    print(f"  tingkat_risiko: {risiko}")
    print(f"  jumlah_beda_dc: {beda_dc}")
    print(f"  diaglist: {diaglist}")
    print()
