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
    # Table for Generated Reports
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS generated_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_type TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        kode_rs TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
    
    # Preserve existing review fields when the frontend edits only notes/signatures.
    previous = cursor.execute('SELECT tindakan_reviewer, triggered_rules_json, reviewer_name FROM kkr_dr01 WHERE sep=?', (sep,)).fetchone()
    stored_form = json.loads(previous['tindakan_reviewer'] or '{}') if previous else {}
    defaults = {
        'analisis_reviewer': data.get('analisis_reviewer', ''),
        'keputusan': data.get('keputusan_reviewer') or data.get('keputusan', ''),
        'tingkat_keyakinan': data.get('tingkat_keyakinan', ''),
        'alasan_keputusan': data.get('alasan_keputusan', ''),
        'catatan_tambahan': data.get('catatan_tambahan', ''),
        'reviewer_name': data.get('reviewer_name', ''),
        'tanggal_review': data.get('tanggal_review', ''),
        'ketua_tim_name': data.get('ketua_tim_name', ''),
        'knavp_skor': data.get('knavp_skor', 0),
        'tingkat_risiko': data.get('tingkat_risiko', ''),
        'keputusan_sistem': data.get('keputusan_sistem', ''),
        'jumlah_beda_dual_coding': data.get('jumlah_beda_dual_coding', 0),
        'ccl_label': data.get('ccl_label', '')
    }
    stored_form.update({key: data[key] for key in data if key not in ('sep', 'kode_rs', 'triggered_rules')})
    form_data_json = json.dumps({**defaults, **stored_form}, ensure_ascii=False)
    if previous and 'reviewer_name' not in data:
        reviewer_name = previous['reviewer_name']
    
    triggered_rules_json = json.dumps(data['triggered_rules'], ensure_ascii=False) if 'triggered_rules' in data else (previous['triggered_rules_json'] if previous else '[]')
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

def get_recap_desk_review(sep=None, kode_rs=None):
    """Get recapitulation of all Desk Reviews joined with case data"""
    conn = get_audit_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            k.sep, k.kode_rs, k.reviewer_name, k.tindakan_reviewer, k.triggered_rules_json, k.updated_at,
            i.*
        FROM kkr_dr01 k
        LEFT JOIN datadb.individual_data i ON k.sep = i.sep AND k.kode_rs = i.kode_rs
        WHERE (? IS NULL OR k.sep = ?) AND (? IS NULL OR k.kode_rs = ?)
    ''', (sep, sep, kode_rs, kode_rs))
    rows = cursor.fetchall()
    conn.close()
    
    recap = []
    for r in rows:
        row = dict(r)
        try:
            fd = json.loads(row.get('tindakan_reviewer') or '{}')
        except:
            fd = {}
            
        try:
            tr = json.loads(row.get('triggered_rules_json') or '[]')
        except:
            tr = []
        
        recap.append({
            'sep': row['sep'],
            'kode_rs': row['kode_rs'],
            'nama_rs': row['nama_rs'],
            'kelas': row['kelas'],
            'reviewer_name': row['reviewer_name'],
            'tanggal': row['updated_at'],
            'updated_at': row['updated_at'],
            'inacbg': row['inacbg'],
            'deskripsi_inacbg': row.get('deskripsi_inacbg', ''),
            'idrg_code': row.get('idrg_code', fd.get('idrg_code', '')),
            'deskripsi_idrg': row.get('deskripsi_idrg', fd.get('deskripsi_idrg', '')),
            'diaglist': row.get('diaglist', ''),
            'proclist': row.get('proclist', ''),
            'diaglist_idrg': row.get('diaglist_idrg', ''),
            'proclist_idrg': row.get('proclist_idrg', ''),
            'alos': row.get('alos', 0),
            'tarif_inacbg': row['tarif_inacbg'],
            'tarif_rs': row['tarif_rs'],
            'keputusan': fd.get('keputusan', '-'),
            'rekomendasi_lanjut': fd.get('rekomendasi_lanjut', '-'),
            'tindakan_reviewer': row.get('tindakan_reviewer'),
            'triggered_rules': tr,
            'triggered_rules_json': row.get('triggered_rules_json'),
            'regional': row.get('regional'),
            'knavp_skor': fd.get('knavp_skor', 0),
            'tingkat_risiko': fd.get('tingkat_risiko', ''),
            'jumlah_beda_dual_coding': fd.get('jumlah_beda_dual_coding', 0),
            # NEW: Patient identity fields
            'nama_pasien': row.get('Nama_Pasien') or row.get('nama_pasien', ''),
            'tanggal_lahir': row.get('Birth_date') or row.get('tanggal_lahir', ''),
            'tgl_masuk': row.get('admission_date') or row.get('tgl_masuk', ''),
            'tgl_pulang': row.get('discharge_date') or row.get('tgl_pulang', ''),
            'jenis_kelamin': row.get('SEX') or row.get('jenis_kelamin', ''),
            'kelas_rawat': row.get('kelas_rawat', ''),
            'keputusan_sistem': fd.get('keputusan_sistem', '')
        })
    return recap

def get_recap_onsite():
    """Get recapitulation of all On-Site Audits joined with case data"""
    conn = get_audit_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            k.sep, k.kode_rs, k.reviewer_name, k.form_data_json, k.updated_at,
            i.nama_rs, i.kelas, i.regional, i.inacbg, i.deskripsi_inacbg, i.idrg_code, i.deskripsi_idrg, i.diaglist, i.proclist, i.tarif_inacbg, i.tarif_rs
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
            'deskripsi_inacbg': row.get('deskripsi_inacbg', ''),
            'idrg_code': row.get('idrg_code', fd.get('idrg_code', '')),
            'deskripsi_idrg': row.get('deskripsi_idrg', fd.get('deskripsi_idrg', '')),
            'diaglist': row.get('diaglist', ''),
            'proclist': row.get('proclist', ''),
            'tarif_inacbg': row['tarif_inacbg'],
            'tarif_rs': row['tarif_rs'],
            'kesimpulan': fd.get('kesimpulan', '-')
        })
    return recap

# Initialize on module import
init_audit_db()

def save_generated_report(report_type, filename, file_path, kode_rs=None):
    """Save a generated report record to the database"""
    conn = get_audit_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO generated_reports (report_type, filename, file_path, kode_rs)
        VALUES (?, ?, ?, ?)
    ''', (report_type, filename, file_path, kode_rs))
    conn.commit()
    conn.close()

def get_generated_reports():
    """Get all generated reports ordered by newest first"""
    conn = get_audit_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, report_type, filename, file_path, kode_rs, created_at
        FROM generated_reports
        ORDER BY created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    reports = []
    for r in rows:
        reports.append(dict(r))
    return reports
