"""
AGENT 1 — DATA REVIEWER
========================
Kementerian Kesehatan RI / Pusat Pembiayaan Kesehatan
AI Report Generation Framework V2

TUGAS:
- Membaca data mentah dari database (audit.db + data.db)
- Mengekstrak SELURUH angka, tabel, statistik, rule, ICD, prosedur, hasil validasi
- Menghasilkan JSON metadata terstruktur
- TIDAK BOLEH menulis narasi, opini, atau kesimpulan
"""

import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'data_review')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cochran sample master table
COCHRAN_MASTER = {
    '3573011': {'total_ri': 38128, 'sample_ri': 60, 'total_rj': 287556, 'sample_rj': 60, 'rs_name': 'RS DR. SAIFUL ANWAR'},
    '3173025': {'total_ri': 32421, 'sample_ri': 60, 'total_rj': 470647, 'sample_rj': 60, 'rs_name': 'RS PAD GATOT SOEBROTO'},
    '1371464': {'total_ri': 6489,  'sample_ri': 60, 'total_rj': 62529,  'sample_rj': 60, 'rs_name': 'RS UNIVERSITAS ANDALAS'},
    '3273015': {'total_ri': 51065, 'sample_ri': 60, 'total_rj': 362347, 'sample_rj': 60, 'rs_name': 'RSU DR. HASAN SADIKIN'},
    '3374010': {'total_ri': 51848, 'sample_ri': 60, 'total_rj': 470691, 'sample_rj': 60, 'rs_name': 'RSU DR. KARIADI'},
    '1371010': {'total_ri': 37588, 'sample_ri': 60, 'total_rj': 275776, 'sample_rj': 60, 'rs_name': 'RSU DR. M.DJAMIL PADANG'},
    '3372015': {'total_ri': 56546, 'sample_ri': 60, 'total_rj': 415528, 'sample_rj': 60, 'rs_name': 'RSU DR. MOEWARDI SURAKARTA'},
    '1671013': {'total_ri': 44463, 'sample_ri': 60, 'total_rj': 302932, 'sample_rj': 60, 'rs_name': 'RSU DR. MOHAMMAD HOESIN'},
    '7371325': {'total_ri': 35885, 'sample_ri': 60, 'total_rj': 290209, 'sample_rj': 60, 'rs_name': 'RSU DR. W. SUDIROHUSODO'},
    '1275655': {'total_ri': 31146, 'sample_ri': 60, 'total_rj': 253319, 'sample_rj': 60, 'rs_name': 'RSU H. ADAM MALIK'},
    '7171013': {'total_ri': 31462, 'sample_ri': 60, 'total_rj': 277498, 'sample_rj': 60, 'rs_name': 'RSU PROF.DR. R.D KANDOU MANADO'},
    '5271010': {'total_ri': 32537, 'sample_ri': 60, 'total_rj': 204887, 'sample_rj': 60, 'rs_name': 'RSU PROV. NTB'},
    '3603010': {'total_ri': 17844, 'sample_ri': 60, 'total_rj': 203713, 'sample_rj': 60, 'rs_name': 'RSU TANGERANG'},
    '3173521': {'total_ri': 19656, 'sample_ri': 60, 'total_rj': 194073, 'sample_rj': 60, 'rs_name': 'RSU TARAKAN'},
    '1471011': {'total_ri': 21099, 'sample_ri': 60, 'total_rj': 123535, 'sample_rj': 60, 'rs_name': 'RSUD ARIFIN ACHMAD'},
    '3578016': {'total_ri': 51808, 'sample_ri': 60, 'total_rj': 498146, 'sample_rj': 60, 'rs_name': 'RSUD DR. SOETOMO'},
    '3404015': {'total_ri': 51988, 'sample_ri': 60, 'total_rj': 657288, 'sample_rj': 60, 'rs_name': 'RSUP DR. SARDJITO'},
    '3310015': {'total_ri': 24930, 'sample_ri': 60, 'total_rj': 161349, 'sample_rj': 60, 'rs_name': 'RSUP DR. SOERADJI TIRTONEGORO'},
    '3171012': {'total_ri': 34308, 'sample_ri': 60, 'total_rj': 345731, 'sample_rj': 60, 'rs_name': 'RSUP FATMAWATI'},
    '3172013': {'total_ri': 25620, 'sample_ri': 60, 'total_rj': 277172, 'sample_rj': 60, 'rs_name': 'RSUP PERSAHABATAN'},
    '5171016': {'total_ri': 43243, 'sample_ri': 60, 'total_rj': 404030, 'sample_rj': 60, 'rs_name': 'RSUP SANGLAH DENPASAR'},
    '3578811': {'total_ri': 1011,  'sample_ri': 57, 'total_rj': 2241,   'sample_rj': 59, 'rs_name': 'RSUP SURABAYA'},
    '1471226': {'total_ri': 23280, 'sample_ri': 60, 'total_rj': 255945, 'sample_rj': 60, 'rs_name': 'RS AWAL BROS PEKANBARU'},
    '1471067': {'total_ri': 4927,  'sample_ri': 60, 'total_rj': 60694,  'sample_rj': 60, 'rs_name': 'RS EKA HOSPITAL PEKANBARU'},
    '3603115': {'total_ri': 1107,  'sample_ri': 57, 'total_rj': 26882,  'sample_rj': 60, 'rs_name': 'RS EMC ALAM SUTERA'},
    '3172495': {'total_ri': 1901,  'sample_ri': 59, 'total_rj': 65475,  'sample_rj': 60, 'rs_name': 'RS EMC PULOMAS'},
    '3671065': {'total_ri': 4734,  'sample_ri': 60, 'total_rj': 76017,  'sample_rj': 60, 'rs_name': 'RS EMC TANGERANG'},
    '3577099': {'total_ri': 1420,  'sample_ri': 58, 'total_rj': 8475,   'sample_rj': 60, 'rs_name': 'RS HERMINA MADIUN'},
    '3671080': {'total_ri': 4336,  'sample_ri': 60, 'total_rj': 55613,  'sample_rj': 60, 'rs_name': 'RS MAYAPADA'},
    '3471052': {'total_ri': 8780,  'sample_ri': 60, 'total_rj': 127441, 'sample_rj': 60, 'rs_name': 'RS PANTI RAPIH'},
    '3578086': {'total_ri': 6667,  'sample_ri': 60, 'total_rj': 190324, 'sample_rj': 60, 'rs_name': 'RS PHC'},
    '3471041': {'total_ri': 7485,  'sample_ri': 60, 'total_rj': 101345, 'sample_rj': 60, 'rs_name': 'RS PKU MUHAMMADIYAH YOGYAKARTA'},
    '3275392': {'total_ri': 9522,  'sample_ri': 60, 'total_rj': 133245, 'sample_rj': 60, 'rs_name': 'RS PRIMAYA BEKASI BARAT'},
    '3671203': {'total_ri': 11078, 'sample_ri': 60, 'total_rj': 174720, 'sample_rj': 60, 'rs_name': 'RS PRIMAYA TANGERANG'},
    '3276017': {'total_ri': 12153, 'sample_ri': 60, 'total_rj': 149658, 'sample_rj': 60, 'rs_name': 'RS SENTRA MEDIKA'},
    '3201230': {'total_ri': 14757, 'sample_ri': 60, 'total_rj': 188543, 'sample_rj': 60, 'rs_name': 'RS SENTRA MEDIKA CIBINONG'},
    '5103035': {'total_ri': 2773,  'sample_ri': 59, 'total_rj': 56328,  'sample_rj': 60, 'rs_name': 'RS SILOAM BALI'},
    '3578443': {'total_ri': 3263,  'sample_ri': 59, 'total_rj': 63141,  'sample_rj': 60, 'rs_name': 'RS SILOAM HOSPITALS SURABAYA'},
    '3671054': {'total_ri': 11775, 'sample_ri': 60, 'total_rj': 238034, 'sample_rj': 60, 'rs_name': 'RS SILOAM INTERNATIONAL HOSPITAL'},
    '3374076': {'total_ri': 17430, 'sample_ri': 60, 'total_rj': 122987, 'sample_rj': 60, 'rs_name': 'RS SULTAN AGUNG SEMARANG'},
    '3374043': {'total_ri': 4838,  'sample_ri': 60, 'total_rj': 69678,  'sample_rj': 60, 'rs_name': 'RS TELOGOREJO'},
    '3275115': {'total_ri': 23895, 'sample_ri': 60, 'total_rj': 283538, 'sample_rj': 60, 'rs_name': 'RSIA HERMINA BEKASI'},
    '3273486': {'total_ri': 28468, 'sample_ri': 60, 'total_rj': 262808, 'sample_rj': 60, 'rs_name': 'RSU SANTOSA HOSPITAL BANDUNG CENTRAL'},
    '3404189': {'total_ri': 21837, 'sample_ri': 60, 'total_rj': 320729, 'sample_rj': 60, 'rs_name': 'RS AKADEMIK UNIVERSITAS GADJAH MADA'},
}

