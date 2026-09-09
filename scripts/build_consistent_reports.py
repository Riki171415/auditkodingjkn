"""Export one immutable reporting snapshot and its Word reports, without AI calls."""
import argparse
import json
import re
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from modules.report_data import load_snapshot


def rs_slug(nama_rs, max_len=40):
    """Convert RS name to a safe uppercase filename fragment (no dots/spaces/special chars)."""
    slug = re.sub(r'[^A-Z0-9]+', '_', str(nama_rs).upper().strip())
    return slug.strip('_')[:max_len].rstrip('_')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    parser.add_argument('--word',action='store_true')
    args=parser.parse_args()
    out=Path(args.output).resolve()
    out.mkdir(parents=True,exist_ok=True)
    snapshot_path=out/'snapshot.json'
    if args.word:
        snapshot=json.loads(snapshot_path.read_text(encoding='utf-8'))
        from modules.report_word import write_report
        from modules.db_manager import save_generated_report
        for h in snapshot['hospitals']:
            # Stable filename is part of the report contract.  The verifier and
            # final package must inspect the exact file overwritten here.
            slug = rs_slug(h['nama_rs'])
            fname = f'LHR_{h["kode_rs"]}_{slug}.docx'
            write_report(h['cases'], out/'word_per_rs'/fname, snapshot['snapshot_id'])
            
            # Save to database
            rel_path = f"outputs/{out.name}/word_per_rs/{fname}"
            save_generated_report('LHA_WORD', fname, rel_path, h['kode_rs'])
            print('WORD', h['kode_rs'], fname, flush=True)
            
        write_report(snapshot['cases'],out/'Laporan_Akhir_Nasional.docx',snapshot['snapshot_id'],snapshot['hospitals'])
        rel_path_nas = f"outputs/{out.name}/Laporan_Akhir_Nasional.docx"
        save_generated_report('LHA_WORD', 'Laporan_Akhir_Nasional.docx', rel_path_nas, 'NASIONAL')
        print('WORD NASIONAL',flush=True)
    else:
        snapshot=load_snapshot()
        snapshot_path.write_text(json.dumps(snapshot,ensure_ascii=False),encoding='utf-8')
        print(json.dumps(snapshot['summary']))

if __name__=='__main__':
    main()
