"""Regression checks; writes only to a temporary audit database."""
import sys
import tempfile
import json
import time
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / 'scratch/test_deps'))
import app
from modules import db_manager, output_catalog

class FrontendContract(TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_output_matches_source_bytes(self):
        from modules.report_data import load_snapshot
        from modules.report_pdf import export_saved_pdf
        sep = load_snapshot()['cases'][0]['sep']
        started = time.perf_counter()
        response = self.client.get('/api/outputs/kkr/DR01/' + sep + '?inline=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, export_saved_pdf(sep))
        self.assertTrue(response.headers['Content-Disposition'].startswith('inline'))
        download = self.client.get('/api/export/dr01/pdf/' + sep)
        self.assertEqual(download.data, response.data)
        download.close()
        print('Output preview seconds:', round(time.perf_counter() - started, 3))
        response.close()

    def test_output_path_cannot_escape(self):
        with self.assertRaises(ValueError):
            output_catalog.resolve_output('../audit.db')

    def test_onsite_has_one_storage_route(self):
        rules = list(app.app.url_map.iter_rules())
        self.assertEqual(sum(r.rule == '/api/kkr-os01/save' for r in rules), 1)
        self.assertEqual(sum(r.rule.startswith('/api/kkr-os01/load/') for r in rules), 1)

    def test_save_roundtrip_preserves_review(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(db_manager, 'AUDIT_DB_PATH', str(Path(directory) / 'audit.db')):
                db_manager.init_audit_db()
                original = dict(kode_rs='TEST', keputusan='Sesuai', knavp_skor=17,
                                jumlah_beda_dual_coding=4, tingkat_risiko='Tinggi',
                                analisis_reviewer='Original analysis', triggered_rules=[{'rule_id':'TEST'}])
                db_manager.save_kkr_dr01('TEST', original)
                db_manager.save_kkr_dr01('TEST', {'catatan_sistem':'New note', 'nip_reviewer':'123'})
                saved = db_manager.load_kkr_dr01('TEST')
                for key in ('keputusan', 'knavp_skor', 'jumlah_beda_dual_coding', 'analisis_reviewer'):
                    self.assertEqual(saved['form_data'][key], original[key])
                self.assertEqual(json.loads(saved['triggered_rules_json']), original['triggered_rules'])
                self.assertEqual(saved['form_data']['catatan_sistem'], 'New note')
                payload = dict(sep='TEST', kode_rs='TEST', form_data={'kesimpulan':'Perlu Klarifikasi'})
                self.assertEqual(self.client.post('/api/kkr-os01/save', json=payload).status_code, 200)
                self.assertEqual(self.client.get('/api/kkr-os01/load/TEST').json['data']['form_data'], payload['form_data'])

    def test_single_case_does_not_load_population(self):
        from modules import data_loader
        import sqlite3
        with sqlite3.connect(BASE / 'data.db') as conn:
            sep = conn.execute('SELECT sep FROM individual_data LIMIT 1').fetchone()[0]
        original = data_loader.load_individual_data
        calls = []
        def checked(*args, **kwargs):
            calls.append(kwargs)
            return original(*args, **kwargs)
        with patch.object(data_loader, 'load_individual_data', side_effect=checked):
            started = time.perf_counter()
            case = data_loader.get_case_by_sep(sep)
        self.assertEqual(case['sep'], sep)
        self.assertEqual(calls, [{'sep':sep}])
        print('Single SEP seconds:', round(time.perf_counter() - started, 3))

if __name__ == '__main__':
    main()