GROUPED_RULES = {
    'mutually_exclusive':        {'title': 'Mutually Exclusive (Includes/Excludes)', 'codes': ['KNAVP-ME', 'ME', 'mutually_exclusive']},
    'underlying_manifestation':  {'title': 'Underlying & Manifestation',            'codes': ['KNAVP-UM', 'UM', 'underlying_manifestation']},
    'procedure_validation':      {'title': 'Procedure Validation',                   'codes': ['KNAVP-PV', 'PV', 'procedure_validation']},
    'unbundling':                {'title': 'Unbundling',                             'codes': ['KNAVP-UB', 'UB', 'unbundling']},
    'medical_evidence':          {'title': 'Medical Evidence',                       'codes': ['KNAVP-MEV', 'MEV', 'medical_evidence']},
    'administrative_validation': {'title': 'Administrative Validation',              'codes': ['KNAVP-ADM', 'ADM', 'administrative_validation']},
    'age_validation':            {'title': 'Age Validation',                         'codes': ['KNAVP-AGE', 'AGE', 'age_validation']},
    'los_validation':            {'title': 'LOS Validation',                         'codes': ['KNAVP-LOS', 'LOS', 'los_validation']},
    'diagnosis_validation':      {'title': 'Diagnosis Validation',                   'codes': ['diagnosis_validation', 'DV']},
    'coding_standard':           {'title': 'Coding Standard',                        'codes': ['coding_standard', 'CS']},
}


