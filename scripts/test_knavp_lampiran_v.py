from pathlib import Path
import sys,json,unittest,hashlib
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE));sys.path.insert(0,str(BASE/'scripts'))
from sync_knavp_lampiran_v import extract_catalog,SOURCE,build_catalog
from modules.knavp_catalog import assess_rule
from modules.rule_engine import load_rules,assess_case,validate_case,calculate_knavp_score,determine_recommendation_knavp

class LampiranVTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rules={r['rule_id']:r for r in load_rules()}

    def test_exact_source_fields_and_chapters(self):
        source=extract_catalog()
        self.assertEqual(set(self.rules),{r['rule_id'] for r in source})
        for r in source:
            for key,value in r.items():self.assertEqual(self.rules[r['rule_id']][key],value,(r['rule_id'],key))
        payload=json.loads((BASE/'rules/audit_rules.json').read_text(encoding='utf-8'))
        self.assertEqual(payload,build_catalog())
        self.assertEqual(payload['source_sha256'],hashlib.sha256(SOURCE.read_bytes()).hexdigest())

    def test_each_expression_true_false_and_missing(self):
        def witness(e):
            if e['op']=='has_any_diag':return [e['patterns'][0] if len(e['patterns'][0])>=3 else e['patterns'][0]+'00']
            return [c for i in e['items'] for c in witness(i)]
        for r in self.rules.values():
            if r['condition']['type']!='catalog_expression':continue
            with self.subTest(rule=r['rule_id']):
                yes={'ptd':'1','diaglist':';'.join(witness(r['condition']['expression']))}
                self.assertEqual(assess_rule(r,yes)['status'],'triggered')
                self.assertEqual(assess_rule(r,{'ptd':'1','diaglist':'Z99.9'})['status'],'not_triggered')
                self.assertEqual(assess_rule(r,{'ptd':'1'})['status'],'needs_review')

    def test_every_evidence_rule_requires_documented_boolean(self):
        for r in self.rules.values():
            if r['condition']['type']!='reviewer_evidence':continue
            with self.subTest(rule=r['rule_id']):
                self.assertEqual(assess_rule(r,{'ptd':'1'})['status'],'needs_review')
                for value,status in [(True,'triggered'),(False,'not_triggered')]:
                    case={'ptd':'1','rule_assessments':{r['rule_id']:{'condition_met':value,'evidence':'Evidence reference','reviewer':'Test reviewer'}}}
                    self.assertEqual(assess_rule(r,case)['status'],status)
                    case['rule_assessments'][r['rule_id']]['evidence']=''
                    self.assertEqual(assess_rule(r,case)['status'],'needs_review')

    def test_missing_or_invalid_ptd_is_not_clean(self):
        for ptd in [None,'',0,3,'nan']:
            self.assertTrue(all(r['status']=='needs_review' for r in assess_case({'ptd':ptd,'diaglist':'A01.0;O98.8'})))
        for r in self.rules.values():
            if r['ptd']=='1':self.assertEqual(assess_rule(r,{'ptd':'2'})['status'],'not_applicable')

    def test_regressions_hiv_and_manifestation(self):
        for rid,diags in [('AUDIT-COD-10','B20'),('AUDIT-COD-40','E11.4;G63.2'),('AUDIT-COD-59','E11.4')]:
            self.assertEqual(assess_rule(self.rules[rid],{'ptd':'1','diaglist':diags})['status'],'needs_review')

    def test_copd_not_broadened(self):
        r=self.rules['AUDIT-COD-20']
        self.assertEqual(assess_rule(r,{'ptd':'1','diaglist':'J44.1;J18.9'})['status'],'not_triggered')
        self.assertEqual(assess_rule(r,{'ptd':'1','diaglist':'J44.9;J18.9'})['status'],'triggered')

    def test_missing_evidence_not_numeric_proxy(self):
        for rid,case in [('AUDIT-COD-64',{'diaglist':'J96.0','rw':99}),('AUDIT-COD-65',{'diaglist':'N17.9'}),('AUDIT-COD-71',{'alos':99,'cmi':1})]:
            self.assertEqual(assess_rule(self.rules[rid],dict(case,ptd='1'))['status'],'needs_review')

    def test_no_scoring_or_automatic_triage(self):
        self.assertIsNone(calculate_knavp_score([{'severity':'High','bobot':999}]))
        for score in [0,3,4,7,8,999,None]:
            res=determine_recommendation_knavp(score,100)
            self.assertIsNone(res['total_skor']);self.assertIsNone(res['effective_skor'])
            self.assertEqual(res['keputusan_sistem'],'Memerlukan penilaian reviewer')
        self.assertFalse(any('bobot' in r for r in self.rules.values()))

    def test_unknown_condition_rejected(self):
        r=dict(self.rules['AUDIT-COD-01'],condition={'type':'missing_handler'})
        with self.assertRaises(ValueError):assess_rule(r,{'ptd':'1'})

    def test_bad_diagnosis_not_false_negative(self):
        for raw in ['nan','invalid','','A01.0;garbage',None]:
            r=assess_rule(self.rules['AUDIT-COD-01'],{'ptd':'1','diaglist':raw})
            self.assertEqual(r['status'],'needs_review')

if __name__=='__main__':unittest.main()
