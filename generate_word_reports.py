import os
import sqlite3
from modules.db_manager import get_audit_db, get_recap_desk_review, save_generated_report
from modules.export_generator import generate_lha_word

def bulk_generate_word_reports():
    print("Starting Bulk Generation of Word Reports (LHA)...")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'word_reports')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    dr_data = get_recap_desk_review()
    
    # Group by RS
    rs_map = {}
    for row in dr_data:
        kode_rs = row['kode_rs']
        if kode_rs not in rs_map:
            rs_map[kode_rs] = {
                'nama_rs': row['nama_rs'],
                'cases': []
            }
        rs_map[kode_rs]['cases'].append(row)
        
    print(f"Found {len(rs_map)} hospitals with KKR data.")
    
    for kode_rs, data in rs_map.items():
        rs_name = data['nama_rs']
        cases = data['cases']
        
        safe_name = rs_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
        filename = f"LHA_{kode_rs}_{safe_name}.docx"
        output_path = os.path.join(output_dir, filename)
        
        print(f"Generating {filename} ({len(cases)} cases)...")
        generate_lha_word(kode_rs, rs_name, cases, output_path)
        
        # Save to database
        rel_path = f"exports/word_reports/{filename}"
        save_generated_report('LHA_WORD', filename, rel_path, kode_rs)
        
    print(f"SUCCESS! All reports saved to {output_dir}")

if __name__ == '__main__':
    bulk_generate_word_reports()
