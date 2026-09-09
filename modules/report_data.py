"""One reporting contract; never re-triage or overwrite a saved review."""
from collections import Counter, defaultdict
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP

ONSITE = 'Direkomendasikan On-Site Audit'
SAMPLING = 'Audit Sampling (Klarifikasi)'
MONITORING = 'Perlu Monitoring'
UNKNOWN = 'Data tidak cukup untuk dinilai'
DECISIONS = (ONSITE, SAMPLING, MONITORING, UNKNOWN)
VERSION = 'saved-review-v1'

def normalize_decision(value):
    text = str(value or '').replace('*', '').strip().lower()
    if 'on-site' in text or 'onsite' in text:
        return ONSITE
    if 'sampling' in text or 'klarifikasi' in text:
        return SAMPLING
    if 'monitor' in text or text in ('tidak perlu tindak lanjut', 'tidak diperlukan tindak lanjut', 'lolos/monitoring', 'perlu monitoring'):
        return MONITORING
    return UNKNOWN

def normalize_case(row):
    case = dict(row)
    raw = case.get('tindakan_reviewer')
    form = json.loads(raw or '{}') if isinstance(raw, str) or raw is None else raw
    if not isinstance(form, dict):
        raise ValueError('Data form review bukan objek JSON')
    rules = case.get('triggered_rules')
    if rules is None:
        rules = json.loads(case.get('triggered_rules_json') or '[]')
    if not isinstance(rules, list):
        raise ValueError('Data aturan audit bukan daftar')
    saved_system = form.get('keputusan_sistem', case.get('keputusan_sistem', ''))
    decision = normalize_decision(saved_system)
    origin = 'keputusan_sistem tersimpan'
    if decision == UNKNOWN:
        # Only explicit follow-up labels can fill a missing system recommendation.
        # A validity verdict (e.g. Sesuai/Fraud) must not be invented into triage.
        decision = normalize_decision(form.get('keputusan', case.get('keputusan', '')))
        origin = 'keputusan reviewer eksplisit' if decision != UNKNOWN else 'belum tersedia'
    score = float(form.get('knavp_skor', case.get('knavp_skor', 0)) or 0)
    dc = int(form.get('jumlah_beda_dual_coding', case.get('jumlah_beda_dual_coding', 0)) or 0)
    if dc < 0 or score < 0:
        raise ValueError('Skor/jumlah perbedaan tidak boleh negatif')
    case.update(knavp_skor=score, tingkat_risiko=form.get('tingkat_risiko', case.get('tingkat_risiko', '')) or 'Belum diisi',
                jumlah_beda_dual_coding=dc, triggered_rules=rules,
                triggered_rules_json=json.dumps(rules, ensure_ascii=False),
                rekomendasi_laporan=decision, keputusan_sistem=saved_system,
                keputusan_reviewer_asli=form.get('keputusan', case.get('keputusan', '')) or '',
                sumber_rekomendasi=origin,
                tanggal_review=form.get('tanggal_review') or case.get('updated_at') or '',
                alasan_keputusan=form.get('alasan_keputusan') or form.get('analisis_reviewer') or '')
    return case

def summarize(cases):
    counts = Counter(c['rekomendasi_laporan'] for c in cases)
    severity = Counter(str(r.get('severity', 'Low')).title() for c in cases for r in c['triggered_rules'])
    return dict(total=len(cases), onsite=counts[ONSITE], sampling=counts[SAMPLING],
                monitoring=counts[MONITORING], unknown=counts[UNKNOWN],
                score_sum=sum(c['knavp_skor'] for c in cases),
                avg_score=float((sum(Decimal(str(c['knavp_skor'])) for c in cases)/len(cases)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) if cases else 0,
                dc_cases=sum(c['jumlah_beda_dual_coding'] > 0 for c in cases),
                dc_total=sum(c['jumlah_beda_dual_coding'] for c in cases),
                alerts=sum(len(c['triggered_rules']) for c in cases),
                cases_with_alerts=sum(bool(c['triggered_rules']) for c in cases), severity=dict(severity))

def build_snapshot(rows):
    cases = sorted((normalize_case(r) for r in rows), key=lambda c: (str(c['kode_rs']), str(c['sep'])))
    keys = [(str(c['kode_rs']), str(c['sep'])) for c in cases]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplikasi pasangan Kode RS/SEP; ekspor dihentikan')
    if any(not c.get('nama_rs') for c in cases):
        raise ValueError('Ada review tanpa pasangan data RS; ekspor dihentikan')
    grouped = defaultdict(list)
    for case in cases:
        grouped[str(case['kode_rs'])].append(case)
    hospitals = [dict(kode_rs=code, nama_rs=group[0]['nama_rs'], summary=summarize(group), cases=group) for code, group in grouped.items()]
    digest = hashlib.sha256(json.dumps(cases, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return dict(version=VERSION, snapshot_id=digest, summary=summarize(cases), hospitals=hospitals, cases=cases)

def load_snapshot():
    from modules.db_manager import get_recap_desk_review
    return build_snapshot(get_recap_desk_review())
