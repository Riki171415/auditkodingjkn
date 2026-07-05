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
        
    return df


def get_hospital_list():
    """Get unique hospitals from CMI data"""
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
    return merged.to_dict('records')


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
    return case.iloc[0].to_dict()


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
    
    total = len(rs_data)
    start = (page - 1) * per_page
    end = start + per_page
    
    cases = rs_data.iloc[start:end].copy()
    cases = cases.fillna('')
    
    return {
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
        'cases': cases.to_dict('records')
    }


def get_dashboard_stats():
    """Get overall dashboard statistics via SQL (Memory optimized)"""
    conn = get_db_connection()
    df_cmi, df_tabel = load_cmi_data()
    
    if not conn:
        return {} # Fallback not implemented for CSV here for brevity, assume DB exists
        
    cursor = conn.cursor()
    
    # Basic counts and sums
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT kode_rs) as total_rs,
            COUNT(sep) as total_kasus,
            SUM(CAST(tarif_inacbg AS FLOAT)) as total_tarif_inacbg,
            SUM(CAST(tarif_rs AS FLOAT)) as total_tarif_rs
        FROM individual_data
    ''')
    basic_stats = cursor.fetchone()
    total_rs = basic_stats['total_rs']
    total_kasus = basic_stats['total_kasus']
    total_tarif_inacbg = basic_stats['total_tarif_inacbg']
    total_tarif_rs = basic_stats['total_tarif_rs']
    
    # CMI stats
    audit_2sd = int(df_cmi[df_cmi['Audit_2SD'] == 'Audit'].shape[0])
    audit_iqr = int(df_cmi[df_cmi['Audit_IQR'] == 'Audit'].shape[0])
    
    # Regional distribution
    cursor.execute('''
        SELECT regional, COUNT(sep) as kasus, COUNT(DISTINCT kode_rs) as rs
        FROM individual_data GROUP BY regional
    ''')
    regional_dist = [dict(row) for row in cursor.fetchall()]
    
    # Class distribution
    cursor.execute('''
        SELECT kelas, COUNT(sep) as kasus, COUNT(DISTINCT kode_rs) as rs
        FROM individual_data GROUP BY kelas
    ''')
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
        'tabel_cmi': {}
    }

def get_scatter_data():
    """Get aggregated data for Casemix Scatter Plot via SQL"""
    conn = get_db_connection()
    df_cmi, _ = load_cmi_data()
    
    if not conn:
        return []
        
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            kode_rs, 
            nama_rs, 
            AVG(CAST(cmi AS FLOAT)) as avg_cmi, 
            AVG(CAST(alos AS FLOAT)) as avg_alos, 
            COUNT(sep) as total_kasus
        FROM individual_data
        GROUP BY kode_rs, nama_rs
    ''')
    
    agg = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Convert df_cmi audit status to dict for O(1) lookup
    cmi_dict = df_cmi.set_index('kode_rs')['Audit_2SD'].to_dict()
    
    data = []
    for row in agg:
        kode_rs = row['kode_rs']
        status = cmi_dict.get(kode_rs, 'N/A')
        if pd.isna(status):
            status = 'N/A'
            
        color = '#EB5757' if status == 'Audit' else ('#27AE60' if status == 'Aman' else '#0B2545')
        data.append({
            'kode_rs': kode_rs,
            'nama_rs': row['nama_rs'],
            'x': float(row['avg_cmi'] or 0),
            'y': float(row['avg_alos'] or 0),
            'z': int(row['total_kasus'] or 0),
            'status': status,
            'fill': color
        })
        
    return data
