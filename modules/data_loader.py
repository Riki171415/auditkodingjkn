"""
Data Loader Module
Loads and caches CSV (Individual Data) and Excel (CMI) data
Includes Cochran sampling per RS
"""
import pandas as pd
import os
import json
import math
import hashlib
import sqlite3
from modules.rule_engine import validate_case


# ============================================================
# Cochran Sampling Formula
# ============================================================

def cochran_sample_size(N, Z=1.96, p=0.5, q=0.5, d=0.05):
    """
    Cochran formula for finite population sample size:
    n = (Z² * p * q * N) / (d²*(N-1) + Z²*p*q)
    
    Args:
        N: Total population size (total kasus RS)
        Z: 1.96 for 95% CI
        p: Estimated proportion (0.5 = max variance)
        q: 1-p = 0.5
        d: Margin of error (5% = 0.05)
    Returns:
        Sample size n (integer)
    """
    if N <= 0:
        return 0
    numerator = (Z ** 2) * p * q * N
    denominator = (d ** 2) * (N - 1) + (Z ** 2) * p * q
    n = math.ceil(numerator / denominator)
    return min(n, N)  # Sample cannot exceed population


def get_cochran_info(N):
    """Return Cochran sample size with explanation"""
    n = cochran_sample_size(N)
    return {
        'N': N,
        'n_sample': n,
        'formula': 'n = (Z²·p·q·N) / (d²(N-1) + Z²·p·q)',
        'params': {'Z': 1.96, 'p': 0.5, 'q': 0.5, 'd': 0.05},
        'percentage': round(n / N * 100, 1) if N > 0 else 0
    }

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data.db')

# Caches
_cmi_data = None
_cmi_hospitals = None
_individual_data = None
_icd_dict = None

def get_icd_dict():
    """Load external ICD dictionary"""
    global _icd_dict
    if _icd_dict is not None:
        return _icd_dict
    try:
        import pandas as pd
        csv_path = r'D:\KERJAAN PUSBIKES\Audit Koding 2025\MRCONSO - mrconso_20250326check.csv'
        df = pd.read_csv(csv_path, usecols=['CODE', 'STR', 'SAB'], dtype=str)
        # Filter for ICD10 and ICD9CM
        df = df[df['SAB'].isin(['ICD10_2010', 'ICD9CM_2010'])]
        # Drop duplicates keeping last
        df = df.dropna(subset=['CODE', 'STR']).drop_duplicates(subset=['CODE'], keep='last')
        _icd_dict = dict(zip(df['CODE'], df['STR']))
    except Exception as e:
        print(f"[DataLoader] Warning: Could not load MRCONSO CSV: {e}")
        _icd_dict = {}
    return _icd_dict

def get_db_connection():
    """Return SQLite connection if DB exists, else None"""
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    return None

def load_cmi_data():
    """Load CMI data from SQLite or Excel"""
    global _cmi_data, _cmi_hospitals
    if _cmi_data is not None:
        return _cmi_data, _cmi_hospitals
    
    conn = get_db_connection()
    if conn:
        print("[DataLoader] Loading CMI data from SQLite...")
        query = "SELECT * FROM cmi_data"
        _cmi_data = pd.read_sql_query(query, conn)
        conn.close()
    else:
        print("[DataLoader] Loading CMI Excel data...")
        cmi_path = os.path.join(BASE_DIR, 'V2_CMI_INACBG_2025_CLEAN_20260704.xlsx')
        _cmi_data = pd.read_excel(cmi_path, dtype=str)
    
    print(f"[DataLoader] Loaded {len(_cmi_data)} rows from CMI data")
    
    # Process numeric columns
    numeric_cols = ['total_kasus_cmi', 'kasus_rs', 'casemix', 'cmi', 'alos']
    for col in numeric_cols:
        if col in _cmi_data.columns:
            _cmi_data[col] = pd.to_numeric(_cmi_data[col], errors='coerce')
    
    # Ensure kode_rs is string
    if 'kode_rs' in _cmi_data.columns:
        _cmi_data['kode_rs'] = _cmi_data['kode_rs'].astype(str)
        _cmi_hospitals = _cmi_data['kode_rs'].unique().tolist()
    else:
        _cmi_hospitals = []
        
    return _cmi_data, _cmi_hospitals

