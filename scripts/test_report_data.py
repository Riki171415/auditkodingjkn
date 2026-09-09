import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from modules.report_data import build_snapshot, normalize_case, summarize, ONSITE, SAMPLING, MONITORING, UNKNOWN

def case(**form):
    return dict(sep='sample',kode_rs='rs',nama_rs='Hospital',triggered_rules=[],tindakan_reviewer=form)

class ReportContractTests(unittest.TestCase):
    def test_saved_recommendation_wins_over_new_threshold(self):
        c=normalize_case(case(keputusan_sistem='Audit Sampling',knavp_skor=6,tingkat_risiko='Sedang'))
        self.assertEqual(c['rekomendasi_laporan'],SAMPLING)

    def test_grouper_inequality_does_not_reclassify(self):
        c=normalize_case(dict(case(keputusan_sistem='Tidak perlu tindak lanjut'),inacbg='A',idrg_code='B'))
        self.assertEqual(c['rekomendasi_laporan'],MONITORING)
        self.assertEqual(c['jumlah_beda_dual_coding'],0)

    def test_reviewer_verdict_is_preserved_not_reinterpreted(self):
        c=normalize_case(case(keputusan='Tidak Sesuai (Terindikasi Fraud/Error)'))
        self.assertEqual(c['rekomendasi_laporan'],UNKNOWN)
        self.assertEqual(c['keputusan_reviewer_asli'],'Tidak Sesuai (Terindikasi Fraud/Error)')

    def test_explicit_fallback(self):
        self.assertEqual(normalize_case(case(keputusan_sistem='',keputusan='Tidak perlu tindak lanjut'))['rekomendasi_laporan'],MONITORING)

    def test_counts_cases_not_events(self):
        summary=summarize([normalize_case(case(keputusan_sistem=ONSITE,jumlah_beda_dual_coding=3))])
        self.assertEqual((summary['dc_cases'],summary['dc_total']),(1,3))

    def test_duplicate_key_fails(self):
        with self.assertRaises(ValueError):build_snapshot([case(),case()])

    def test_hospital_is_part_of_key(self):
        s=build_snapshot([case(),dict(case(),kode_rs='another')])
        self.assertEqual(s['summary']['total'],2)

    def test_excel_half_up_rounding(self):
        rows=[normalize_case(case(knavp_skor=1))]+[normalize_case(case(knavp_skor=0)) for _ in range(7)]
        self.assertEqual(summarize(rows)['avg_score'],0.13)

if __name__=='__main__':unittest.main()
