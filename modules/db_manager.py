import os
import sqlite3
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_DB_PATH = os.path.join(BASE_DIR, 'audit.db')

def get_audit_db():
    """Get connection to audit database"""
    conn = sqlite3.connect(AUDIT_DB_PATH)
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
        catatan TEXT,
        kesimpulan TEXT,
        tindakan_reviewer TEXT,
        triggered_rules_json TEXT,
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

# Initialize on module import
init_audit_db()