def load_individual_data(kode_rs=None):
    """Load Individual data from SQLite (with parameterized query) or CSV"""
    global _individual_data
    
    conn = get_db_connection()
    if conn:
        if kode_rs:
            # SQL INJECTION PROTECTION: Parameterized query
            print(f"[DataLoader] Loading Individual data for RS {kode_rs} from SQLite...")
            query = "SELECT * FROM individual_data WHERE kode_rs = ?"
            df = pd.read_sql_query(query, conn, params=(kode_rs,))
        else:
            print("[DataLoader] Loading ALL Individual data from SQLite...")
            query = "SELECT * FROM individual_data"
            df = pd.read_sql_query(query, conn)
        conn.close()
    else:
        if _individual_data is not None:
            df = _individual_data
        else:
            print("[DataLoader] Loading individual CSV data...")
            csv_path = os.path.join(BASE_DIR, 'Individual Data_RS Sampel Audit_INACBG_2025_20260704.csv')
            df = pd.read_csv(csv_path, sep=',', dtype=str)
            _individual_data = df
        
        if kode_rs:
            df = df[df['kode_rs'] == str(kode_rs)]
            
    # Pre-process numeric
    if 'tarif_inacbg' in df.columns:
        df['tarif_inacbg'] = pd.to_numeric(df['tarif_inacbg'], errors='coerce')
    if 'tarif_rs' in df.columns:
        df['tarif_rs'] = pd.to_numeric(df['tarif_rs'], errors='coerce')
    if 'alos' in df.columns:
        df['alos'] = pd.to_numeric(df['alos'], errors='coerce')
    if 'cmi' in df.columns:
        df['cmi'] = pd.to_numeric(df['cmi'], errors='coerce')
        
    return df


def get_hospital_list(sample_only=False):
    """Get unique hospitals from CMI data, optionally filtered to 40 RS"""
    df_cmi, _ = load_cmi_data()
    df_ind = load_individual_data()
    
    # Get hospitals that appear in individual data (audit sample)
    audit_hospitals = df_ind[['kode_rs', 'nama_rs', 'kelas', 'nama_prop', 'regional', 'pemilik']].drop_duplicates('kode_rs')
    
    # Merge with CMI data
    merged = audit_hospitals.merge(
        df_cmi[['kode_rs', 'jumlah_kasus', 'casemix', 'cmi', 'alos', 'Kategori_2SD', 'Audit_2SD', 'Kategori_IQR', 'Audit_IQR']],
        on='kode_rs',
        how='left'
    )
    
    merged = merged.fillna({'Audit_2SD': 'N/A', 'Audit_IQR': 'N/A'})
    
    # Sort by CMI descending
    merged['cmi_num'] = pd.to_numeric(merged['cmi'], errors='coerce').fillna(0)
    merged = merged.sort_values(by='cmi_num', ascending=False)
    merged = merged.drop(columns=['cmi_num'])
    
    if sample_only:
        # Filter 20 P and 20 S
        p_hospitals = merged[merged['pemilik'].str.upper() == 'P'].head(20)
        s_hospitals = merged[merged['pemilik'].str.upper() == 'S'].head(20)
        merged = pd.concat([p_hospitals, s_hospitals])
    
    return merged.to_dict('records')

def get_sample_hospital_codes():
    """Helper to quickly get the 40 RS codes"""
    hospitals = get_hospital_list(sample_only=True)
    return [h['kode_rs'] for h in hospitals]


