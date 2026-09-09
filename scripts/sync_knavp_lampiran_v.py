"""Extract the authoritative 44-row catalogue; do not infer clinical criteria."""
from pathlib import Path
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import json,hashlib,shutil

BASE=Path(__file__).resolve().parents[1]
SOURCE=BASE.parent/'V1.DRAFT KEPUTUSAN SEKRETARIS JENDERAL KEMENTERIAN KESEHATAN.docx'
VERSION='knavp-lampiran-v-20260907'

def extract_catalog():
    doc=Document(SOURCE); active=False; chapter=''; rows=[]
    for element in doc.element.body:
        if element.tag.endswith('}p'):
            text=Paragraph(element,doc).text.strip()
            if text=='LAMPIRAN V':active=True
            elif active and text.startswith('LAMPIRAN VI'):break
            elif active and text.startswith('BAB '):chapter=text
        elif active and element.tag.endswith('}tbl'):
            for row in Table(element,doc).rows:
                cells=[c.text.strip() for c in row.cells]
                if len(cells)==7 and cells[0].startswith('AUDIT-COD-'):
                    rows.append(dict(zip(['rule_id','nama_aturan','ptd','severity','kondisi_validasi','pesan_validasi','rekomendasi_reviewer'],cells),bab=chapter))
    assert len(rows)==44 and len({r['rule_id'] for r in rows})==44
    return rows

def present(patterns):return {'op':'has_any_diag','patterns':patterns}
def both(a,b):return {'op':'all','items':[present(a),present(b)]}
AUTO={
 '01':both(['A01.0'],['O98','O98.8']),
 '03':both(['N20','N21','N22','N23'],['N39.0']),
 '05':both(['K80'],['K83.0','K83.1']),
 '08':both(['E10','E11','E14'],['R02','L97']),
 '16':both(['I10'],['I50']), '17':both(['I10'],['N18']),
 '18':{'op':'all','items':[present(['I10']),present(['N18']),present(['I50'])]},
 '19':both(['I50'],['J81']), '20':both(['J44.9'],['J18']),
 '33':both(['D50'],['O99.0']), '44':both(['A15','A16'],['R04.2']),
 '48':both(['I60','I61','I62','I63','I64'],['G81']),
 '09':both(['E10','E11','E14'],['G63.2']), '22':both(['A01.0'],['J18']),
 '52':both(['B05'],['J18']), '21':both(['A01.0'],['A09']),
 '23':both(['O41.0'],['O42']), '24':both(['R57.1'],['S','T']),
 '41':both(['S06'],['G93.5']), '50':both(['A15.2','A16.2'],['J18']),
 '51':both(['A90'],['A91']), '58':both(['M84.0'],['S']),
}
NEEDS={
 '10':'Konfirmasi B20 dan lebih dari satu infeksi oportunistik. Lampiran tidak menetapkan daftar kode infeksi oportunistik.',
 '40':'Verifikasi kode manifestation dan pasangan underlying cause yang sesuai; daftar pasangan tidak ditentukan dalam lampiran.',
 '59':'Verifikasi ketidaksesuaian pasangan underlying cause dan manifestation berdasarkan bukti reviewer.',
 '07':'Verifikasi diagnosis O82 dan ketiadaan prosedur Sectio Caesarea; lampiran tidak merinci kode prosedurnya.',
 '37':'Verifikasi adanya hemodialisis dan ketiadaan diagnosis N17, N18 atau N19.',
 '39':'Verifikasi penggunaan ventilator mekanik dan ketiadaan diagnosis J96.',
 '62':'Verifikasi adanya appendektomi dan ketiadaan diagnosis K35, K36 atau K37.',
 '67':'Verifikasi kateterisasi jantung dan diagnosis penyakit jantung yang mendukung.',
 '68':'Verifikasi kemoterapi dan ketiadaan diagnosis C00 sampai C97 atau D00 sampai D09.',
 '06':'Verifikasi persalinan normal O80 disertai episiotomi.',
 '25':'Verifikasi debridement dilaporkan bersama operasi yang telah mencakup tindakan tersebut.',
 '26':'Verifikasi eksplorasi dilaporkan bersama operasi definitif yang mencakupnya.',
 '34':'Verifikasi transfusi darah dilaporkan bersama operasi yang telah mencakup pelayanan tersebut.',
 '46':'Verifikasi histopatologi dilaporkan bersama operasi pengambilan spesimen.',
 '66':'Verifikasi kateter urin dilaporkan bersama tindakan operasi.',
 '60':'Verifikasi diagnosis sepsis serta fokus infeksi atau bukti medis pendukung.',
 '64':'Verifikasi diagnosis J96 dan ketiadaan bukti klinis pendukung; tidak menggunakan ambang RW.',
 '65':'Verifikasi diagnosis N17 dan ketiadaan bukti klinis; keberadaan N17 saja bukan bukti ketiadaan dukungan.',
 '63':'Verifikasi diagnosis, jenis kelamin dan kesesuaiannya; pemetaan diagnosis ke jenis kelamin tidak dirinci.',
 '70':'Verifikasi diagnosis dan usia pasien; batas umur tidak dirinci dalam lampiran.',
 '69':'Verifikasi karakteristik kelompok umur dan diagnosis; batas umur tidak dirinci dalam lampiran.',
 '71':'Verifikasi LOS terhadap karakteristik diagnosis dan tindakan; lampiran tidak menetapkan rumus atau ambang numerik.',
}
CATEGORIES=dict(zip('ABCDEFGHI',['combination_code','dagger_asterisk','includes_excludes','underlying_manifestation','procedure_validation','unbundling','medical_evidence','administrative_validation','age_los_validation']))

