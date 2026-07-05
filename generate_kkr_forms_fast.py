import os
import json
import time
from multiprocessing import Pool, cpu_count
from modules.db_manager import get_recap_desk_review
from modules.data_loader import get_case_by_sep
from modules.rule_engine import validate_case
from modules.export_generator import export_kkr_dr01_pdf

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'kkr_forms')

def process_case(row):
    sep = row['sep']
    case = get_case_by_sep(sep)
    if not case: return False
    
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
    
    # Override with db column if available
    if row.get('reviewer_name'):
        kkr_data['reviewer_name'] = row['reviewer_name']
    
    if row.get('updated_at'):
        from datetime import datetime
        try:
            # updated_at format is usually YYYY-MM-DD HH:MM:SS
            dt = datetime.strptime(str(row['updated_at']).split('.')[0], '%Y-%m-%d %H:%M:%S')
            kkr_data['tanggal_review'] = dt.strftime('%d/%m/%Y')
        except:
            kkr_data['tanggal_review'] = str(row['updated_at']).split(' ')[0]
            
    validate_data = {'triggered_rules': triggered_rules}
    
    try:
        pdf_bytes = export_kkr_dr01_pdf(kkr_data, validate_data)
        
        rs_name = str(case.get('nama_rs', 'RS')).replace(' ', '_').replace('/', '_').replace('\\', '_')[:40]
        rs_code = str(case.get('kode_rs', 'UNKNOWN'))
        rs_folder_name = f"{rs_code}_{rs_name}"
        
        rs_dir = os.path.join(output_dir, rs_folder_name)
        if not os.path.exists(rs_dir):
            try:
                os.makedirs(rs_dir, exist_ok=True)
            except:
                pass
                
        sep_short = str(sep).replace('/', '_').replace('\\', '_')[:20]
        filename = f"KKR-DR01_{sep_short}.pdf"
        output_path = os.path.join(rs_dir, filename)
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        return True
    except Exception as e:
        print(f"Error on {sep}: {e}")
        return False

if __name__ == '__main__':
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    dr_data = get_recap_desk_review()
    print(f"Starting FAST Bulk Generation of {len(dr_data)} KKR-DR01 Forms...")
    
    start_time = time.time()
    
    # Use max cores for speed
    cores = cpu_count()
    print(f"Using {cores} CPU cores...")
    
    with Pool(cores) as p:
        results = p.map(process_case, dr_data)
        
    success = sum(1 for r in results if r)
    print(f"SUCCESS! Generated {success} files in {time.time() - start_time:.1f} seconds.")
