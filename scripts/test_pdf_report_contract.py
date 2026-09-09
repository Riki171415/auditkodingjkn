import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from modules.report_data import load_snapshot
from modules.report_pdf import export_pdf,export_saved_pdf

class PDFContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.snapshot=load_snapshot()

    def text(self,c,demographics=None):
        return '\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(export_pdf(c,self.snapshot['snapshot_id'],demographics))).pages)

    def test_preserves_reviewer_verdict_and_recommendation_separately(self):
        c=next(c for c in self.snapshot['cases'] if c['rekomendasi_laporan']=='Audit Sampling (Klarifikasi)')
        t=self.text(c)
        self.assertIn(c['keputusan_reviewer_asli'],t)
        self.assertIn(c['keputusan_sistem'],t)
        self.assertIn(c['rekomendasi_laporan'],t)

    def test_missing_risk_is_not_filled_with_low(self):
        c=next(c for c in self.snapshot['cases'] if c['tingkat_risiko']=='Belum diisi')
        # The cover contains the reference form's three unselected risk labels.
        # Verify the authoritative saved-value table does not substitute low risk.
        t=self.text(c).split('1. RINGKASAN HASIL REVIEW TERSIMPAN', 1)[1].split('AKHIR RINGKASAN TERSIMPAN')[0]
        self.assertIn('Belum diisi',t)
        self.assertNotIn('Rendah',t)

    def test_missing_identities_are_explicitly_missing(self):
        t=self.text(self.snapshot['cases'][0])
        self.assertIn('Nama pasien\nTidak tersedia pada sumber',t)
        self.assertIn('Nomor klaim / peserta\nTidak tersedia pada sumber',t)
        self.assertIn('DPJP\nTidak tersedia pada sumber',t)

    def test_identity_is_escaped_without_interpreting_markup(self):
        t=self.text(self.snapshot['cases'][0],{'Nama_Pasien':'TEST <A> & B'})
        self.assertIn('TEST <A> & B',t)

    def test_unknown_or_ambiguous_saved_review_fails(self):
        with patch('modules.db_manager.get_recap_desk_review',return_value=[]):
            with self.assertRaises(ValueError):export_saved_pdf('missing')
        with patch('modules.db_manager.get_recap_desk_review',return_value=[{},{}]):
            with self.assertRaises(ValueError):export_saved_pdf('duplicate')

    def test_reference_cover_and_overflow_detail(self):
        c = dict(self.snapshot['cases'][0])
        c['triggered_rules'] = [dict(rule_id=f'TEST-{i}', nama_aturan=f'Aturan {i}',
                                     evidence=f'BUKTI-LENGKAP-{i}') for i in range(9)]
        pdf = PdfReader(io.BytesIO(export_pdf(c, self.snapshot['snapshot_id'])))
        cover = ' '.join(pdf.pages[0].extract_text().split())
        self.assertIn('HASIL VALIDASI OTOMATIS', cover)
        for title in ['1. IDENTITAS KLAIM', '2. INFORMASI GROUPING', '3. INFORMASI DUAL CODING',
                      '4. HASIL VALIDASI RULE', '5. REKOMENDASI', '6. CATATAN SISTEM', '7. VALIDASI REVIEWER']:
            self.assertIn(title, cover)
        self.assertIn('Tidak Sesuai', cover)
        detail = '\n'.join(p.extract_text() for p in pdf.pages[1:])
        for i in range(9): self.assertIn(f'BUKTI-LENGKAP-{i}', detail)

    def test_export_is_deterministic_for_the_same_saved_data(self):
        c = self.snapshot['cases'][0]
        self.assertEqual(export_pdf(c, 'snapshot'), export_pdf(c, 'snapshot'))

    def test_legacy_export_cannot_override_saved_score(self):
        from modules.export_generator import export_kkr_dr01_pdf
        c=self.snapshot['cases'][0]
        data=export_kkr_dr01_pdf({'sep':c['sep'],'kode_rs':c['kode_rs'],'knavp_skor':99999})
        text='\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages)
        self.assertNotIn('99999',text)
        self.assertIn(c['rekomendasi_laporan'],text)

if __name__=='__main__':unittest.main()
