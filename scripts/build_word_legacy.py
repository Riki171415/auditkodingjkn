import json
import os
import re
import sys
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from generate_from_template import _generate_docx_legacy, format_rs_title

def rs_slug(nama_rs, max_len=40):
    slug = re.sub(r'[^A-Z0-9]+', '_', str(nama_rs).upper().strip())
    return slug.strip('_')[:max_len].rstrip('_')

def main():
    out_dir = Path('outputs/laporan_final_20260831')
    word_dir = out_dir / 'word_per_rs'
    word_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_path = out_dir / 'snapshot.json'
    snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
    
    md_dir = Path('exports/agent_outputs/final_md')
    
    for h in snapshot['hospitals']:
        kode_rs = h['kode_rs']
        nama_rs = h['nama_rs']
        slug = rs_slug(nama_rs)
        final_fname = f'LHR_{kode_rs}_{slug}.docx'
        final_path = word_dir / final_fname
        
        md_file = md_dir / f'final_md_{kode_rs}.md'
        if not md_file.exists():
            print(f"WARNING: No markdown for {kode_rs}, using empty string")
            md_text = ''
        else:
            md_text = md_file.read_text(encoding='utf-8')
            
        metadata = {
            '_meta': {'rs_name': nama_rs},
            'cases': h['cases']
        }
        
        # Format cases array to have 'rekomendasi_laporan' copied into 'keputusan_sistem' if missing
        # because the template relies on it
        for c in metadata['cases']:
            if 'keputusan_sistem' not in c:
                c['keputusan_sistem'] = c.get('rekomendasi_laporan', '-')
        
        print(f"Generating legacy Word for {kode_rs} - {nama_rs}...")
        _generate_docx_legacy(kode_rs, md_text, metadata, {})
        
        # Locate the generated legacy file
        clean_rs_name = re.sub(r'[^A-Za-z0-9]', '_', format_rs_title(nama_rs))
        legacy_path = Path('exports/laporan_review_per_rs') / f"LHR_V2_{kode_rs}_{clean_rs_name}.docx"
        
        if legacy_path.exists():
            # Move and rename to the new consistent format
            shutil.copy2(legacy_path, final_path)
            # Optional: delete the legacy one so we don't clutter
            # legacy_path.unlink()
            print(f" -> Moved to {final_path}")
        else:
            print(f" -> ERROR: Output file {legacy_path} not found!")

if __name__ == '__main__':
    main()
