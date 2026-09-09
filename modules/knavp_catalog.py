"""Execution contract for Lampiran V. Missing evidence is never a clean result."""
import re

VERSION='knavp-lampiran-v-20260907'
NEEDS_REVIEW='needs_review'

def normalize_codes(value):
    if value is None:return None
    if not isinstance(value,str):return None
    if value.strip().lower() in ('','nan','none','null','-'):return None
    codes=[x.strip().upper() for x in value.split(';') if x.strip()]
    # ICD diagnosis code, optionally followed by a dagger/asterisk marker.
    if not codes or any(not re.fullmatch(r'[A-Z][0-9]{2}(?:\.[A-Z0-9]+)?[†*]?',x) for x in codes):return None
    return [x.rstrip('†*') for x in codes]

def expression_matches(expression,codes):
    op=expression.get('op')
    if op=='has_any_diag':
        patterns=expression['patterns']
        if not patterns:raise ValueError('Empty diagnosis pattern list')
        return any(code.startswith(pattern) for code in codes for pattern in patterns)
    if op=='all':
        if not expression['items']:raise ValueError('Empty expression')
        return all(expression_matches(item,codes) for item in expression['items'])
    raise ValueError(f'Unsupported catalogue expression: {op}')

def assess_rule(rule,case):
    result={key:rule[key] for key in ['rule_id','nama_aturan','kategori','kelompok_rule','ptd','severity','pesan_validasi','rekomendasi_reviewer','sumber_referensi','catalog_version']}
    result['requires_evidence'] = rule['condition']['type'] == 'reviewer_evidence'
    result['kondisi_validasi'] = rule['kondisi_validasi']
    def finish(status,evidence):
        return dict(result,status=status,evidence=evidence)
    ptd=str(case.get('ptd','')).strip()
    if ptd not in ('1','2'):
        return finish(NEEDS_REVIEW,'PTD tidak tersedia atau tidak valid; lingkup pelayanan belum dapat ditentukan.')
    if ptd not in rule['ptd'].split('/'):
        return finish('not_applicable','PTD kasus berada di luar lingkup aturan.')
    condition=rule['condition']
    if condition['type']=='catalog_expression':
        codes=normalize_codes(case.get('diaglist'))
        if codes is None:return finish(NEEDS_REVIEW,'Daftar diagnosis kosong, tidak tersedia atau format kodenya tidak valid.')
        yes=expression_matches(condition['expression'],codes)
        return finish('triggered' if yes else 'not_triggered',
                      'Kondisi kode terpenuhi: '+rule['kondisi_validasi'] if yes else 'Kondisi kode dalam lampiran tidak ditemukan pada daftar diagnosis.')
    if condition['type']=='reviewer_evidence':
        assessments=case.get('rule_assessments')
        entry=assessments.get(rule['rule_id']) if isinstance(assessments,dict) else None
        if not isinstance(entry,dict) or type(entry.get('condition_met')) is not bool:
            return finish(NEEDS_REVIEW,rule['metode_evaluasi'])
        if any(not isinstance(entry.get(k),str) or not entry[k].strip() for k in ('evidence','reviewer')):
            return finish(NEEDS_REVIEW,'Penilaian memerlukan bukti dan identitas reviewer yang tidak kosong.')
        return finish('triggered' if entry['condition_met'] else 'not_triggered',
                      f"Penilaian {entry['reviewer'].strip()}: {entry['evidence'].strip()}")
    raise ValueError(f"Unsupported catalogue condition: {condition['type']}")

def assess_catalog(rules,case):
    return [assess_rule(rule,case) for rule in rules]
