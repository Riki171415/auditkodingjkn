"""Read-only reconciliation of existing national and hospital exports."""
from pathlib import Path
from collections import Counter
import json
import openpyxl

BASE = Path(__file__).resolve().parents[1]

def read_sheet(path, sheet):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    it = ws.iter_rows(values_only=True)
    headers = next(it)
    rows = [dict(zip(headers, row)) for row in it if any(v is not None for v in row)]
    wb.close()
    return rows

def main():
    national = sorted((BASE / 'exports/rekap').glob('*.xlsx'))[-1]
    summaries = read_sheet(national, 'Ringkasan Eksekutif')
    master = read_sheet(national, 'Master Data (Rincian)')
    national_by_key = {(str(r['Kode RS']), str(r['Nomor SEP'])): r for r in master}
    total_rs = Counter()
    total_nat = Counter(r['Keputusan Reviewer'] for r in master)
    transitions = Counter()
    missing = extra = 0
    hospitals = []
    metrics = ['Total Kasus Di-Review', 'Lanjut On-Site Audit', 'Perlu Monitoring', 'Tidak Perlu Tindak Lanjut', 'Data Tidak Cukup']
    summary_rs = Counter()
    summary_nat = Counter({k: sum(r.get(k, 0) or 0 for r in summaries) for k in metrics})
    seen = set()
    for path in sorted((BASE / 'exports/rekap_per_rs').glob('*.xlsx')):
        summary = read_sheet(path, 'Ringkasan Eksekutif RS')[0]
        detail = read_sheet(path, 'Rincian SEP Kasus')
        counts = Counter(r['Rekomendasi Reviewer (Desk Review)'] for r in detail)
        total_rs.update(counts)
        summary_rs.update({k: summary.get(k, 0) or 0 for k in metrics})
        mismatch = 0
        for row in detail:
            key = str(summary['Kode RS']), str(row['Nomor SEP'])
            seen.add(key)
            other = national_by_key.get(key)
            if other is None:
                extra += 1
            elif other['Keputusan Reviewer'] != row['Rekomendasi Reviewer (Desk Review)']:
                mismatch += 1
                transitions[(other['Keputusan Reviewer'], row['Rekomendasi Reviewer (Desk Review)'])] += 1
        ns = next((r for r in summaries if str(r['Kode RS']) == str(summary['Kode RS'])), {})
        hospitals.append({'kode_rs': summary['Kode RS'], 'nama': summary['Nama Rumah Sakit'], 'mismatch': mismatch, 'national': {k: ns.get(k) for k in metrics}, 'per_rs': {k: summary.get(k) for k in metrics}, 'path': str(path)})
    missing = len(set(national_by_key) - seen)
    result = {'national_file': str(national), 'hospital_count': len(hospitals), 'national_rows': len(master), 'national_unique': len(national_by_key), 'per_rs_unique': len(seen), 'missing_from_per_rs': missing, 'extra_in_per_rs': extra, 'national_decisions': total_nat, 'per_rs_decisions': total_rs, 'national_summary': summary_nat, 'per_rs_summary': summary_rs, 'transitions': [{'national': k[0], 'per_rs': k[1], 'count': v} for k,v in transitions.items()], 'affected_hospitals': sum(h['mismatch'] > 0 for h in hospitals), 'examples': sorted(hospitals, key=lambda h: h['mismatch'], reverse=True)[:3]}
    print(json.dumps(result, ensure_ascii=True, indent=2))

if __name__ == '__main__':
    main()
