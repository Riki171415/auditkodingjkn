"""Generate KKR PDFs without re-running audit rules, using the Excel snapshot."""
import argparse
from pathlib import Path
import sys
import json
import sqlite3
import hashlib

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from modules.report_pdf import export_pdf

def load_demographics():
    conn=sqlite3.connect((BASE/'data.db').as_uri()+'?mode=ro',uri=True);conn.row_factory=sqlite3.Row
    data={}
    for row in conn.execute('SELECT kode_rs,sep,Nama_Pasien,SEX,Birth_date,admission_date,discharge_date,kelas_rawat FROM individual_data'):
        item=dict(row);key=(str(item['kode_rs']),str(item['sep']))
        if key in data:raise ValueError('Duplicate source patient key')
        data[key]=item
    conn.close();return data

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--sample',action='store_true')
    parser.add_argument('--source',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    SOURCE = Path(args.source).resolve()
    OUT = Path(args.output).resolve()
    snapshot=json.loads((SOURCE/'snapshot.json').read_text(encoding='utf-8'))
    demographics=load_demographics();cases=snapshot['cases']
    if args.sample:
        chosen=[]
        for decision in sorted({c['rekomendasi_laporan'] for c in cases}):
            chosen.append(max((c for c in cases if c['rekomendasi_laporan']==decision),key=lambda c:len(c.get('alasan_keputusan',''))+len(c['triggered_rules'])*100))
        chosen.append(max(cases,key=lambda c:len(str(c.get('diaglist','')))+len(str(c.get('proclist','')))))
        chosen.append(next(c for c in cases if c['sumber_rekomendasi']=='keputusan reviewer eksplisit'))
        cases=list({(c['kode_rs'],c['sep']):c for c in chosen}.values())
    import re
    def rs_slug(nama_rs, max_len=40):
        slug = re.sub(r'[^A-Z0-9]+', '_', str(nama_rs).upper().strip())
        return slug.strip('_')[:max_len].rstrip('_')

    manifest=[]
    for i,c in enumerate(cases,1):
        kode_rs = str(c['kode_rs'])
        nama_rs = c.get('nama_rs', 'RS')
        # Format "Kode RS - Nama RS" as requested
        safe_nama_rs = re.sub(r'[\\/*?:"<>|]', '', str(nama_rs).upper().strip())
        folder_name = f"{kode_rs} - {safe_nama_rs}"
        
        key=(kode_rs, str(c['sep']))
        path=OUT/folder_name/f'KKR-DR01_{key[1]}.pdf'
        path.parent.mkdir(parents=True,exist_ok=True)
        
        data=export_pdf(c,snapshot['snapshot_id'],demographics.get(key))
        path.write_bytes(data)
        manifest.append(dict(kode_rs=key[0],sep=key[1],path=str(path.relative_to(OUT)),sha256=hashlib.sha256(data).hexdigest()))
        if i%500==0:print('PDF CREATED',i,'/',len(cases),flush=True)
    (OUT/('sample_manifest.json' if args.sample else 'manifest_pdf.json')).write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('COMPLETED',len(cases),'PDFs',flush=True)

if __name__=='__main__':main()