def classify_rule(rule_id: str, kategori: str = '') -> str:
    """
    Klasifikasi rule berdasarkan field 'kategori' (prioritas) atau 'rule_id'.
    Data DB: rule_id='AUDIT-COD-39', kategori='procedure_validation'
    """
    # Prioritas 1: gunakan field kategori langsung
    if kategori:
        kat_lower = kategori.lower().strip()
        for cat_key, cat_info in GROUPED_RULES.items():
            if kat_lower == cat_key or kat_lower in [c.lower() for c in cat_info['codes']]:
                return cat_key
        # Partial match pada kategori
        for cat_key in GROUPED_RULES:
            if cat_key in kat_lower or kat_lower in cat_key:
                return cat_key

    # Prioritas 2: fallback ke rule_id prefix
    if rule_id:
        rule_id_upper = rule_id.upper()
        for cat_key, cat_info in GROUPED_RULES.items():
            if any(code.upper() in rule_id_upper for code in cat_info['codes']):
                return cat_key

    return 'other'


def get_db():
    from modules.db_manager import get_audit_db
    return get_audit_db()


def run(kode_rs: str, verbose: bool = True) -> dict:
    """
    Eksekusi Agent 1 untuk satu RS.
    Return: dict metadata (juga disimpan ke JSON file).
    """
    if verbose:
        print(f"\n[AGENT 1] DATA REVIEWER — RS: {kode_rs}")
        print("=" * 60)

    conn = get_db()
    cursor = conn.cursor()

    # --- 1. AMBIL DATA KASUS DARI DB ---
    cursor.execute("""
        SELECT
            d.sep, d.kode_rs, d.nama_rs, d.inacbg,
            d.diaglist, d.proclist, d.alos,
            d.idrg_code, d.idrg_diag_lists, d.idrg_proc_lists,
            k.triggered_rules_json, k.tindakan_reviewer
        FROM datadb.individual_data d
        LEFT JOIN kkr_dr01 k ON d.sep = k.sep AND d.kode_rs = k.kode_rs
        WHERE d.kode_rs = ?
    """, (kode_rs,))
    rows = cursor.fetchall()

    if not rows:
        print(f"  [WARN] Tidak ada data ditemukan untuk kode_rs={kode_rs}")
        conn.close()
        return {}

    cases = []
    for row in rows:
        c = dict(row)
        try:
            c['triggered_rules'] = json.loads(c.get('triggered_rules_json') or '[]')
        except Exception:
            c['triggered_rules'] = []
        try:
            fd = json.loads(c.get('tindakan_reviewer') or '{}')
        except Exception:
            fd = {}
        c['knavp_skor']    = float(fd.get('knavp_skor', 0) or 0)
        c['tingkat_risiko']= fd.get('tingkat_risiko', '-') or '-'
        c['keputusan']     = fd.get('keputusan', fd.get('keputusan_sistem', '-')) or '-'
        c['jumlah_beda_dual_coding'] = int(fd.get('jumlah_beda_dual_coding', 0) or 0)
        cases.append(c)

    rs_name = rows[0]['nama_rs'] or COCHRAN_MASTER.get(kode_rs, {}).get('rs_name', kode_rs)
    conn.close()

    # --- 2. POPULASI & SAMPEL ---
    cochran = COCHRAN_MASTER.get(kode_rs, {})
    total_ri  = cochran.get('total_ri', 0)
    total_rj  = cochran.get('total_rj', 0)
    total_pop = total_ri + total_rj
    sample_ri = sum(1 for c in cases if not str(c.get('inacbg', '')).endswith('-0'))
    sample_rj = sum(1 for c in cases if str(c.get('inacbg', '')).endswith('-0'))
    total_sample = len(cases)

    # --- 3. KNAVP ALERTS ---
    rule_counts    = defaultdict(int)
    rule_details   = defaultdict(list)  # category → list of rule_id occurrences
    icd_freq       = defaultdict(int)
    proc_freq      = defaultdict(int)
    all_alerts     = []
    severity_counts = {'High': 0, 'Medium': 0, 'Low': 0}

    for c in cases:
        # ICD frequency — parse from diaglist field
        for code in (c.get('diaglist', '') or '').split(';'):
            code = code.strip().split(':')[0].strip()  # handle 'A00.0:desc' format
            if code and code != 'nan' and len(code) >= 3:
                icd_freq[code] += 1
        # Procedure frequency — parse from proclist field
        for code in (c.get('proclist', '') or '').split(';'):
            code = code.strip().split(':')[0].strip()
            if code and code != 'nan' and len(code) >= 2:
                proc_freq[code] += 1
        # Rule alerts
        for rule in c.get('triggered_rules', []):
            # Gunakan field 'kategori' dari rule JSON (prioritas utama)
            cat = classify_rule(
                rule.get('rule_id', ''),
                rule.get('kategori', '') or rule.get('kelompok_rule', '')
            )
            rule_counts[cat] += 1
            rule_details[cat].append({
                'rule_id':    rule.get('rule_id', ''),
                'nama_aturan':rule.get('nama_aturan', ''),
                'severity':   rule.get('severity', ''),
                'kategori':   rule.get('kategori', ''),
                'kelompok':   rule.get('kelompok_rule', ''),
                'sep':        c.get('sep', ''),
            })
            sev = rule.get('severity', 'Low')
            if sev in severity_counts:
                severity_counts[sev] += 1
            else:
                severity_counts['Low'] += 1
            all_alerts.append(rule)

    # --- 4. TRIASE COUNTS ---
    onsite_cases   = []
    sampling_cases = []
    monitor_cases  = []
    for c in cases:
        k = str(c.get('keputusan', '')).lower()
        r = str(c.get('tingkat_risiko', '')).lower()
        skor = c.get('knavp_skor', 0)
        if 'on-site' in k or 'onsite' in k or r == 'tinggi' or skor >= 4:
            onsite_cases.append(c)
        elif 'sampling' in k or r == 'sedang' or skor >= 2:
            sampling_cases.append(c)
        else:
            monitor_cases.append(c)

    # Sort priority by risk desc
    def risk_weight(c):
        r = str(c.get('tingkat_risiko', '')).lower()
        if r == 'tinggi': return 3
        if r == 'sedang': return 2
        return 1

    priority_cases = sorted(
        [c for c in cases if c.get('triggered_rules') or c.get('jumlah_beda_dual_coding', 0) > 0],
        key=lambda x: (-risk_weight(x), -x.get('knavp_skor', 0))
    )

    # --- 5. DUAL CODING ---
    total_beda_dc    = sum(c.get('jumlah_beda_dual_coding', 0) for c in cases)
    mismatch_cases   = [c for c in cases if c.get('jumlah_beda_dual_coding', 0) > 0]
    match_cases_count = total_sample - len(mismatch_cases)
    mismatch_pct     = round(len(mismatch_cases) / total_sample * 100, 1) if total_sample else 0

    # --- 6. TOP ANOMALIES ---
    top_anomalies = sorted(
        [c for c in cases if c.get('triggered_rules')],
        key=lambda x: (-len(x.get('triggered_rules', [])), -x.get('knavp_skor', 0))
    )[:10]

    # --- 7. DOMINANT RULE CATEGORY ---
    dom_cat, dom_count = max(rule_counts.items(), key=lambda x: x[1]) if rule_counts else ('-', 0)
    dom_title = GROUPED_RULES.get(dom_cat, {}).get('title', dom_cat)

    # --- 8. SORTED RULE BREAKDOWN ---
    sorted_rule_breakdown = sorted(
        [{'category': k, 'title': GROUPED_RULES.get(k, {}).get('title', k), 'count': v}
         for k, v in rule_counts.items()],
        key=lambda x: -x['count']
    )

    # --- COMPOSE JSON METADATA ---
    metadata = {
        "_meta": {
            "agent": "Agent 1 — Data Reviewer",
            "framework": "AI Report Generation Framework V2",
            "generated_at": datetime.now().isoformat(),
            "kode_rs": kode_rs,
            "rs_name": rs_name,
        },
        "population": {
            "total": total_pop,
            "rawat_inap": total_ri,
            "rawat_jalan": total_rj,
            "source": "Cochran Master Table / Data Center Kemenkes RI",
        },
        "sample": {
            "total": total_sample,
            "rawat_inap": sample_ri,
            "rawat_jalan": sample_rj,
            "method": "Cochran Sampling Formula",
        },
        "knavp_validation": {
            "total_alerts": len(all_alerts),
            "severity_breakdown": severity_counts,
            "category_breakdown": sorted_rule_breakdown,
            "dominant_category": {
                "key": dom_cat,
                "title": dom_title,
                "count": dom_count,
                "percentage": round(dom_count / len(all_alerts) * 100, 1) if all_alerts else 0,
            },
            "rule_details_by_category": {k: v[:5] for k, v in rule_details.items()},  # max 5 examples per cat
        },
        "triase": {
            "onsite":            len(onsite_cases),
            "sampling":          len(sampling_cases),
            "monitor":           len(monitor_cases),
            "onsite_count":      len(onsite_cases),
            "sampling_count":    len(sampling_cases),
            "monitoring_count":  len(monitor_cases),
            "onsite_percentage": round(len(onsite_cases) / total_sample * 100, 1) if total_sample else 0,
        },
        "dual_coding": {
            "total_discrepancy": total_beda_dc,
            "cases_with_discrepancy": len(mismatch_cases),
            "mismatch_count":    len(mismatch_cases),
            "cases_matching": match_cases_count,
            "mismatch_pct":      mismatch_pct,
            "mismatch_percentage": mismatch_pct,
            "match_percentage": round(100 - mismatch_pct, 1),
        },
        "priority_cases": [
            {
                "sep": c.get('sep', ''),
                "inacbg": c.get('inacbg', ''),
                "idrg_code": c.get('idrg_code', ''),
                "diaglist": (c.get('diaglist', '') or '')[:80],
                "knavp_skor": c.get('knavp_skor', 0),
                "tingkat_risiko": c.get('tingkat_risiko', '-'),
                "keputusan": c.get('keputusan', '-'),
                "jumlah_beda_dc": c.get('jumlah_beda_dual_coding', 0),
                "triggered_rules_count": len(c.get('triggered_rules', [])),
                "triggered_rules": c.get('triggered_rules', [])[:3],  # top 3 rules per case
            }
            for c in priority_cases[:20]  # top 20 priority cases
        ],
        "top_anomalies": [
            {
                "sep": c.get('sep', ''),
                "rules_count": len(c.get('triggered_rules', [])),
                "knavp_skor": c.get('knavp_skor', 0),
                "diaglist": (c.get('diaglist', '') or '')[:60],
                "rules": [r.get('rule_id', '') for r in c.get('triggered_rules', [])]
            }
            for c in top_anomalies
        ],
        "icd_frequency": dict(sorted(icd_freq.items(), key=lambda x: -x[1])[:30]),
        "procedure_frequency": dict(sorted(proc_freq.items(), key=lambda x: -x[1])[:20]),
        "summary_stats": {
            "avg_knavp_skor": round(
                sum(c.get('knavp_skor', 0) for c in cases) / total_sample, 2
            ) if total_sample else 0,
            "cases_with_alerts": len([c for c in cases if c.get('triggered_rules')]),
            "alert_rate_pct": round(
                len([c for c in cases if c.get('triggered_rules')]) / total_sample * 100, 1
            ) if total_sample else 0,
            "total_priority": len(priority_cases),
        },
        # Lampiran data — kasus lengkap + detail rule untuk generate_from_md.py
        "cases": [
            {
                "sep":                    c.get('sep', ''),
                "inacbg":                 c.get('inacbg', ''),
                "idrg_code":              c.get('idrg_code', '-'),
                "knavp_skor":             c.get('knavp_skor', 0),
                "tingkat_risiko":         c.get('tingkat_risiko', '-'),
                "keputusan":              c.get('keputusan', '-'),
                "jumlah_beda_dual_coding":c.get('jumlah_beda_dual_coding', 0),
                "triggered_rules":        c.get('triggered_rules', []),
            }
            for c in cases
        ],
        "knavp_rule_details": {k: v for k, v in rule_details.items()},  # SEMUA rule per kategori
        "total_sample":       total_sample,
        "total_knavp_alerts": len(all_alerts),
        "severity_counts":    severity_counts,
    }

    # --- SIMPAN JSON ---
    out_path = os.path.join(OUTPUT_DIR, f'data_review_{kode_rs}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    if verbose:
        print(f"  Populasi   : {total_pop:,} kasus (RI: {total_ri:,} | RJ: {total_rj:,})")
        print(f"  Sampel     : {total_sample} kasus (RI: {sample_ri} | RJ: {sample_rj})")
        print(f"  KNAVP Alerts: {len(all_alerts)} total — Dominan: {dom_title} ({dom_count})")
        print(f"  Triase     : Onsite={len(onsite_cases)} | Sampling={len(sampling_cases)} | Monitor={len(monitor_cases)}")
        print(f"  Dual Coding: {len(mismatch_cases)} kasus mismatch ({mismatch_pct}%)")
        print(f"  Output     : {out_path}")

    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Agent 1 — Data Reviewer')
    parser.add_argument('--kode_rs', type=str, default='1275655', help='Kode RS')
    parser.add_argument('--all',     action='store_true', help='Proses semua RS')
    args = parser.parse_args()

    if args.all:
        for krs in COCHRAN_MASTER.keys():
            run(krs)
        print(f"\n[AGENT 1] Selesai. {len(COCHRAN_MASTER)} RS diproses.")
    else:
        result = run(args.kode_rs)
        if result:
            print(f"\n[AGENT 1] DONE. Metadata tersimpan.")
