import os
import json
from modules.db_manager import get_recap_desk_review
from modules.data_loader import get_case_by_sep
from modules.rule_engine import validate_case
from modules.export_generator import export_kkr_dr01_excel

def bulk_generate_kkr_forms():
    print("Starting Bulk Generation of KKR-DR01 Forms (Excel)...")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'kkr_forms')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    dr_data = get_recap_desk_review()
    print(f"Found {len(dr_data)} cases to generate.")
    
    count = 0
    for row in dr_data:
        sep = row['sep']
        kode_rs = row['kode_rs']
        
        # We need full case to validate rules
        case = get_case_by_sep(sep)
        if not case:
            continue
            
        triggered_rules = validate_case(case)
        
        kkr_data = {
            'sep': sep,
            'kode_rs': case.get('kode_rs'),
            'nama_rs': case.get('nama_rs'),
            'inacbg': case.get('inacbg'),
            'case': case,
            'triggered_rules': triggered_rules,
            'total_triggered': len(triggered_rules)
        }
        
        try:
            form_data = json.loads(row.get('tindakan_reviewer') or '{}')
        except:
            form_data = {}
            
        kkr_data.update(form_data)
        validate_data = {'triggered_rules': triggered_rules}
        
        try:
            excel_bytes = export_kkr_dr01_excel(kkr_data, validate_data)
            
            rs_name = str(case.get('nama_rs', 'RS')).replace(' ', '_').replace('/', '_').replace('\\', '_')[:20]
            sep_short = str(sep)[:15]
            filename = f"KKR-DR01_{rs_name}_{sep_short}.xlsx"
            output_path = os.path.join(output_dir, filename)
            
            with open(output_path, 'wb') as f:
                f.write(excel_bytes)
                
            count += 1
            if count % 100 == 0:
                print(f"Generated {count} forms...")
                
        except Exception as e:
            print(f"Error generating for SEP {sep}: {e}")
            
    print(f"SUCCESS! {count} KKR forms saved to {output_dir}")

if __name__ == '__main__':
    bulk_generate_kkr_forms()
