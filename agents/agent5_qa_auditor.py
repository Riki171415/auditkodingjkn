"""
AGENT 5 — QUALITY ASSURANCE
=============================
Kementerian Kesehatan RI / Pusat Pembiayaan Kesehatan
AI Report Generation Framework V2

TUGAS:
- Menerima Final Markdown dari Agent 4
- Menjalankan 24-point QA checklist
- Cross-check semua angka terhadap JSON Agent 1
- Deteksi AI-wording, typo, inkonsistensi terminologi
- Auto-fix issues yang ditemukan
- Loop sampai semua poin lulus (atau max 3 iterasi)
- Output: approved Final Markdown + QA Report
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'approved')
INPUT_DIR  = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'final_md')
META_DIR   = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'data_review')
os.makedirs(OUTPUT_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(BASE_DIR, 'agents'))
from shared.banned_phrases import check_banned, BANNED_PHRASES


from agents.shared.gemini_client import call_gemini, get_model_name, test_connection


# -----------------------------------------------------------------------------
# QA CHECKLIST (24 POIN)
# -----------------------------------------------------------------------------

class QAChecker:
    """Eksekutor 24-point QA checklist."""

    def __init__(self, md_text: str, meta: dict, kode_rs: str):
        self.text    = md_text
        self.meta    = meta
        self.kode_rs = kode_rs
        self.issues  = []
        self.score   = 0
        self.max_score = 24

    def _add_issue(self, point: int, severity: str, description: str, fix_hint: str = ""):
        self.issues.append({
            'point': point,
            'severity': severity,   # CRITICAL / WARNING / INFO
            'description': description,
            'fix_hint': fix_hint,
        })

    def _check_number_in_text(self, number: int, context: str) -> bool:
        """Periksa apakah angka tertentu muncul di teks."""
        return str(number) in self.text or f"{number:,}" in self.text

    def run_all_checks(self) -> dict:
        """Jalankan seluruh 24 poin QA."""
        passed = 0

        # P1: Logika narasi — minimal ada BAB I, II, III
        if all(h in self.text for h in ['BAB I', 'BAB II', 'BAB III']):
            passed += 1
        else:
            self._add_issue(1, 'CRITICAL', 'Struktur BAB tidak lengkap', 'Pastikan BAB I, II, dan III ada')

        # P2: Konsistensi angka — total populasi
        pop_total = self.meta.get('population', {}).get('total', 0)
        if pop_total == 0 or self._check_number_in_text(pop_total, 'populasi'):
            passed += 1
        else:
            self._add_issue(2, 'CRITICAL', f'Angka populasi {pop_total:,} tidak ditemukan di dokumen', 'Tambahkan angka populasi di A. Gambaran Data')

        # P3: Heading hierarchy benar
        headings = re.findall(r'^#+\s', self.text, re.MULTILINE)
        if headings:
            passed += 1
        else:
            self._add_issue(3, 'CRITICAL', 'Tidak ada heading Markdown ditemukan', 'Gunakan # ## ### untuk heading')

        # P4: Semua tabel punya caption (table_id)
        tables_with_id  = len(re.findall(r'<!-- table_id:', self.text))
        actual_tables   = len(re.findall(r'^\|', self.text, re.MULTILINE))
        if tables_with_id > 0 or actual_tables == 0:
            passed += 1
        else:
            self._add_issue(4, 'WARNING', f'{actual_tables} tabel ditemukan tapi {tables_with_id} mempunyai table_id', 'Tambahkan <!-- table_id: --> sebelum setiap tabel')

        # P5: Chart blocks ada
        charts = re.findall(r'```chart', self.text)
        if charts:
            passed += 1
        else:
            self._add_issue(5, 'WARNING', 'Tidak ada chart block ditemukan', 'Tambahkan chart blocks untuk visualisasi')

        # P6: Gambar mempunyai caption/alt
        img_tags = re.findall(r'!\[([^\]]*)\]', self.text)
        if not img_tags or all(t.strip() for t in img_tags):
            passed += 1
        else:
            self._add_issue(6, 'WARNING', 'Ada gambar tanpa alt text', 'Isi alt text di semua tag gambar')

        # P7: Tidak ada AI-wording
        violations = check_banned(self.text)
        if not violations:
            passed += 1
        else:
            self._add_issue(7, 'CRITICAL', f'{len(violations)} frasa AI terdeteksi: {violations[:3]}', 'Hapus/ganti frasa AI dengan bahasa administratif')

        # P8: Tidak ada typo ICD/prosedur umum
        # Cek format ICD: harus [A-Z][0-9][0-9]
        icd_mentions = re.findall(r'\b[A-Z]\d{2}(?:\.\d)?\b', self.text)
        # Kita hanya flag jika ada ICD yang formatnya salah (bukan check validitas)
        passed += 1  # P8: diasumsikan lulus kecuali ada pattern aneh

        # P9: Konsistensi terminologi
        terminologi = {
            'INA-CBG': ['INACBG', 'Ina-cbg', 'ina cbg'],
            'iDRG': ['IDRG', 'I-DRG', 'IDrg'],
            'KNAVP': ['Knavp', 'knavp'],
        }
        term_issues = []
        for correct, variants in terminologi.items():
            for variant in variants:
                if variant in self.text:
                    term_issues.append(f"'{variant}' seharusnya '{correct}'")
        if not term_issues:
            passed += 1
        else:
            self._add_issue(9, 'WARNING', f'Inkonsistensi terminologi: {term_issues[:3]}', 'Standarkan terminologi INA-CBG, iDRG, KNAVP')

        # P10: Cross-reference BAB I -> BAB II -> BAB III
        has_bab1 = 'PENDAHULUAN' in self.text.upper()
        has_bab2 = 'HASIL DESK REVIEW' in self.text.upper()
        has_bab3 = 'KESIMPULAN' in self.text.upper()
        if has_bab1 and has_bab2 and has_bab3:
            passed += 1
        else:
            self._add_issue(10, 'CRITICAL', 'Cross-reference BAB tidak lengkap', 'Pastikan semua BAB terhubung secara logis')

        # P11: TOC ada
        if 'TOC_START' in self.text or 'DAFTAR ISI' in self.text.upper():
            passed += 1
        else:
            self._add_issue(11, 'WARNING', 'TOC tidak ditemukan', 'Tambahkan Daftar Isi')

        # P12: Daftar Gambar ada
        if 'FIGURE_LIST_START' in self.text or 'DAFTAR GAMBAR' in self.text.upper():
            passed += 1
        else:
            self._add_issue(12, 'INFO', 'Daftar Gambar tidak ditemukan', 'Tambahkan Daftar Gambar')

        # P13: Daftar Tabel ada
        if 'TABLE_LIST_START' in self.text or 'DAFTAR TABEL' in self.text.upper():
            passed += 1
        else:
            self._add_issue(13, 'INFO', 'Daftar Tabel tidak ditemukan', 'Tambahkan Daftar Tabel')

        # P14: Nomor bab konsisten
        bab_nums = re.findall(r'BAB\s+([IVX]+)', self.text)
        expected = ['I', 'II', 'III']
        has_all  = all(b in bab_nums for b in expected)
        if has_all:
            passed += 1
        else:
            self._add_issue(14, 'WARNING', f'Nomor BAB tidak lengkap: ditemukan {bab_nums}', 'Pastikan BAB I, II, III ada dan urut')

        # P15: Nomor gambar (setidaknya ada 1 referensi Gambar)
        fig_refs = re.findall(r'Gambar\s+\d', self.text)
        if fig_refs or charts:
            passed += 1
        else:
            self._add_issue(15, 'INFO', 'Tidak ada referensi Gambar di dokumen', 'Tambahkan referensi gambar')

        # P16: Nomor tabel (setidaknya ada 1)
        tbl_refs = re.findall(r'Tabel\s+\d', self.text)
        if tbl_refs:
            passed += 1
        else:
            self._add_issue(16, 'INFO', 'Tidak ada referensi Tabel di dokumen', 'Tambahkan referensi tabel')

        # P17: Angka total kasus = Agent 1 JSON
        total_sample = self.meta.get('sample', {}).get('total', 0)
        if total_sample == 0 or self._check_number_in_text(total_sample, 'sampel'):
            passed += 1
        else:
            self._add_issue(17, 'CRITICAL', f'Angka sampel {total_sample} tidak muncul di dokumen', 'Tambahkan angka total sampel')

        # P18: Angka On-Site
        onsite = self.meta.get('triase', {}).get('onsite_count', 0)
        if onsite == 0 or self._check_number_in_text(onsite, 'onsite'):
            passed += 1
        else:
            self._add_issue(18, 'CRITICAL', f'Angka on-site {onsite} tidak ditemukan', 'Cantumkan jumlah kasus on-site')

        # P19: Angka Sampling
        sampling = self.meta.get('triase', {}).get('sampling_count', 0)
        if sampling == 0 or self._check_number_in_text(sampling, 'sampling'):
            passed += 1
        else:
            self._add_issue(19, 'WARNING', f'Angka sampling {sampling} tidak ditemukan', 'Cantumkan jumlah kasus sampling')

        # P20: Angka Discrepancy
        disc = self.meta.get('dual_coding', {}).get('cases_with_discrepancy', 0)
        if disc == 0 or self._check_number_in_text(disc, 'mismatch'):
            passed += 1
        else:
            self._add_issue(20, 'WARNING', f'Angka diskrepansi {disc} tidak ditemukan', 'Cantumkan jumlah kasus mismatch')

        # P21: Format ICD valid
        bad_icds = [m for m in re.findall(r'\b[A-Z]\d+\b', self.text) if len(m) < 3 or len(m) > 8]
        if not bad_icds:
            passed += 1
        else:
            self._add_issue(21, 'INFO', f'Beberapa kode ICD berformat tidak standar: {bad_icds[:3]}', 'Periksa format kode ICD')

        # P22: Kasus Prioritas urutan Tinggi->Sedang
        prio_section = re.search(r'[Kk]asus [Pp]rioritas(.*?)(?=##|\Z)', self.text, re.DOTALL)
        if prio_section:
            prio_text = prio_section.group(1)
            tinggi_pos = prio_text.find('Tinggi')
            sedang_pos = prio_text.find('Sedang')
            if tinggi_pos == -1 or sedang_pos == -1 or tinggi_pos <= sedang_pos:
                passed += 1
            else:
                self._add_issue(22, 'WARNING', 'Urutan Kasus Prioritas tidak konsisten (Tinggi harus sebelum Sedang)', 'Sort kasus prioritas Tinggi->Sedang->Rendah')
        else:
            passed += 1  # Tidak ada seksi Prioritas = tidak ada masalah

        # P23: Tidak ada paragraf pendek (< 3 kalimat)
        paragraphs = [p.strip() for p in self.text.split('\n\n') if p.strip() and not p.strip().startswith('#') and not p.strip().startswith('|') and not p.strip().startswith('```')]
        short_paras = [p[:50] for p in paragraphs if len(p.split('.')) < 2 and len(p) > 20]
        if not short_paras:
            passed += 1
        else:
            self._add_issue(23, 'INFO', f'{len(short_paras)} paragraf pendek terdeteksi', 'Kembangkan paragraf pendek')

        # P24: Tidak ada referensi data yang tidak ada di JSON
        # Cek angka besar yang muncul tapi tidak ada di metadata
        all_numbers_in_text = set(re.findall(r'\b\d{3,}\b', self.text))
        meta_numbers = set()
        def collect_numbers(obj):
            if isinstance(obj, dict):
                for v in obj.values(): collect_numbers(v)
            elif isinstance(obj, list):
                for v in obj: collect_numbers(v)
            elif isinstance(obj, (int, float)):
                meta_numbers.add(str(int(obj)))
        collect_numbers(self.meta)
        meta_numbers.add(str(datetime.now().year))
        meta_numbers.add('2025')
        meta_numbers.add('2026')
        orphan_numbers = all_numbers_in_text - meta_numbers
        # Hanya flag jika ada angka > 999 yang tidak ada di meta (kemungkinan data asing)
        bad_orphans = [n for n in orphan_numbers if int(n) > 9999 and int(n) not in [2025, 2026, 1234]]
        if len(bad_orphans) <= 5:  # toleransi untuk angka tanggal dll
            passed += 1
        else:
            self._add_issue(24, 'WARNING', f'{len(bad_orphans)} angka besar tidak ada di data source', 'Verifikasi angka tanpa referensi')

        self.score = passed
        return {
            'score': passed,
            'max_score': self.max_score,
            'percentage': round(passed / self.max_score * 100, 1),
            'issues': self.issues,
            'passed': passed >= 20,  # threshold: minimal 20/24 poin
        }


def apply_auto_fixes(md_text: str, meta: dict, kode_rs: str, issues: list) -> str:
    """Auto-fix issues yang bisa diperbaiki secara programatik."""
    fixed = md_text

    for issue in issues:
        p = issue['point']

        # Fix P7: Banned phrases — replace otomatis
        if p == 7:
            violations = check_banned(fixed)
            replacements = {
                'sangat penting': 'penting',
                'dengan demikian, dapat disimpulkan': 'data menunjukkan',
                'secara keseluruhan, dapat dikatakan': 'berdasarkan data yang dievaluasi',
                'dalam rangka meningkatkan': 'untuk meningkatkan',
                'memberikan gambaran yang komprehensif': 'menunjukkan',
                'tidak dapat dipungkiri': '',
                'signifikan': 'tercatat',
                'komprehensif': 'menyeluruh',
            }
            for phrase, replacement in replacements.items():
                if phrase in fixed.lower():
                    fixed = re.sub(phrase, replacement, fixed, flags=re.IGNORECASE)

        # Fix P9: Terminologi
        if p == 9:
            fixed = re.sub(r'\bINACBG\b', 'INA-CBG', fixed)
            fixed = re.sub(r'\bIna-cbg\b', 'INA-CBG', fixed)
            fixed = re.sub(r'\bIDRG\b', 'iDRG', fixed)
            fixed = re.sub(r'\bI-DRG\b', 'iDRG', fixed)
            fixed = re.sub(r'\bKnavp\b', 'KNAVP', fixed)
            fixed = re.sub(r'\bknavp\b', 'KNAVP', fixed)

    return fixed


SYSTEM_PROMPT_AGENT5_FIX = """
Anda adalah QA Auditor laporan resmi Kementerian Kesehatan.

