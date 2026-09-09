"""Read every existing PDF, not just the DB, and reconcile visible report fields."""
import json
import hashlib
import re
import sys
import sqlite3
import random
import string
from pathlib import Path
from collections import Counter
import pypdfium2 as pdfium

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from modules.report_data import normalize_decision, UNKNOWN
OUT=BASE/'tmp/pdfs'
OUT.mkdir(parents=True,exist_ok=True)
snapshot=json.loads((BASE/'outputs/rekonsiliasi_20260831/snapshot.json').read_text(encoding='utf-8'))
cases={(str(c['kode_rs']),str(c['sep'])):c for c in snapshot['cases']}

def read_text(path):
    doc=pdfium.PdfDocument(path)
    texts=[]
    for i in range(len(doc)):
        page=doc[i]
        textpage=page.get_textpage()
        texts.append(textpage.get_text_bounded())
        textpage.close();page.close()
    pages=len(doc);doc.close()
    return '\n'.join(texts),pages

def extract(text):
    t=re.sub(r'\s+',' ',text)
    def match(pattern):
        found=list(re.finditer(pattern,t,re.I))
        return found[-1].group(1).strip() if found else None
    return dict(sep=match(r'Nomor SEP\s+([A-Za-z0-9]+)'),kode_rs=match(r'Kode FPKTL\s+(\d+)'),
        decision=match(r'Keputusan Reviewer\s+((?:(?!Keputusan Reviewer).)+?)\s+Tingkat Keyakinan'),
        score=match(r'Total Skor KNAVP:\s*([\d.]+)'),
        risk=match(r'Tingkat Risiko:\s*(Rendah|Sedang|Tinggi)\b'),
        dc=match(r'Perbedaan Dual Coding:\s*(\d+)'),
        patient_name=match(r'Nama Peserta\s+(.+?)\s+Tanggal Lahir'),
        claim=match(r'Nomor Klaim\s+(\d+)'))

def main():
    stats=Counter();issues=[];records=[];seen=Counter();transitions=Counter()
    files=sorted((BASE/'exports/kkr_forms_pdf_only').rglob('*.pdf'))
    conn=sqlite3.connect((BASE/'data.db').as_uri()+'?mode=ro',uri=True)
    source_names={(str(a),str(b)):str(c or '').strip() for a,b,c in conn.execute('SELECT kode_rs, sep, Nama_Pasien FROM individual_data')}
    conn.close()
    for i,path in enumerate(files,1):
        text,pages=read_text(path);fields=extract(text)
        key=(fields['kode_rs'],fields['sep']);seen[key]+=1
        c=cases.get(key)
        row=dict(path=str(path.relative_to(BASE)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),pages=pages,**fields)
        errors=[]
        if not c:
            errors.append('identity_not_matched')
        else:
            rng=random.Random(int(hashlib.md5(str(c['sep']).encode()).hexdigest(),16))
            fake_claim=''.join(rng.choices(string.digits,k=12))
            if fields['claim']==fake_claim:stats['claim_matches_fabricated_generator']+=1
            if fields['patient_name']!=source_names.get(key):stats['patient_name_differs_from_source']+=1
            decision=normalize_decision(fields['decision'])
            transitions[(fields['decision'],c['rekomendasi_laporan'])]+=1
            if decision!=c['rekomendasi_laporan']:errors.append('recommendation_mismatch_or_absent')
            if fields['decision']!=c['keputusan_reviewer_asli']:errors.append('reviewer_original_mismatch')
            for field,expected in [('score',c['knavp_skor']),('dc',c['jumlah_beda_dual_coding'])]:
                if fields[field] is None:errors.append(field+'_missing')
                elif float(fields[field])!=expected:errors.append(field+'_mismatch')
            if fields['risk'] is None:errors.append('risk_missing')
            elif fields['risk'].lower()!=c['tingkat_risiko'].lower():errors.append('risk_mismatch')
            row['expected_recommendation']=c['rekomendasi_laporan']
        stats.update(errors)
        row['issues']=errors;records.append(row)
        if errors:issues.append(row)
        stats['pdf_count']+=1;stats['page_count']+=pages
        if i%500==0:print('EXTRACTED',i,'/',len(files),flush=True)
    stats['matched_case_keys']=sum(key in cases for key in seen)
    stats['missing_pdf_cases']=len(set(cases)-set(seen))
    stats['duplicate_case_keys']=sum(count>1 for count in seen.values())
    stats['files_with_issues']=len(issues)
    result=dict(summary=dict(stats),transitions=[dict(pdf=a,recap=b,count=n) for (a,b),n in transitions.items()],records=records)
    (OUT/'original_pdf_audit.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2,ensure_ascii=True))

if __name__=='__main__':main()