def get_hospital_detail(kode_rs):
    """Get single hospital detail with all cases"""
    df_ind = load_individual_data()
    df_cmi, _ = load_cmi_data()
    
    kode_rs = str(kode_rs)
    rs_data = df_ind[df_ind['kode_rs'] == kode_rs].copy()
    
    # Get CMI detail
    cmi_data = df_cmi[df_cmi['kode_rs'] == kode_rs].to_dict('records')
    cmi_info = cmi_data[0] if cmi_data else {}
    
    # Basic stats
    stats = {
        'total_kasus': len(rs_data),
        'total_tarif_inacbg': float(rs_data['tarif_inacbg'].sum()),
        'total_tarif_rs': float(rs_data['tarif_rs'].sum()),
        'selisih_tarif': float(rs_data['tarif_rs'].sum() - rs_data['tarif_inacbg'].sum()),
        'avg_alos': float(rs_data['alos'].mean()) if len(rs_data) > 0 else 0,
        'avg_cmi': float(rs_data['cmi'].mean()) if len(rs_data) > 0 else 0,
    }
    
    return {
        'info': rs_data[['kode_rs', 'nama_rs', 'kelas', 'nama_prop', 'regional', 'pemilik']].iloc[0].to_dict() if len(rs_data) > 0 else {},
        'cmi_info': cmi_info,
        'stats': stats,
        'cases': rs_data.head(500).to_dict('records')  # Limit for performance
    }


def get_case_by_sep(sep):
    """Get single case by SEP number"""
    df_ind = load_individual_data()
    case = df_ind[df_ind['sep'] == sep]
    if len(case) == 0:
        return None
    
    case_dict = case.iloc[0].to_dict()
    
    # Attach ICD descriptions
    icd_dict = get_icd_dict()
    icd_desc_map = {}
    
    # Process diagnoses
    if case_dict.get('diaglist'):
        for code in str(case_dict['diaglist']).split(';'):
            code = code.strip()
            if code:
                icd_desc_map[code] = icd_dict.get(code) or icd_dict.get(code.replace('.', '')) or '-'
                
    # Process procedures
    if case_dict.get('proclist'):
        for code in str(case_dict['proclist']).split(';'):
            code = code.strip()
            if code:
                icd_desc_map[code] = icd_dict.get(code) or icd_dict.get(code.replace('.', '')) or '-'
                
    case_dict['icd_desc_map'] = icd_desc_map
    return case_dict


def get_sampled_cases_by_rs(kode_rs):
    """
    Get Cochran-sampled cases for a hospital.
    Sample is deterministic (seeded by kode_rs hash) for reproducibility.
    """
    df_ind = load_individual_data()
    kode_rs = str(kode_rs)
    rs_data = df_ind[df_ind['kode_rs'] == kode_rs].copy()
    N = len(rs_data)
    
    if N == 0:
        return pd.DataFrame()
    
    n = cochran_sample_size(N)
    
    # Deterministic seed based on kode_rs for reproducibility
    seed = int(hashlib.md5(kode_rs.encode()).hexdigest()[:8], 16) % (2**31)
    
    if n >= N:
        return rs_data
    
    # Stratified sample by severity/complexity if possible
    # Otherwise random sample
    sampled = rs_data.sample(n=n, random_state=seed)
    return sampled


def get_cases_by_rs(kode_rs, page=1, per_page=50, search='', use_sample=True):
    """Get paginated cases for a hospital (Cochran-sampled)"""
    df_ind = load_individual_data()
    kode_rs = str(kode_rs)
    
    # Use sampled or full dataset
    if use_sample:
        rs_data = get_sampled_cases_by_rs(kode_rs)
    else:
        rs_data = df_ind[df_ind['kode_rs'] == kode_rs].copy()
    
    if search:
        mask = (
            rs_data['sep'].astype(str).str.contains(search, case=False, na=False) |
            rs_data['inacbg'].astype(str).str.contains(search, case=False, na=False) |
            rs_data['diaglist'].astype(str).str.contains(search, case=False, na=False)
        )
        rs_data = rs_data[mask]
    
    cases = rs_data.copy()
    
    # Apply rules
    cases['rules'] = cases.apply(lambda row: validate_case(row.to_dict()), axis=1)
    cases['needs_audit'] = cases['rules'].apply(lambda x: len(x) > 0)
    
    cases = cases.fillna('')
    
    # Sort by needs_audit descending (True first)
    cases = cases.sort_values(by=['needs_audit'], ascending=[False])
    
    # Pagination
    total = len(cases)
    start = (page - 1) * per_page
    end = start + per_page
    
    cases = cases.iloc[start:end].copy()
    
    return {
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
        'cases': cases.to_dict('records')
    }


