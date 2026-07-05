"""
Aplikasi Audit Koding INA-CBG / iDRG 2025
Flask Backend - Main Application
"""
from flask import Flask, render_template, jsonify, request, send_file
import os
import sys
import json

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from data_loader import (
    load_individual_data, load_cmi_data,
    get_hospital_list, get_hospital_detail,
    get_case_by_sep, get_cases_by_rs, get_dashboard_stats,
    get_sampled_cases_by_rs, get_cochran_info, cochran_sample_size
)
from rule_engine import validate_case, validate_batch_by_rs, get_validation_summary, determine_recommendation

app = Flask(__name__)
app.config['JSON_ENSURE_ASCII'] = False


# ============================================================
# ROUTES - Pages
# ============================================================

@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/hospitals')
def hospitals():
    return render_template('hospitals.html')


@app.route('/hospitals/<kode_rs>')
def hospital_detail(kode_rs):
    return render_template('hospital_detail.html', kode_rs=kode_rs)


@app.route('/desk-review/<kode_rs>')
def desk_review(kode_rs):
    return render_template('desk_review.html', kode_rs=kode_rs)


@app.route('/kkr-dr01/<sep>')
def kkr_dr01(sep):
    return render_template('kkr_dr01.html', sep=sep)


@app.route('/kkr-os01/<sep>')
def kkr_os01(sep):
    return render_template('kkr_os01.html', sep=sep)


@app.route('/laporan')
def laporan():
    return render_template('laporan.html')


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
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        use_sample = request.args.get('use_sample', 'true').lower() == 'true'
        
        result = get_cases_by_rs(kode_rs, page=page, per_page=per_page, search=search, use_sample=use_sample)
        
        # Add Cochran info
        N_total = len(load_individual_data()[load_individual_data()['kode_rs'] == str(kode_rs)])
        result['cochran_info'] = get_cochran_info(N_total)
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/case/<sep>')
def api_case_detail(sep):
    try:
        case = get_case_by_sep(sep)
        if case is None:
            return jsonify({'success': False, 'error': 'Case not found'}), 404
        return jsonify({'success': True, 'data': case})
    except Exception as e:
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
