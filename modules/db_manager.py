import os
import sqlite3
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_DB_PATH = os.path.join(BASE_DIR, 'audit.db')

def get_audit_db():
    """Get connection to audit database"""
    conn = sqlite3.connect(AUDIT_DB_PATH)
    data_db_path = os.path.join(BASE_DIR, 'data.db')
    conn.execute(f"ATTACH DATABASE '{data_db_path}' AS datadb")
    conn.row_factory = sqlite3.Row
    return conn

def init_audit_db():
    """Initialize audit database schema if not exists"""
    conn = get_audit_db()
    cursor = conn.cursor()
    
    # Table for KKR-DR01 (Desk Review)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kkr_dr01 (
        sep TEXT PRIMARY KEY,
        kode_rs TEXT NOT NULL,
        reviewer_name TEXT,
        tindakan_reviewer TEXT,
        triggered_rules_json TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table for KKR-OS01 (On-Site Audit)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kkr_os01 (
        sep TEXT PRIMARY KEY,
        kode_rs TEXT NOT NULL,
        reviewer_name TEXT,
        form_data_json TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_kkr_dr01(sep, data):
    """Save or update KKR-DR01 data"""
    conn = get_audit_db()
    cursor = conn.cursor()
    
    kode_rs = data.get('kode_rs', '')
    reviewer_name = data.get('reviewer_name', '')
    
    # Store all form data in tindakan_reviewer as JSON
    form_data_json = json.dumps({
        'analisis_reviewer': data.get('analisis_reviewer', ''),
        'keputusan': data.get('keputusan', ''),
        'alasan_keputusan': data.get('alasan_keputusan', ''),
        'catatan_tambahan': data.get('catatan_tambahan', ''),
        'reviewer_name': data.get('reviewer_name', ''),
        'tanggal_review': data.get('tanggal_review', ''),
        'ketua_tim_name': data.get('ketua_tim_name', '')
    }, ensure_ascii=False)
    
    triggered_rules_json = json.dumps(data.get('triggered_rules', []), ensure_ascii=False)
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
    INSERT INTO kkr_dr01 (sep, kode_rs, reviewer_name, tindakan_reviewer, triggered_rules_json, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(sep) DO UPDATE SET
        reviewer_name=excluded.reviewer_name,
        tindakan_reviewer=excluded.tindakan_reviewer,
        triggered_rules_json=excluded.triggered_rules_json,
        updated_at=excluded.updated_at
    ''', (sep, kode_rs, reviewer_name, form_data_json, triggered_rules_json, updated_at))
    
    conn.commit()
    conn.close()

def load_kkr_dr01(sep):
    """Load KKR-DR01 data for a specific SEP"""
    conn = get_audit_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM kkr_dr01 WHERE sep = ?", (sep,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        row_dict = dict(row)
        try:
            form_data = json.loads(row_dict.get('tindakan_reviewer') or '{}')
        except:
            form_data = {}
        row_dict['form_data'] = form_data
        return row_dict
    return None

def save_kkr_os01(sep, data):
    """Save or update KKR-OS01 data"""
    conn = get_audit_db()
    cursor = conn.cursor()
    
    kode_rs = data.get('kode_rs', '')
    reviewer_name = data.get('reviewer_name', '')
    form_data_json = json.dumps(data.get('form_data', {}), ensure_ascii=False)
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
    INSERT INTO kkr_os01 (sep, kode_rs, reviewer_name, form_data_json, updated_at)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(sep) DO UPDATE SET
        reviewer_name=excluded.reviewer_name,
        form_data_json=excluded.form_data_json,
        updated_at=excluded.updated_at
    ''', (sep, kode_rs, reviewer_name, form_data_json, updated_at))
    
    conn.commit()
    conn.close()

def load_kkr_os01(sep):
    """Load KKR-OS01 data for a specific SEP"""
    conn = get_audit_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM kkr_os01 WHERE sep = ?", (sep,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        row_dict = dict(row)
        try:
            row_dict['form_data'] = json.loads(row_dict.get('form_data_json') or '{}')
        except:
            row_dict['form_data'] = {}
        return row_dict
    return None

def get_recap_desk_review():
    """Get recapitulation of all Desk Reviews joined with case data"""
    conn = get_audit_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            k.sep, k.kode_rs, k.reviewer_name, k.tindakan_reviewer, k.updated_at,
            i.nama_rs, i.kelas, i.regional, i.inacbg, i.tarif_inacbg, i.tarif_rs
        FROM kkr_dr01 k
        LEFT JOIN datadb.individual_data i ON k.sep = i.sep
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    recap = []
    for r in rows:
        row = dict(r)
        try:
            fd = json.loads(row.get('tindakan_reviewer') or '{}')
        except:
            fd = {}
        
        recap.append({
            'sep': row['sep'],
            'kode_rs': row['kode_rs'],
            'nama_rs': row['nama_rs'],
            'kelas': row['kelas'],
            'reviewer_name': row['reviewer_name'],
            'tanggal': row['updated_at'],
            'updated_at': row['updated_at'],
            'inacbg': row['inacbg'],
            'tarif_inacbg': row['tarif_inacbg'],
            'tarif_rs': row['tarif_rs'],
            'keputusan': fd.get('keputusan', '-'),
            'rekomendasi_lanjut': fd.get('rekomendasi_lanjut', '-'),
            'tindakan_reviewer': row.get('tindakan_reviewer')
        })
    return recap

def get_recap_onsite():
    """Get recapitulation of all On-Site Audits joined with case data"""
    conn = get_audit_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            k.sep, k.kode_rs, k.reviewer_name, k.form_data_json, k.updated_at,
            i.nama_rs, i.kelas, i.regional, i.inacbg, i.tarif_inacbg, i.tarif_rs
        FROM kkr_os01 k
        LEFT JOIN datadb.individual_data i ON k.sep = i.sep
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    recap = []
    for r in rows:
        row = dict(r)
        try:
            fd = json.loads(row.get('form_data_json') or '{}')
        except:
            fd = {}
            
        recap.append({
            'sep': row['sep'],
            'kode_rs': row['kode_rs'],
            'nama_rs': row['nama_rs'],
            'reviewer_name': row['reviewer_name'],
            'tanggal': row['updated_at'],
            'inacbg': row['inacbg'],
            'tarif_inacbg': row['tarif_inacbg'],
            'tarif_rs': row['tarif_rs'],
            'kesimpulan': fd.get('kesimpulan', '-')
        })
    return recap

# Initialize on module import
init_audit_db()
