import sys,json,unittest
from pathlib import Path
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'.report_work/knavp_test_deps'))
sys.path.insert(0,str(BASE))
import app
from modules import db_manager

class APIContract(unittest.TestCase):
    def setUp(self):
        self.client=app.app.test_client()
        self.case={'sep':'TEST','kode_rs':'TEST','nama_rs':'Test hospital','diaglist':'A01.0;O98.8','proclist':'','ptd':'1'}
        self.saved={'sep':'TEST','kode_rs':'TEST','nama_rs':'Test hospital','tindakan_reviewer':json.dumps({'knavp_skor':8,'keputusan_sistem':'Direkomendasikan On-Site Audit'}),'triggered_rules_json':'[]'}

    def call(self,method,payload=None,saved=None):
        with patch.object(app,'get_case_by_sep',return_value=self.case),patch.object(db_manager,'get_recap_desk_review',return_value=[saved or self.saved]):
            return getattr(self.client,method)('/api/validate/TEST',json=payload)

    def test_get_preserves_old_review(self):
        response=self.call('get')
        self.assertEqual(response.status_code,200,response.json)
        d=response.json['data'];self.assertTrue(d['saved_review']);self.assertEqual(d['knavp']['total_skor'],8)
        self.assertEqual(d['knavp']['keputusan_sistem'],'Direkomendasikan On-Site Audit')

    def test_post_evaluates_without_saved_override(self):
        response=self.call('post',{'ptd':'1'})
        self.assertEqual(response.status_code,200,response.json)
        d=response.json['data'];self.assertFalse(d['saved_review']);self.assertIsNone(d['knavp']['total_skor'])
        self.assertEqual(len(d['rule_assessments']),44)
        self.assertIn('AUDIT-COD-01',[r['rule_id'] for r in d['triggered_rules']])
        self.assertFalse(d['knavp']['scoring_defined'])

    def test_evidence_evaluated(self):
        payload={'ptd':'1','rule_assessments':{'AUDIT-COD-40':{'condition_met':False,'evidence':'Reviewed code pairing','reviewer':'Tester'}}}
        d=self.call('post',payload).json['data']
        self.assertEqual(next(r for r in d['rule_assessments'] if r['rule_id']=='AUDIT-COD-40')['status'],'not_triggered')

    def test_saved_null_score_stays_null_and_evidence_loaded(self):
        s=dict(self.saved,tindakan_reviewer=json.dumps({'scoring_defined':False,'knavp_skor':None,'catalog_version':'knavp-lampiran-v-20260907','ptd':'2','rule_assessments':{}}))
        d=self.call('get',saved=s).json['data']
        self.assertIsNone(d['knavp']['total_skor'])
        self.assertEqual(next(r for r in d['rule_assessments'] if r['rule_id']=='AUDIT-COD-23')['status'],'not_applicable')

    def test_invalid_payload_rejected(self):
        response=self.call('post',[]);self.assertEqual(response.status_code,400)

if __name__=='__main__':unittest.main()