def build_catalog():
    result=[]
    for source in extract_catalog():
        r=dict(source);short=r['rule_id'].split('-')[-1]
        r.update(kategori=CATEGORIES[r['bab'][4]],kelompok_rule=r['bab'].split('. ',1)[1],
                 sumber_referensi=f'{SOURCE.name}, Lampiran V, {r["bab"]}, {r["rule_id"]}',
                 catalog_version=VERSION)
        if short in AUTO:
            r['condition']={'type':'catalog_expression','expression':AUTO[short]}
            r['metode_evaluasi']='Pencocokan kode diagnosis sesuai kondisi lampiran'
        else:
            r['condition']={'type':'reviewer_evidence','assessment_key':r['rule_id'],'required_fields':['condition_met','evidence','reviewer']}
            r['metode_evaluasi']=NEEDS[short]
        result.append(r)
    return {'catalog_version':VERSION,'source_document':SOURCE.name,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'source_section':'Lampiran V','rule_count':44,
            'scoring':{'defined_by_source':False,'weights':None,'thresholds':None,'dual_coding_additive_weight':None,
                       'decision':'Memerlukan penilaian reviewer'},
            'evaluation_contract':{'statuses':['triggered','not_triggered','needs_review','not_applicable'],
                                   'ptd':'1 atau 2 dari data sumber; jika hilang atau tidak valid, perlu verifikasi',
                                   'missing_input':'needs_review, bukan not_triggered',
                                   'code_matching':'prefix pada kode diagnosis yang telah dinormalisasi; seluruh daftar adalah OR, semua kelompok adalah AND',
                                   'reviewer_evidence':'Objek rule_assessments[rule_id] dengan condition_met boolean, evidence dan reviewer tidak kosong'},
            'rules':result}

if __name__=='__main__':
    target=BASE/'rules/audit_rules.json';archive=BASE/'.report_work/knavp_before_lampiran_v'
    archive.mkdir(exist_ok=True)
    for relative in ['rules/audit_rules.json','modules/rule_engine.py']:
        dest=archive/Path(relative).name
        if not dest.exists():shutil.copy2(BASE/relative,dest)
    payload=build_catalog()
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Synchronized',len(payload['rules']),'rules')