def get_dashboard_stats(sample_only=False):
    """Get overall dashboard statistics via SQL (Memory optimized)"""
    conn = get_db_connection()
    df_cmi, df_tabel = load_cmi_data()
    
    if not conn:
        return {} # Fallback not implemented for CSV here for brevity, assume DB exists
        
    cursor = conn.cursor()
    
    # Basic counts and sums
    
    where_clause = ""
    if sample_only:
        codes = get_sample_hospital_codes()
        placeholders = ','.join(['?'] * len(codes))
        where_clause = f" WHERE kode_rs IN ({placeholders})"
    
    query = f'''
        SELECT 
            COUNT(DISTINCT kode_rs) as total_rs,
            COUNT(sep) as total_kasus,
            SUM(CAST(tarif_inacbg AS FLOAT)) as total_tarif_inacbg,
            SUM(CAST(tarif_rs AS FLOAT)) as total_tarif_rs
        FROM individual_data
        {where_clause}
    '''
    
    if sample_only:
        cursor.execute(query, codes)
    else:
        cursor.execute(query)
    basic_stats = cursor.fetchone()
    total_rs = basic_stats['total_rs']
    total_kasus = basic_stats['total_kasus']
    total_tarif_inacbg = basic_stats['total_tarif_inacbg']
    total_tarif_rs = basic_stats['total_tarif_rs']
    
    # CMI stats
    audit_2sd = int(df_cmi[df_cmi['Audit_2SD'] == 'Audit'].shape[0])
    audit_iqr = int(df_cmi[df_cmi['Audit_IQR'] == 'Audit'].shape[0])
    
    # Regional distribution
    cursor.execute(f'''
        SELECT regional, COUNT(sep) as kasus, COUNT(DISTINCT kode_rs) as rs
        FROM individual_data {where_clause} GROUP BY regional
    ''', codes if sample_only else ())
    regional_dist = [dict(row) for row in cursor.fetchall()]
    
    # Class distribution
    cursor.execute(f'''
        SELECT kelas, COUNT(sep) as kasus, COUNT(DISTINCT kode_rs) as rs
        FROM individual_data {where_clause} GROUP BY kelas
    ''', codes if sample_only else ())
    kelas_dist = [dict(row) for row in cursor.fetchall()]
    
    # Top RS by tarif discrepancy
    cursor.execute('''
        SELECT kode_rs, nama_rs, 
               SUM(CAST(tarif_rs AS FLOAT)) - SUM(CAST(tarif_inacbg AS FLOAT)) as selisih,
               COUNT(sep) as kasus
        FROM individual_data 
        GROUP BY kode_rs, nama_rs
        ORDER BY selisih DESC
        LIMIT 10
    ''')
    top_rs = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Calculate CMI metrics
    cmi_metrics = {}
    if not df_cmi.empty:
        df_cmi['casemix_num'] = pd.to_numeric(df_cmi['casemix'], errors='coerce').fillna(0)
        df_cmi['kasus_num'] = pd.to_numeric(df_cmi['jumlah_kasus'], errors='coerce').fillna(0)
        
        tot_casemix = df_cmi['casemix_num'].sum()
        tot_kasus = df_cmi['kasus_num'].sum()
        cmi_metrics['Nasional'] = (tot_casemix / tot_kasus) if tot_kasus > 0 else 0
        
        for cls in ['A', 'B', 'C', 'D']:
            df_cls = df_cmi[df_cmi['KELAS'].str.upper() == cls]
            c_casemix = df_cls['casemix_num'].sum()
            c_kasus = df_cls['kasus_num'].sum()
            cmi_metrics[f'Kelas {cls}'] = (c_casemix / c_kasus) if c_kasus > 0 else 0
    
    return {
        'total_rs': total_rs,
        'total_kasus': total_kasus,
        'total_tarif_inacbg': total_tarif_inacbg,
        'total_tarif_rs': total_tarif_rs,
        'selisih_total': total_tarif_rs - total_tarif_inacbg,
        'audit_2sd': audit_2sd,
        'audit_iqr': audit_iqr,
        'regional_dist': regional_dist,
        'kelas_dist': kelas_dist,
        'top_rs_selisih': top_rs,
        'cmi_metrics': cmi_metrics,
        'tabel_cmi': {}
    }

