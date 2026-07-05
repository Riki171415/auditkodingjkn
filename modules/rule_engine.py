"""
Rule Engine Module
Implements Rule-Based Coding Validation based on Ministry of Health guidelines
"""
import json
import os
import re

RULES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rules', 'audit_rules.json')

_rules = None


def load_rules():
    global _rules
    if _rules is None:
        with open(RULES_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _rules = data['rules']
    return _rules


def parse_codes(code_str):
    """Parse semicolon-separated code list"""
    if not code_str or str(code_str).strip() == '' or str(code_str) == 'nan':
        return []
    return [c.strip().upper() for c in str(code_str).split(';') if c.strip()]


def code_matches(code, patterns):
    """Check if a code matches any pattern (prefix match)"""
    code = code.upper().strip()
    for pattern in patterns:
        pattern = pattern.upper().strip()
        if code == pattern:
            return True
        if code.startswith(pattern):
            return True
    return False


def code_in_list(code, code_list):
    """Exact or prefix match against a list"""
    return code_matches(code, code_list)


def has_any_code(codes, patterns):
    """Check if any code in list matches any pattern"""
    for code in codes:
        if code_matches(code, patterns):
            return True
    return False


def get_matching_codes(codes, patterns):
    """Get all matching codes"""
    return [c for c in codes if code_matches(c, patterns)]


def evaluate_rule(rule, diag_codes, proc_codes, case_data=None):
    """
    Evaluate a single rule against diagnosis and procedure codes.
    Returns (triggered: bool, evidence: str)
    """
    cond = rule['condition']
    cond_type = cond['type']
    
    try:
        if cond_type == 'diag_combination':
            # Both diag_a AND diag_b present in diag_codes
            has_a = has_any_code(diag_codes, cond['diag_a'])
            has_b = has_any_code(diag_codes, cond['diag_b'])
            if has_a and has_b:
                matched_a = get_matching_codes(diag_codes, cond['diag_a'])
                matched_b = get_matching_codes(diag_codes, cond['diag_b'])
                return True, f"Ditemukan: {', '.join(matched_a)} + {', '.join(matched_b)}"
                
        elif cond_type == 'diag_triple':
            # All three diag groups present
            has_a = has_any_code(diag_codes, cond['diag_a'])
            has_b = has_any_code(diag_codes, cond['diag_b'])
            has_c = has_any_code(diag_codes, cond['diag_c'])
            if has_a and has_b and has_c:
                return True, f"Ditemukan kombinasi tiga kondisi: {'+'.join(cond['diag_a'])}, {'+'.join(cond['diag_b'])}, {'+'.join(cond['diag_c'])}"
                
        elif cond_type == 'diag_combination_prefix':
            # diag_a present AND any code with prefix in diag_b_prefix
            has_a = has_any_code(diag_codes, cond['diag_a'])
            has_b = any(any(c.startswith(p) for p in cond['diag_b_prefix']) for c in diag_codes)
            if has_a and has_b:
                matched_a = get_matching_codes(diag_codes, cond['diag_a'])
                matched_b = [c for c in diag_codes if any(c.startswith(p) for p in cond['diag_b_prefix'])]
                return True, f"Ditemukan: {', '.join(matched_a)} + {', '.join(matched_b[:3])}"
                
        elif cond_type == 'diag_without_proc':
            # Diagnosis present but required procedure absent
            has_diag = has_any_code(diag_codes, cond['diag'])
            has_proc = has_any_code(proc_codes, cond['required_proc_prefix'])
            if has_diag and not has_proc:
                matched_diag = get_matching_codes(diag_codes, cond['diag'])
                return True, f"Diagnosis {', '.join(matched_diag)} tanpa prosedur yang sesuai"
                
        elif cond_type == 'proc_without_diag':
            # Procedure present but required diagnosis absent
            has_proc = has_any_code(proc_codes, cond['proc'])
            has_diag = has_any_code(diag_codes, cond['required_diag'])
            if has_proc and not has_diag:
                matched_proc = get_matching_codes(proc_codes, cond['proc'])
                return True, f"Prosedur {', '.join(matched_proc)} tanpa diagnosis pendukung"
                
        elif cond_type == 'proc_without_diag_prefix':
            # Procedure present but required diagnosis (by prefix) absent
            has_proc = has_any_code(proc_codes, cond.get('proc_prefix', []))
            has_diag = any(any(d.startswith(p) for p in cond.get('required_diag_prefix', [])) for d in diag_codes)
            if has_proc and not has_diag:
                matched_proc = [p for p in proc_codes if any(p.startswith(pf) for pf in cond.get('proc_prefix', []))]
                return True, f"Prosedur {', '.join(matched_proc[:3])} tanpa diagnosis pendukung"
                
        elif cond_type == 'diag_with_proc':
            # Both diagnosis AND specific procedure present (unbundling)
            has_diag = has_any_code(diag_codes, cond['diag'])
            has_proc = has_any_code(proc_codes, cond['proc'])
            if has_diag and has_proc:
                matched_proc = get_matching_codes(proc_codes, cond['proc'])
                return True, f"Prosedur {', '.join(matched_proc)} sudah termasuk dalam paket tindakan"
                
        elif cond_type == 'proc_combination':
            # Two procedure groups present together (unbundling)
            has_proc_a = has_any_code(proc_codes, cond['proc_a'])
            has_proc_b = any(any(p.startswith(pf) for pf in cond['proc_b_prefix']) for p in proc_codes)
            if has_proc_a and has_proc_b:
                return True, f"Terdapat prosedur yang terindikasi unbundling"
                
        elif cond_type == 'unbundling_check':
            has_proc_a = has_any_code(proc_codes, cond['proc_a'])
            has_proc_b = any(any(p.startswith(pf) for pf in cond['proc_b_prefix']) for p in proc_codes)
            if has_proc_a and has_proc_b:
                return True, f"Debridement dan prosedur utama dikode terpisah"
                
        elif cond_type == 'diag_without_supporting_diag':
            # Main diag present but no supporting diag
            has_diag = has_any_code(diag_codes, cond['diag'])
            has_support = any(any(d.startswith(p) for p in cond['supporting_diag_prefix']) 
                            for d in diag_codes if not any(d.startswith(s) for s in ['A41']))
            if has_diag and not has_support:
                return True, f"Sepsis ditemukan tanpa fokus infeksi yang jelas"
                
        elif cond_type == 'diag_check':
            # Simply check if specific diagnosis exists (high-risk codes)
            has_diag = has_any_code(diag_codes, cond['diag'])
            if has_diag:
                matched = get_matching_codes(diag_codes, cond['diag'])
                return True, f"Ditemukan kode risiko tinggi: {', '.join(matched)}"
                
        elif cond_type == 'diag_check_high_rw':
            # Check diagnosis AND high relative weight
            has_diag = has_any_code(diag_codes, cond['diag'])
            if has_diag and case_data:
                rw = float(case_data.get('rw', 0) or 0)
                if rw >= cond.get('min_rw_threshold', 5.0):
                    return True, f"Ditemukan kode risiko tinggi dengan RW={rw:.2f}"
                    
        elif cond_type == 'manifestation_without_underlying':
            # Manifestation code without underlying cause
            manifestations_found = [d for d in diag_codes if d in cond['manifestation_codes']]
            if manifestations_found:
                return True, f"Kode manifestasi ({', '.join(manifestations_found)}) tanpa Underlying Cause"
                
        elif cond_type == 'los_outlier':
            # LOS is unusually high
            if case_data:
                alos = float(case_data.get('alos', 0) or 0)
                cmi_val = float(case_data.get('cmi', 1) or 1)
                if alos > 0 and cmi_val > 0 and alos > (cmi_val * cond['los_threshold_multiplier'] * 5):
                    return True, f"LOS={alos} hari terindikasi tidak wajar"
                    
        elif cond_type == 'dual_coding_discrepancy':
            # Check for missing secondary code requirement
            has_primary = has_any_code(diag_codes, cond['primary_diag'])
            has_secondary = has_any_code(diag_codes, cond['secondary_diag_prefix'])
            if has_primary and not has_secondary:
                return True, "Dual coding diperlukan namun tidak ditemukan kode pendukung"

    except Exception as e:
        pass
    
    return False, ""


def validate_case(case_data):
    """
    Run all rules against a single case.
    Returns list of triggered rules with details, including bobot and kelompok_rule.
    """
    rules = load_rules()
    
    diaglist = case_data.get('diaglist', '') or ''
    proclist = case_data.get('proclist', '') or ''
    
    diag_codes = parse_codes(diaglist)
    proc_codes = parse_codes(proclist)
    
    triggered = []
    
    for rule in rules:
        triggered_flag, evidence = evaluate_rule(rule, diag_codes, proc_codes, case_data)
        if triggered_flag:
            severity = rule.get('severity', 'Low')
            bobot = rule.get('bobot', _get_default_bobot(severity))
            triggered.append({
                'rule_id': rule['rule_id'],
                'nama_aturan': rule['nama_aturan'],
                'kategori': rule['kategori'],
                'kelompok_rule': rule.get('kelompok_rule', _get_kelompok_label(rule.get('kategori', ''))),
                'severity': severity,
                'bobot': bobot,
                'ptd': rule['ptd'],
                'pesan_validasi': rule['pesan_validasi'],
                'rekomendasi_reviewer': rule['rekomendasi_reviewer'],
                'evidence': evidence
            })
    
    return triggered


def _get_default_bobot(severity):
    """Default bobot based on severity if not defined in rule JSON"""
    return {'High': 3, 'Medium': 2, 'Low': 1}.get(severity, 1)


def _get_kelompok_label(kategori):
    """Human-readable kelompok rule label"""
    labels = {
        'combination_code': 'Combination Code',
        'dagger_asterisk': 'Dagger & Asterisk',
        'includes_excludes': 'Includes/Excludes',
        'underlying_manifestation': 'Underlying & Manifestation',
        'procedure_validation': 'Procedure Validation',
        'unbundling': 'Unbundling',
        'dual_coding': 'Dual Coding',
        'medical_evidence': 'Medical Evidence',
        'administrative_validation': 'Administrative',
        'age_validation': 'Age Validation',
        'los_validation': 'LOS Validation',
    }
    return labels.get(kategori, kategori)


def get_validation_summary(triggered_rules):
    """Summarize triggered rules by category"""
    categories = {
        'combination_code': 'Combination Code',
        'dagger_asterisk': 'Dagger & Asterisk',
        'includes_excludes': 'Includes dan Excludes',
        'underlying_manifestation': 'Underlying Cause dan Manifestation',
        'procedure_validation': 'Procedure Validation',
        'unbundling': 'Unbundling dan Omit Code',
        'dual_coding': 'Dual Coding Discrepancy',
        'medical_evidence': 'Medical Evidence Validation',
        'administrative_validation': 'Administrative Validation',
        'age_validation': 'Age Validation',
        'los_validation': 'Length of Stay Validation'
    }
    
    summary = {cat: 0 for cat in categories}
    
    for rule in triggered_rules:
        cat = rule.get('kategori', '')
        if cat in summary:
            summary[cat] += 1
    
    return {
        categories.get(k, k): v 
        for k, v in summary.items() 
        if v > 0
    }


# ============================================================
# Dual Coding Discrepancy Checker
# (Dikloning dari SAK-iDRG analyze_new.py, diperluas)
# ============================================================

# Kode non-klinis / admin yang diabaikan dari perbandingan
DIAG_EXCLUSIONS = {'KG', 'HL', 'NL', 'KND', 'G89', 'U82', 'U83', 'U84'}
PROC_EXCLUSIONS = {'99.290'}


def _is_excluded(code, exclusion_set):
    """Check if a code should be excluded from comparison"""
    c = str(code).strip().upper()
    return any(c == e or c.startswith(e) for e in exclusion_set)


def check_code_match(ina_code, idrg_code):
    """
    Compare a single INA-CBG code vs iDRG code.
    Returns True (Sesuai) or False (Tidak Sesuai).

    Aturan matching (berurutan):
    1. Exact match          : 'A01.0'  vs 'A01.0'    -> Sesuai
    2. Prefix/spesifisitas  : '90.59'  vs '90.599'   -> Sesuai (one starts with other)
    3. iDRG Modifier (+X)   : '99.04'  vs '99.04+2'  -> Sesuai (strip '+...' dari iDRG)
    4. No match             : benar-benar beda        -> Tidak Sesuai
    """
    if not ina_code or not idrg_code:
        return False

    a = str(ina_code).strip().upper()
    b = str(idrg_code).strip().upper()

    # Rule 1: Exact match
    if a == b:
        return True

    # Rule 2: Prefix / specificity tolerance
    if a.startswith(b) or b.startswith(a):
        return True

    # Rule 3: iDRG modifier strip — e.g. '99.04+2' -> '99.04'
    b_base = b.split('+')[0].strip() if '+' in b else b
    a_base = a.split('+')[0].strip() if '+' in a else a
    if a_base == b_base:
        return True
    if a_base.startswith(b_base) or b_base.startswith(a_base):
        return True

    return False


def check_dual_coding_discrepancy(case_data):
    """
    Compare INA-CBG vs iDRG code lists row-by-row.
    Returns list of per-row comparison results for diagnosa & prosedur.

    Each row dict:
        {
          'no': int,
          'ina_code': str,
          'ina_desc': str,
          'idrg_code': str,
          'idrg_desc': str,
          'sesuai': bool,
          'keterangan': str   # 'Kode & Deskripsi sama' / 'Kode berbeda' / 'Hanya di INA-CBG' / 'Hanya di iDRG'
        }
    """
    from modules.data_loader import get_icd_dict
    icd_dict = get_icd_dict()

    def _get_desc(code):
        if not code:
            return ''
        c = str(code).strip().upper().split('+')[0]  # strip modifier for lookup
        while len(c) >= 3:
            if c in icd_dict:
                return icd_dict[c]
            c = c[:-1]
        return '-'

    def _parse(raw, exclusions):
        if not raw or str(raw).strip().lower() in ('', 'nan', 'none'):
            return []
        codes = [c.strip().upper() for c in str(raw).split(';') if c.strip()]
        return [c for c in codes if c not in ('-', 'NAN') and not _is_excluded(c, exclusions)]

    diag_ina = _parse(case_data.get('diaglist', ''), DIAG_EXCLUSIONS)
    diag_idrg = _parse(case_data.get('diaglist_idrg', case_data.get('diaglist', '')), DIAG_EXCLUSIONS)
    proc_ina = _parse(case_data.get('proclist', ''), PROC_EXCLUSIONS)
    proc_idrg = _parse(case_data.get('proclist_idrg', case_data.get('proclist', '')), PROC_EXCLUSIONS)

    def _build_rows(ina_list, idrg_list):
        rows = []
        matched_idrg_indices = set()
        
        # 1. Cari pasangan kode yang cocok (mengabaikan urutan)
        for ina_c in ina_list:
            match_found = False
            for j, idrg_c in enumerate(idrg_list):
                if j not in matched_idrg_indices and check_code_match(ina_c, idrg_c):
                    matched_idrg_indices.add(j)
                    rows.append({
                        'ina_code': ina_c,
                        'idrg_code': idrg_c,
                        'sesuai': True,
                        'keterangan': 'Kode & Deskripsi sama'
                    })
                    match_found = True
                    break
            
            if not match_found:
                rows.append({
                    'ina_code': ina_c,
                    'idrg_code': '',
                    'sesuai': False,
                    'keterangan': 'Hanya di INA-CBG'
                })
        
        # 2. Tambahkan sisa kode iDRG yang tidak punya pasangan di INA-CBG
        for j, idrg_c in enumerate(idrg_list):
            if j not in matched_idrg_indices:
                rows.append({
                    'ina_code': '',
                    'idrg_code': idrg_c,
                    'sesuai': False,
                    'keterangan': 'Hanya di iDRG'
                })
        
        # 3. Beri nomor dan lengkapi deskripsi
        for i, row in enumerate(rows):
            row['no'] = i + 1
            row['ina_desc'] = _get_desc(row['ina_code']) if row['ina_code'] else '-'
            row['idrg_desc'] = _get_desc(row['idrg_code']) if row['idrg_code'] else '-'

        return rows

    diag_rows = _build_rows(diag_ina, diag_idrg)
    proc_rows = _build_rows(proc_ina, proc_idrg)

    jumlah_beda_diag = sum(1 for r in diag_rows if not r['sesuai'])
    jumlah_beda_proc = sum(1 for r in proc_rows if not r['sesuai'])

    return {
        'diag_rows': diag_rows,
        'proc_rows': proc_rows,
        'jumlah_beda_diag': jumlah_beda_diag,
        'jumlah_beda_proc': jumlah_beda_proc,
        'jumlah_beda_total': jumlah_beda_diag + jumlah_beda_proc,
    }


# ============================================================
# KNAVP Score & Recommendation
# ============================================================

def calculate_knavp_score(triggered_rules):
    """Sum of bobot for all triggered rules = Total Skor KNAVP"""
    return sum(r.get('bobot', _get_default_bobot(r.get('severity', 'Low'))) for r in triggered_rules)


def determine_recommendation_knavp(total_skor, jumlah_beda_dual_coding=0):
    """
    Determine system recommendation based on KNAVP total score.
    Threshold (from gauge in form image):
      0        -> Tidak perlu tindak lanjut
      1-3      -> Rendah  -> Monitoring
      4-7      -> Sedang  -> Audit Sampling
      >= 8     -> Tinggi  -> Direkomendasikan On-Site Audit
    Dual coding differences also influence: each difference adds weight.
    """
    effective_skor = total_skor + (jumlah_beda_dual_coding * 1)  # each dual coding diff = +1

    if effective_skor == 0:
        tingkat = 'Rendah'
        keputusan = 'Tidak perlu tindak lanjut'
    elif effective_skor <= 3:
        tingkat = 'Rendah'
        keputusan = 'Monitoring (Tidak perlu tindak lanjut)'
    elif effective_skor <= 7:
        tingkat = 'Sedang'
        keputusan = 'Audit Sampling'
    else:
        tingkat = 'Tinggi'
        keputusan = 'Direkomendasikan On-Site Audit'

    return {
        'total_skor': total_skor,
        'effective_skor': effective_skor,
        'tingkat_risiko': tingkat,
        'keputusan_sistem': keputusan,
    }


def validate_batch_by_rs(df_rs):
    """Validate all cases for a hospital and return summary"""
    results = []
    for _, row in df_rs.iterrows():
        case = row.to_dict()
        triggered = validate_case(case)
        
        results.append({
            'sep': case.get('sep', ''),
            'inacbg': case.get('inacbg', ''),
            'deskripsi_inacbg': case.get('deskripsi_inacbg', ''),
            'triggered_count': len(triggered),
            'has_high': any(r['severity'] == 'High' for r in triggered),
            'has_medium': any(r['severity'] == 'Medium' for r in triggered),
            'triggered_rules': triggered,
            'rekomendasi': determine_recommendation(triggered),
            'tarif_inacbg': case.get('tarif_inacbg', 0),
            'tarif_rs': case.get('tarif_rs', 0),
            'alos': case.get('alos', 0),
            'cmi': case.get('cmi', 0)
        })
    
    return results
