"""
Aplikasi Audit Koding INA-CBG / iDRG 2025
Flask Backend - Main Application
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import math
import traceback
import json
from datetime import datetime
from flask_cors import CORS

# Add modules to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from data_loader import (
    load_individual_data, load_cmi_data,
    get_hospital_list, get_hospital_detail,
    get_case_by_sep, get_cases_by_rs, get_dashboard_stats,
    get_sampled_cases_by_rs, get_cochran_info, cochran_sample_size
)
from rule_engine import validate_case, validate_batch_by_rs, get_validation_summary, determine_recommendation

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)
app.config['JSON_ENSURE_ASCII'] = False

PER_PAGE = 50

# -------------------------------------------------------------
# REACT APP SERVING
# -------------------------------------------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
        
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # SPA Fallback
        if os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return "Vite React build not found in frontend/dist. Please run 'npm run build' inside frontend/ directory.", 404


# ============================================================
# API - Dashboard
# ============================================================

@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    try:
        stats = get_dashboard_stats()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# API - Hospitals
# ============================================================

@app.route('/api/hospitals')
def api_hospitals():
    try:
        hospitals = get_hospital_list()
        return jsonify({'success': True, 'data': hospitals})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/hospitals/<kode_rs>')
def api_hospital_detail(kode_rs):
    try:
        detail = get_hospital_detail(kode_rs)
        return jsonify({'success': True, 'data': detail})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# API - Cases
# ============================================================

@app.route('/api/cases/<kode_rs>')
def api_cases_by_rs(kode_rs):
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', PER_PAGE))
        search = request.args.get('search', '').lower()
        
        # SQL Injection protected data load via parameterized query
        df = load_individual_data(kode_rs=kode_rs)
        
        if df.empty:
            return jsonify({'success': True, 'data': {'cases': [], 'total': 0}})
            
        N = len(df)
        n = cochran_sample_size(N)
        percentage = round((n/N)*100, 1) if N > 0 else 0
        
        # Ambil sampel (deterministic)
        import hashlib
        seed = int(hashlib.md5(kode_rs.encode()).hexdigest()[:8], 16) % (2**31)
        if n < N:
            df = df.sample(n=n, random_state=seed)
        
        if search:
            mask = (
                df['sep'].str.lower().str.contains(search, na=False) |
                df['inacbg'].str.lower().str.contains(search, na=False) |
                df['deskripsi_inacbg'].str.lower().str.contains(search, na=False)
            )
            df = df[mask]
            
        total = len(df)
        
        # Manual pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paged_df = df.iloc[start_idx:end_idx]
        
        cases = paged_df.to_dict('records')
        
        # Ganti NaN dengan None untuk JSON
        for c in cases:
            for k, v in c.items():
                if isinstance(v, float) and math.isnan(v):
                    c[k] = None
                    
        return jsonify({
            'success': True,
            'data': {
                'cases': cases,
                'total': total,
                'page': page,
                'total_pages': math.ceil(total / per_page),
                'cochran_info': {
                    'N': N,
                    'n_sample': n,
                    'percentage': percentage,
                    'formula': "Cochran Formula: n = (Z² × p × q) / e²"
                }
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/case/<sep>')
def api_case_detail(sep):
    """Ambil data kasus individual"""
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.db')
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM individual_data WHERE sep = ?", (sep,))
            row = cursor.fetchone()
            conn.close()
            if row:
                c = dict(row)
                return jsonify({'success': True, 'data': c})
            return jsonify({'success': False, 'error': 'Kasus tidak ditemukan'}), 404
        else:
            df = load_individual_data()
            case_df = df[df['sep'] == str(sep)]
            if case_df.empty:
                return jsonify({'success': False, 'error': 'Kasus tidak ditemukan'}), 404
            
            c = case_df.iloc[0].to_dict()
            for k, v in c.items():
                if isinstance(v, float) and math.isnan(v):
                    c[k] = None
            return jsonify({'success': True, 'data': c})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# API - Rule Validation (KKR-DR01)
# ============================================================

@app.route('/api/validate/<sep>')
def api_validate_case(sep):
    """Validate a single case and return KKR-DR01 data"""
    try:
        case = get_case_by_sep(sep)
        if case is None:
            return jsonify({'success': False, 'error': 'Case not found'}), 404
        
        # Run rule validation
        triggered_rules = validate_case(case)
        summary = get_validation_summary(triggered_rules)
        rekomendasi = determine_recommendation(triggered_rules)
        
        # Parse diag and proc lists for display
        diag_codes = [c.strip() for c in str(case.get('diaglist', '')).split(';') if c.strip()]
        proc_codes = [c.strip() for c in str(case.get('proclist', '')).split(';') if c.strip()]
        
        result = {
            'case': case,
            'diag_codes': diag_codes,
            'proc_codes': proc_codes,
            'triggered_rules': triggered_rules,
            'summary_by_category': summary,
            'total_triggered': len(triggered_rules),
            'rekomendasi': rekomendasi,
            'has_high_severity': any(r['severity'] == 'High' for r in triggered_rules)
        }
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/validate-batch/<kode_rs>')
def api_validate_batch(kode_rs):
    """Validate Cochran-sampled cases for a hospital"""
    try:
        # Use Cochran-sampled cases (not all cases)
        df_rs = get_sampled_cases_by_rs(kode_rs)
        
        if len(df_rs) == 0:
            return jsonify({'success': False, 'error': 'No cases found'}), 404
        
        results = validate_batch_by_rs(df_rs)
        
        # Summary
        total = len(results)
        with_findings = sum(1 for r in results if r['triggered_count'] > 0)
        onsite_recommended = sum(1 for r in results if r['rekomendasi'] == 'Direkomendasikan On-Site Audit')
        
        # Cochran info
        N_total = len(load_individual_data()[load_individual_data()['kode_rs'] == str(kode_rs)])
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'cochran_info': get_cochran_info(N_total),
                'summary': {
                    'total_kasus': total,
                    'kasus_dengan_temuan': with_findings,
                    'rekomendasi_onsite': onsite_recommended,
                    'kasus_aman': total - with_findings
                }
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


# ============================================================
# API - Save KKR (Store in session/file)
# ============================================================

KKR_STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'exports', 'kkr_data')
os.makedirs(KKR_STORAGE_DIR, exist_ok=True)

@app.route('/api/kkr-dr01/save', methods=['POST'])
def api_save_kkr_dr01():
    """Save KKR-DR01 form data"""
    try:
        data = request.get_json()
        sep = data.get('sep', '').replace('/', '_').replace('\\', '_')
        
        filepath = os.path.join(KKR_STORAGE_DIR, f'KKR-DR01_{sep}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'KKR-DR01 berhasil disimpan'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/kkr-dr01/load/<sep>')
def api_load_kkr_dr01(sep):
    """Load saved KKR-DR01 data"""
    try:
        sep_safe = sep.replace('/', '_').replace('\\', '_')
        filepath = os.path.join(KKR_STORAGE_DIR, f'KKR-DR01_{sep_safe}.json')
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': True, 'data': None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/kkr-os01/save', methods=['POST'])
def api_save_kkr_os01():
    """Save KKR-OS01 form data"""
    try:
        data = request.get_json()
        sep = data.get('sep', '').replace('/', '_').replace('\\', '_')
        
        filepath = os.path.join(KKR_STORAGE_DIR, f'KKR-OS01_{sep}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'KKR-OS01 berhasil disimpan'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/kkr-os01/load/<sep>')
def api_load_kkr_os01(sep):
    """Load saved KKR-OS01 data"""
    try:
        sep_safe = sep.replace('/', '_').replace('\\', '_')
        filepath = os.path.join(KKR_STORAGE_DIR, f'KKR-OS01_{sep_safe}.json')
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': True, 'data': None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# API - Cochran Info
# ============================================================

@app.route('/api/cochran/<kode_rs>')
def api_cochran_info(kode_rs):
    """Get Cochran sample size info for a hospital"""
    try:
        df = load_individual_data()
        N = len(df[df['kode_rs'] == str(kode_rs)])
        info = get_cochran_info(N)
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# API - Export KKR (Excel & PDF)
# ============================================================

@app.route('/api/export/dr01/excel/<sep>')
def api_export_dr01_excel(sep):
    """Export KKR-DR01 as Excel with QR barcode"""
    try:
        from modules.export_generator import export_kkr_dr01_excel
        import io
        
        # Load saved KKR or build from validation
        sep_safe = sep.replace('/', '_').replace('\\', '_')
        filepath = os.path.join(KKR_STORAGE_DIR, f'KKR-DR01_{sep_safe}.json')
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                kkr_data = json.load(f)
        else:
            # Build from case data
            case = get_case_by_sep(sep)
            if not case:
                return jsonify({'success': False, 'error': 'Case not found'}), 404
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
        
        # Ensure case data
        if 'case' not in kkr_data:
            case = get_case_by_sep(sep)
            kkr_data['case'] = case or {}
        
        validate_data = {
            'triggered_rules': kkr_data.get('triggered_rules', [])
        }
        
        excel_bytes = export_kkr_dr01_excel(kkr_data, validate_data)
        
        nama_rs = str(kkr_data.get('nama_rs', 'RS')).replace(' ', '_')[:20]
        sep_short = str(sep)[:15]
        filename = f"KKR-DR01_{nama_rs}_{sep_short}.xlsx"
        
        return send_file(
            io.BytesIO(excel_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/export/dr01/pdf/<sep>')
def api_export_dr01_pdf(sep):
    """Export KKR-DR01 as PDF with QR barcode"""
    try:
        from modules.export_generator import export_kkr_dr01_pdf
        import io
        
        sep_safe = sep.replace('/', '_').replace('\\', '_')
        filepath = os.path.join(KKR_STORAGE_DIR, f'KKR-DR01_{sep_safe}.json')
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                kkr_data = json.load(f)
        else:
            case = get_case_by_sep(sep)
            if not case:
                return jsonify({'success': False, 'error': 'Case not found'}), 404
            triggered_rules = validate_case(case)
            kkr_data = {
                'sep': sep, 'kode_rs': case.get('kode_rs'),
                'nama_rs': case.get('nama_rs'), 'inacbg': case.get('inacbg'),
                'case': case, 'triggered_rules': triggered_rules,
                'total_triggered': len(triggered_rules)
            }
        
        if 'case' not in kkr_data:
            kkr_data['case'] = get_case_by_sep(sep) or {}
        
        validate_data = {'triggered_rules': kkr_data.get('triggered_rules', [])}
        
        pdf_bytes = export_kkr_dr01_pdf(kkr_data, validate_data)
        
        nama_rs = str(kkr_data.get('nama_rs', 'RS')).replace(' ', '_')[:20]
        sep_short = str(sep)[:15]
        filename = f"KKR-DR01_{nama_rs}_{sep_short}.pdf"
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/export/dr01/qr/<sep>')
def api_export_dr01_qr(sep):
    """Return QR barcode as base64 data URI for inline use"""
    try:
        from modules.export_generator import generate_qr_base64, generate_qr_payload
        
        sep_safe = sep.replace('/', '_').replace('\\', '_')
        filepath = os.path.join(KKR_STORAGE_DIR, f'KKR-DR01_{sep_safe}.json')
        
        kkr_data = {'sep': sep, 'reviewer': ''}
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                kkr_data = json.load(f)
        
        qr_b64 = generate_qr_base64(kkr_data, 'KKR-DR01')
        payload = generate_qr_payload(kkr_data, 'KKR-DR01')
        
        return jsonify({
            'success': True,
            'data': {
                'qr_base64': qr_b64,
                'payload': payload
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# API - Reports
# ============================================================

@app.route('/api/laporan/rekapitulasi')
def api_laporan_rekapitulasi():
    """Generate rekapitulasi from all saved KKR"""
    try:
        rekapitulasi = []
        
        for filename in os.listdir(KKR_STORAGE_DIR):
            if filename.startswith('KKR-DR01_') and filename.endswith('.json'):
                filepath = os.path.join(KKR_STORAGE_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                rekapitulasi.append({
                    'type': 'DR01',
                    'sep': data.get('sep', ''),
                    'nama_rs': data.get('nama_rs', ''),
                    'kode_rs': data.get('kode_rs', ''),
                    'inacbg': data.get('inacbg', ''),
                    'total_triggered': data.get('total_triggered', 0),
                    'keputusan': data.get('keputusan_reviewer', ''),
                    'tanggal': data.get('tanggal_review', ''),
                    'reviewer': data.get('reviewer', '')
                })
        
        return jsonify({'success': True, 'data': rekapitulasi})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("  APLIKASI AUDIT KODING INA-CBG / iDRG 2025")
    print("  Pusat Pembiayaan Kesehatan - Kementerian Kesehatan")
    print("=" * 60)
    print("\nMemuat data... (mohon tunggu)")
    
    # Pre-load data
    try:
        load_cmi_data()
        print("[OK] Data CMI berhasil dimuat")
    except Exception as e:
        print(f"[WARN] Gagal muat CMI: {e}")
    
    try:
        load_individual_data()
        print("[OK] Data Individual berhasil dimuat")
    except Exception as e:
        print(f"[WARN] Gagal muat Individual: {e}")
    
    print("\nServer berjalan di: http://localhost:5000")
    print("Tekan Ctrl+C untuk menghentikan server\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