def get_scatter_data(sample_only=False):
    """Get CMI scatter plot data with limit to avoid large payloads"""
    df_cmi, _ = load_cmi_data()
    
    if sample_only:
        codes = get_sample_hospital_codes()
        df_cmi = df_cmi[df_cmi['kode_rs'].isin(codes)]
        
    if df_cmi is None or df_cmi.empty:
        return {'points': [], 'boundaries': {}, 'insights': {}}
        
    # Ensure numeric
    cmi_series = pd.to_numeric(df_cmi['cmi'], errors='coerce').dropna()
    
    # Calculate boundaries
    mean_cmi = cmi_series.mean()
    std_cmi = cmi_series.std()
    atas_2sd = mean_cmi + (2 * std_cmi)
    bawah_2sd = mean_cmi - (2 * std_cmi)
    
    q1 = cmi_series.quantile(0.25)
    q3 = cmi_series.quantile(0.75)
    iqr = q3 - q1
    atas_iqr = q3 + (1.5 * iqr)
    bawah_iqr = q1 - (1.5 * iqr)
    
    boundaries = {
        'mean_cmi': float(mean_cmi),
        'atas_2sd': float(atas_2sd),
        'bawah_2sd': float(bawah_2sd),
        'atas_iqr': float(atas_iqr),
        'bawah_iqr': float(bawah_iqr)
    }
    
    points = []
    outlier_2sd_count = 0
    outlier_iqr_count = 0
    
    for _, row in df_cmi.iterrows():
        cmi_val = float(row.get('cmi', 0)) if pd.notna(row.get('cmi')) else 0
        if cmi_val <= 0:
            continue
            
        status_2sd = str(row.get('Audit_2SD', ''))
        status_iqr = str(row.get('Audit_IQR', ''))
        
        is_2sd = status_2sd.lower() == 'audit'
        is_iqr = status_iqr.lower() == 'audit'
        
        if is_2sd:
            status = 'Outlier 2SD'
            color = '#EB5757'
            outlier_2sd_count += 1
        elif is_iqr:
            status = 'Outlier IQR'
            color = '#F39C12'
            outlier_iqr_count += 1
        else:
            status = 'Inlier (Normal)'
            color = '#3498DB'
            
        points.append({
            'kode_rs': row.get('kode_rs', ''),
            'nama_rs': row.get('nama_rs', ''),
            'kelas': row.get('KELAS', ''),
            'x': cmi_val,
            'y': float(row.get('alos', 0)) if pd.notna(row.get('alos')) else 0,
            'z': int(row.get('jumlah_kasus', 1)) if pd.notna(row.get('jumlah_kasus')) else 1,
            'status': status,
            'fill': color
        })
        
    insights = {
        'total_rs': len(points),
        'outlier_2sd_count': outlier_2sd_count,
        'outlier_iqr_count': outlier_iqr_count
    }
    
    return {
        'points': points,
        'boundaries': boundaries,
        'insights': insights
    }