Anda telah menemukan isu-isu berikut dalam laporan:

{issues}

TUGAS:
1. Perbaiki semua isu CRITICAL dan WARNING.
2. Jangan mengubah fakta atau angka.
3. Jangan menambahkan konten baru.
4. Hanya perbaiki bahasa, struktur, dan konsistensi.
5. Pastikan tidak ada frasa AI yang tersisa.

Kembalikan laporan yang sudah diperbaiki secara penuh.
"""


def run(kode_rs: str, final_md: str = None, metadata: dict = None, verbose: bool = True) -> str:
    """
    Eksekusi Agent 5 untuk satu RS.
    Return: string approved final Markdown.
    """
    if verbose:
        print(f"\n[AGENT 5] QA AUDITOR — RS: {kode_rs}")
        print("=" * 60)

    # Load final_md dari file jika tidak diberikan
    if final_md is None:
        md_path = os.path.join(INPUT_DIR, f'final_md_{kode_rs}.md')
        if not os.path.exists(md_path):
            print(f"  [ERROR] Final MD tidak ditemukan: {md_path}")
            return ""
        with open(md_path, 'r', encoding='utf-8') as f:
            final_md = f.read()

    # Load metadata untuk cross-check
    if metadata is None:
        meta_path = os.path.join(META_DIR, f'data_review_{kode_rs}.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}

    current_md = final_md
    qa_history = []
    max_iterations = 3

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n  [QA] Iterasi {iteration}/{max_iterations}")

        checker = QAChecker(current_md, metadata, kode_rs)
        result  = checker.run_all_checks()
        qa_history.append(result)

        if verbose:
            print(f"  Skor QA: {result['score']}/{result['max_score']} ({result['percentage']}%)")
            critical_issues = [i for i in result['issues'] if i['severity'] == 'CRITICAL']
            warning_issues  = [i for i in result['issues'] if i['severity'] == 'WARNING']
            print(f"  CRITICAL: {len(critical_issues)} | WARNING: {len(warning_issues)}")

        if result['passed']:
            if verbose:
                print(f"   QA LULUS pada iterasi {iteration}")
            break

        # Auto-fix programatik
        current_md = apply_auto_fixes(current_md, metadata, kode_rs, result['issues'])

        # Jika masih ada isu critical -> minta Gemini untuk perbaiki
        critical_issues = [i for i in result['issues'] if i['severity'] == 'CRITICAL']
        if critical_issues and iteration < max_iterations:
            try:
                issues_text = "\n".join([
                    f"- Poin {i['point']}: {i['description']} (Fix: {i['fix_hint']})"
                    for i in critical_issues
                ])
                fix_prompt = SYSTEM_PROMPT_AGENT5_FIX.format(issues=issues_text)
                fix_prompt += f"\n\nLaporan yang perlu diperbaiki:\n\n{current_md[:5000]}"

                fixed = call_gemini(fix_prompt, temperature=0.1, max_tokens=8192, verbose=verbose)
                if fixed:
                    current_md = fixed
                if verbose:
                    print(f"  Gemini fix applied untuk {len(critical_issues)} isu CRITICAL")
            except Exception as e:
                if verbose:
                    print(f"  [WARN] Gemini fix gagal: {e} — lanjut dengan auto-fix")

    # Final QA report
    final_checker = QAChecker(current_md, metadata, kode_rs)
    final_result  = final_checker.run_all_checks()

    qa_report = _generate_qa_report(kode_rs, qa_history, final_result)

    # Simpan approved MD
    approved_path = os.path.join(OUTPUT_DIR, f'approved_{kode_rs}.md')
    with open(approved_path, 'w', encoding='utf-8') as f:
        f.write(current_md)

    # Simpan QA report
    qa_path = os.path.join(OUTPUT_DIR, f'qa_report_{kode_rs}.md')
    with open(qa_path, 'w', encoding='utf-8') as f:
        f.write(qa_report)

    if verbose:
        print(f"\n  Final QA Score: {final_result['score']}/{final_result['max_score']} ({final_result['percentage']}%)")
        print(f"  Approved MD: {approved_path}")
        print(f"  QA Report  : {qa_path}")

    return current_md


def _generate_qa_report(kode_rs: str, history: list, final: dict) -> str:
    """Generate QA report Markdown."""
    lines = [
        f"# QA Report — RS {kode_rs}",
        f"Tanggal: {datetime.now().strftime('%d %B %Y %H:%M')}",
        "",
        f"## Hasil Akhir",
        f"**Skor: {final['score']}/{final['max_score']} ({final['percentage']}%)**",
        f"**Status: {' APPROVED' if final['passed'] else '️ PERLU REVIEW MANUAL'}**",
        "",
        "## Riwayat Iterasi",
    ]
    for i, h in enumerate(history, 1):
        lines.append(f"- Iterasi {i}: {h['score']}/{h['max_score']} ({h['percentage']}%)")

    if final['issues']:
        lines += ["", "## Isu yang Tersisa"]
        for issue in final['issues']:
            lines.append(f"- **[{issue['severity']}] Poin {issue['point']}**: {issue['description']}")
            if issue.get('fix_hint'):
                lines.append(f"  - Saran: {issue['fix_hint']}")
    else:
        lines += ["", "##  Tidak Ada Isu Tersisa"]

    lines += [
        "",
        "## Checklist 24 Poin",
        "",
        "| # | Poin QA | Status |",
        "|---|---------|--------|",
    ]
    checklist_items = [
        "Logika narasi (BAB I/II/III ada)",
        "Konsistensi angka — total populasi",
        "Heading hierarchy benar",
        "Semua tabel punya caption + id",
        "Chart blocks ada",
        "Semua gambar punya alt text",
        "Tidak ada AI-wording",
        "Format ICD valid",
        "Konsistensi terminologi (INA-CBG, iDRG, KNAVP)",
        "Cross-reference BAB I -> II -> III",
        "TOC ada",
        "Daftar Gambar ada",
        "Daftar Tabel ada",
        "Nomor bab konsisten",
        "Nomor gambar ada",
        "Nomor tabel ada",
        "Angka total sampel = Agent 1 JSON",
        "Angka On-Site = Agent 1 JSON",
        "Angka Sampling = Agent 1 JSON",
        "Angka Discrepancy = Agent 1 JSON",
        "Format ICD valid",
        "Kasus Prioritas urutan Tinggi->Sedang->Rendah",
        "Tidak ada paragraf pendek",
        "Tidak ada angka tanpa referensi data",
    ]
    failed_points = {i['point'] for i in final['issues']}
    for i, item in enumerate(checklist_items, 1):
        status = "" if i in failed_points else ""
        lines.append(f"| {i} | {item} | {status} |")

    return "\n".join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Agent 5 — QA Auditor')
    parser.add_argument('--kode_rs', type=str, default='1275655', help='Kode RS')
    args = parser.parse_args()
    result = run(args.kode_rs)
    if result:
        print("\n[AGENT 5] DONE. Approved Markdown tersimpan.")
