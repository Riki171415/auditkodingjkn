"""Invoke the bundled artifact-tool writer; keep every report on one contract."""
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess

from modules.report_data import load_snapshot

BASE=Path(__file__).resolve().parents[1]
DEFAULT_NODE=Path('C:/Users/PUSBIKES-KEMKES/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')

def export_reports(per_rs=False, out_dir=None):
    node=Path(os.environ.get('REPORT_NODE_BIN',str(DEFAULT_NODE)))
    builder=BASE/'.report_work/build_excel.mjs'
    if not node.is_file() or not (builder.parent/'node_modules/@oai/artifact-tool').exists():
        raise RuntimeError('Runtime artifact-tool belum dikonfigurasi. Gunakan runtime workspace dan junction .report_work/node_modules.')
    
    if out_dir:
        out = Path(out_dir).resolve()
        out.mkdir(parents=True, exist_ok=True)
        if not (out/'snapshot.json').exists():
            snapshot=load_snapshot()
            (out/'snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False),encoding='utf-8')
    else:
        out=BASE/'outputs'/('rekonsiliasi_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        out.mkdir(parents=True)
        snapshot=load_snapshot()
        (out/'snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False),encoding='utf-8')

    subprocess.run([str(node),str(builder),'--output',str(out),'--per-rs-only' if per_rs else '--national-only'],cwd=BASE,check=True)
    if per_rs:
        return [str(p) for p in sorted((out/'excel_per_rs').glob('*.xlsx'))]
    return str(out/'Rekap_Nasional.xlsx')
