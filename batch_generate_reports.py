import os
import glob
import json
import re
from generate_from_template import generate_docx

def main():
    print("Mulai Batch Generate DOCX untuk semua RS...")
    md_files = glob.glob('exports/agent_outputs/final_md/final_md_*.md')
    
    total = len(md_files)
    success = 0
    
    for i, mf in enumerate(md_files, 1):
        kode_rs = re.search(r'final_md_(\d+)\.md', mf).group(1)
        
        # Prioritaskan file approved jika ada
        approved_mf = f'exports/agent_outputs/approved/approved_{kode_rs}.md'
        target_mf = approved_mf if os.path.exists(approved_mf) else mf
        
        with open(target_mf, 'r', encoding='utf-8') as f:
            md_text = f.read()
            
        meta_file = f'exports/agent_outputs/data_review/data_review_{kode_rs}.json'
        if not os.path.exists(meta_file):
            print(f"[{i}/{total}] SKIP {kode_rs} - Metadata tidak ditemukan")
            continue
            
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        print(f"[{i}/{total}] Generating Laporan RS: {kode_rs} ...")
        
        # Sesuai prompt: ganti "Tim Auditor" jadi "Tim Reviewer" untuk semua RS
        md_text = re.sub(r'(?i)Tim Auditor Pusat Pembiayaan Kesehatan', 'Tim Reviewer Pusat Pembiayaan Kesehatan', md_text)
        
        try:
            generate_docx(kode_rs, md_text, metadata, {})
            success += 1
        except Exception as e:
            print(f"[{i}/{total}] ERROR {kode_rs}: {e}")
            
    print(f"\nSelesai! Berhasil memproses {success} dari {total} Rumah Sakit.")

if __name__ == '__main__':
    main()
