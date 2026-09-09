"""
generate_from_md.py — Universal Markdown Generator
====================================================
AI Report Generation Framework V2
Kementerian Kesehatan RI / Pusat Pembiayaan Kesehatan

Membaca Final Approved Markdown dari Agent 5 dan menghasilkan:
  ├── DOCX  (python-docx)
  ├── PDF   (reportlab)
  ├── PNG Chart(s) (matplotlib)
  ├── TOC otomatis dari heading
  ├── Daftar Gambar (dari <!-- img_id: --> blocks)
  └── Daftar Tabel  (dari <!-- table_id: --> blocks)
"""

import os
import sys
import re
import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

APPROVED_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'approved')
DOCX_DIR     = os.path.join(BASE_DIR, 'exports', 'laporan_review_per_rs')
CHART_DIR    = os.path.join(BASE_DIR, 'exports', 'charts')

os.makedirs(DOCX_DIR,  exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHART GENERATOR (PNG)
# ─────────────────────────────────────────────────────────────────────────────

def generate_charts_from_md(md_text: str, kode_rs: str) -> dict:
    """
    Parse semua ```chart blocks dari Markdown dan render ke PNG.
    Return: dict {chart_id: file_path}
    """
    chart_paths = {}
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm

        # Cari semua chart blocks
        chart_blocks = re.findall(r'```chart\n(.*?)```', md_text, re.DOTALL)

        for block in chart_blocks:
            try:
                # Parse YAML-like content
                chart_data = {}
                lines = block.strip().split('\n')
                current_key = None
                list_values = []

                for line in lines:
                    if re.match(r'^[a-z_]+:', line):
                        if current_key and list_values:
                            chart_data[current_key] = list_values
                            list_values = []
                        key, _, val = line.partition(':')
                        val = val.strip()
                        current_key = key.strip()
                        if val:
                            chart_data[current_key] = val
                    elif line.strip().startswith('- ') and current_key:
                        list_values.append(line.strip()[2:].strip())

                if current_key and list_values:
                    chart_data[current_key] = list_values

                chart_id   = chart_data.get('id', f'chart_{kode_rs}_unknown')
                chart_type = chart_data.get('type', 'bar').lower()
                title      = chart_data.get('title', 'Chart')
                labels     = chart_data.get('labels', [])
                values_raw = chart_data.get('values', [])

                # Convert values to numbers
                values = []
                for v in values_raw:
                    try:
                        values.append(float(str(v).replace(',', '')))
                    except Exception:
                        values.append(0)

                if not labels or not values or len(labels) != len(values):
                    continue

                # Colors palette
                colors = ['#2563EB', '#7C3AED', '#059669', '#DC2626', '#D97706',
                          '#0891B2', '#BE185D', '#65A30D', '#9333EA', '#EA580C']

                fig, ax = plt.subplots(figsize=(6, 4))
                fig.patch.set_facecolor('#F8FAFC')
                ax.set_facecolor('#F8FAFC')

                if chart_type == 'pie':
                    # Filter zero values
                    filtered = [(l, v, colors[i % len(colors)])
                                for i, (l, v) in enumerate(zip(labels, values)) if v > 0]
                    if filtered:
                        fl, fv, fc = zip(*filtered)
                        wedges, texts, autotexts = ax.pie(
                            fv, labels=fl, colors=fc,
                            autopct='%1.1f%%', startangle=90,
                            pctdistance=0.8, labeldistance=1.1
                        )
                        for t in texts:
                            t.set_fontsize(9)
                        for t in autotexts:
                            t.set_fontsize(8)
                            t.set_color('white')
                            t.set_fontweight('bold')
                    ax.set_aspect('equal')

                elif chart_type == 'bar':
                    bar_colors = [colors[i % len(colors)] for i in range(len(labels))]
                    bars = ax.bar(range(len(labels)), values, color=bar_colors,
                                  edgecolor='white', linewidth=0.8)
                    ax.set_xticks(range(len(labels)))
                    ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
                    ax.set_ylabel('Jumlah', fontsize=9)
                    ax.grid(axis='y', alpha=0.3, linestyle='--')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    # Value labels on bars
                    for bar, val in zip(bars, values):
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                                f'{int(val):,}', ha='center', va='bottom', fontsize=8, fontweight='bold')

                ax.set_title(title, fontsize=11, fontweight='bold', pad=15, color='#1E293B')
                plt.tight_layout()

                # Simpan PNG
                chart_path = os.path.join(CHART_DIR, f'{chart_id}.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight',
                            facecolor=fig.get_facecolor())
                plt.close()
                chart_paths[chart_id] = {
                    'path': chart_path,
                    'labels': labels,
                    'values': values,
                    'title': title
                }

            except Exception as e:
                print(f"  [WARN] Chart block error: {e}")
                continue

    except ImportError:
        print("  [WARN] matplotlib tidak terinstall — chart tidak di-generate")

    return chart_paths


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN PARSER
# ─────────────────────────────────────────────────────────────────────────────

def parse_md_structure(md_text: str) -> dict:
    """Parse Markdown menjadi struktur terstruktur."""
    structure = {
        'headings': [],
        'tables': [],
        'charts': [],
        'figures': [],
        'paragraphs': [],
    }

    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        # Headings
        m = re.match(r'^(#{1,4})\s+(.+)', line)
        if m:
            level = len(m.group(1))
            text  = m.group(2).strip()
            structure['headings'].append({'level': level, 'text': text, 'line': i})

        # Tables
        if re.match(r'^<!-- table_id:', line):
            table_id = re.search(r'table_id:\s*(\S+)', line)
            if table_id:
                structure['tables'].append({'id': table_id.group(1), 'line': i})

        # Charts
        if re.match(r'^<!-- chart_id:|```chart', line):
            structure['charts'].append({'line': i})

        # Figures
        if re.match(r'^<!-- img_id:', line):
            fig_id = re.search(r'img_id:\s*(\S+)', line)
            if fig_id:
                structure['figures'].append({'id': fig_id.group(1), 'line': i})

    return structure


# ─────────────────────────────────────────────────────────────────────────────
# DOCX GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_docx(kode_rs: str, md_text: str, metadata: dict, chart_paths: dict) -> str:
    from generate_from_template import generate_docx as generate_consistent_docx
    return generate_consistent_docx(kode_rs, md_text, metadata, chart_paths)


def _generate_docx_legacy(kode_rs: str, md_text: str, metadata: dict, chart_paths: dict) -> str:
    """Generate DOCX dari approved Markdown."""
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn

    rs_name = metadata.get('_meta', {}).get('rs_name', kode_rs)
    doc = Document()

    # Setup styles — force Times New Roman 12pt hitam untuk semua style
    from docx.shared import RGBColor
    for style in doc.styles:
        try:
            if hasattr(style, 'font'):
                style.font.name = 'Times New Roman'
                style.font.size = Pt(12)
                style.font.color.rgb = RGBColor(0, 0, 0)
        except Exception:
            pass
    # Override Normal style secara eksplisit
    try:
        normal = doc.styles['Normal']
        normal.font.name = 'Times New Roman'
        normal.font.size = Pt(12)
        normal.font.color.rgb = RGBColor(0, 0, 0)
        from docx.oxml.ns import qn
        from lxml import etree
        rPr = normal.element.get_or_add_rPr()
        rFonts = rPr.get_or_add_rFonts()
        rFonts.set(qn('w:ascii'), 'Times New Roman')
        rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    except Exception:
        pass

    def set_normal_style(run):
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)

    def _add_formatted_runs(p, text):
        # Auto italicize common English terms if they are not already italicized
        en_terms = ['desk review', 'rule-based engine', 'expert review', 'on-site audit', 'sampling', 'medical evidence', 'unbundling', 'procedure validation', 'severity', 'mismatch', 'dual coding', 'false positive', 'compliance rate', 'executive summary']
        for term in en_terms:
            # Case insensitive replace but keep original casing, only if not already wrapped in *
            text = re.sub(rf'(?i)(?<!\*)(?<=\b)({term})(?=\b)(?!\*)', r'*\1*', text)
            
        # Parse bold and italic
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\[.*?\]\(.*?\))', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                run = p.add_run(part[2:-2])
                run.bold = True
                set_normal_style(run)
            elif part.startswith('*') and part.endswith('*'):
                run = p.add_run(part[1:-1])
                run.italic = True
                set_normal_style(run)
            elif part.startswith('[') and '](' in part and part.endswith(')'):
                # Simple link strip
                clean_text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', part)
                run = p.add_run(clean_text)
                set_normal_style(run)
            else:
                run = p.add_run(part)
                set_normal_style(run)

    def add_para(text, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_after=6, italic=False):
        if not text.strip():
            return
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.first_line_indent = Pt(24) if align == WD_ALIGN_PARAGRAPH.JUSTIFY else Pt(0)
        _add_formatted_runs(p, text)
        return p

    # Remove chart blocks and HTML comments from text before processing
    clean_text = re.sub(r'```chart.*?```', '', md_text, flags=re.DOTALL)
    clean_text = re.sub(r'<!--.*?-->', '', clean_text)
    clean_text = re.sub(r'```.*?```', '', clean_text, flags=re.DOTALL)
    # Filter TOC anchor links: [text](#anchor) -> hapus seluruh baris bullet TOC
    clean_text = re.sub(r'^\s*[•\-\*]?\s*\[[^\]]+\]\(#[^)]+\)\s*$', '', clean_text, flags=re.MULTILINE)
    # Filter DAFTAR ISI, DAFTAR TABEL, DAFTAR GAMBAR sections entirely
    clean_text = re.sub(
        r'#+\s*(DAFTAR ISI|DAFTAR TABEL|DAFTAR GAMBAR).*?(?=^#{1,2}\s|\Z)',
        '', clean_text, flags=re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    # Filter horizontal rules (--- or ***) yang menyebabkan baris kosong berlebih
    clean_text = re.sub(r'^\s*[-\*]{3,}\s*$', '', clean_text, flags=re.MULTILINE)
    # Collapse 3+ blank lines menjadi 1 blank line
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)

    # Title page
    doc.add_heading('LAPORAN HASIL DESK REVIEW AUDIT CODING', level=0)
    sub = doc.add_paragraph('Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)')
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].italic = True

    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.style = 'Table Grid'
    meta_rows = [
        ('Rumah Sakit',        f': {rs_name}'),
        ('Kode RS',            f': {kode_rs}'),
        ('Periode Data',       ': Januari – Desember 2025'),
        ('Tanggal Laporan',    ': 15 Juni 2026'),
        ('Nomor Laporan',      f': LHR-DR/2026/{kode_rs}'),
        ('Disusun oleh',       ': Tim Reviewer Koding — Pusat Pembiayaan Kesehatan, Kemenkes RI'),
    ]
    for i, (col1, col2) in enumerate(meta_rows):
        c0 = meta_table.rows[i].cells[0]
        c1 = meta_table.rows[i].cells[1]
        r0 = c0.paragraphs[0].add_run(col1)
        r1 = c1.paragraphs[0].add_run(col2)
        for r in [r0, r1]:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)

    # Note: Page break dihapus agar BAB I yang memiliki page_break_before tidak menghasilkan halaman kosong ganda

    # Embed charts
    embedded_charts = set()

    # Process Markdown content
    lines = clean_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Heading
        m = re.match(r'^(#{1,4})\s+(.+)', line)
        if m:
            level = min(len(m.group(1)), 4)
            text  = m.group(2).strip()
            # Skip TOC/list headings
            if text.upper() not in ('DAFTAR ISI', 'DAFTAR TABEL', 'DAFTAR GAMBAR'):
                h = doc.add_heading(text, level=level)
                for run in h.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(12)
                    run.font.color.rgb = RGBColor(0, 0, 0)
                if level == 1:
                    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    h.paragraph_format.page_break_before = True
            i += 1
            continue

        # Table row — skip raw MD tables (they were already processed)
        if line.startswith('|'):
            # Collect all table rows
            table_lines = []
            while i < len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i])
                i += 1
            if table_lines:
                _add_md_table_to_doc(doc, table_lines)
            continue

        # Bullet
        if line.startswith('- ') or re.match(r'^\s*[-*•]\s', line):
            text = re.sub(r'^\s*[-*•]\s+', '', line).strip()
            p = doc.add_paragraph(style='List Bullet')
            _add_formatted_runs(p, text)
            i += 1
            continue

        # Numbered list
        num_match = re.match(r'^\s*(\d+)\.\s+(.+)', line)
        if num_match:
            text = num_match.group(2).strip()
            try:
                p = doc.add_paragraph(style='List Number')
            except KeyError:
                p = doc.add_paragraph()
                p.paragraph_format.first_line_indent = Pt(-18)
                p.paragraph_format.left_indent = Pt(36)
                _add_formatted_runs(p, f"{num_match.group(1)}. {text}")
            else:
                _add_formatted_runs(p, text)
            i += 1
            continue

        # Normal paragraph
        if line.strip() and not line.startswith('#'):
            # Append lampiran reference to the end of BAB I
            if "dan konfirmasi langsung kepada tenaga koding serta klinisi di fasilitas pelayanan kesehatan yang bersangkutan." in line:
                line = line + " Rincian hasil temuan secara lengkap dapat merujuk pada bagian Lampiran (lihat Lampiran 1)."
            
            # Smart injection for specific topics per sentence
            def inject_per_sentence(text):
                if "(lihat lampiran" in text.lower(): return text
                
                sentences = text.split('. ')
                new_sentences = []
                for s in sentences:
                    lower_s = s.lower()
                    refs = []
                    if "distribusi temuan tersebut tersebar" in lower_s or "distribusi anomali per kategori" in lower_s:
                        refs.append("Lampiran 2")
                    if "medical evidence" in lower_s or "analisis mendalam terhadap temuan knavp" in lower_s:
                        refs.append("Lampiran 3")
                    if "prioritas tinggi ini memerlukan perhatian segera" in lower_s or ("prioritas tinggi" in lower_s and "prioritas sedang" in lower_s):
                        refs.append("Lampiran 4")
                    if "seluruh kasus sampel dikategorikan ke dalam tiga kelompok tindak lanjut" in lower_s or "rata-rata skor knavp" in lower_s:
                        refs.append("Lampiran 5")
                    if "tingkat diskrepansi dual coding sebesar" in lower_s or "diskrepansi antara koding ina-cbg dan idrg" in lower_s:
                        refs.append("Lampiran 1 dan Lampiran 6")
                    
                    if refs:
                        seen = set()
                        unique_refs = [x for x in refs if not (x in seen or seen.add(x))]
                        if len(unique_refs) == 1:
                            refs_str = unique_refs[0]
                        elif len(unique_refs) == 2:
                            refs_str = " dan ".join(unique_refs)
                        else:
                            refs_str = ", ".join(unique_refs[:-1]) + ", dan " + unique_refs[-1]
                        
                        s = s.rstrip('.') + f" *(lihat {refs_str})*"
                    new_sentences.append(s)
                
                res = '. '.join(new_sentences)
                if text.endswith('.') and not res.endswith('.'):
                    res += '.'
                return res
            
            line = inject_per_sentence(line)

            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.first_line_indent = Pt(24)
            _add_formatted_runs(p, line.strip())

        i += 1

    # ─── LAMPIRAN — Landscape Section (seperti audit_pipeline) ─────────────────
    # CATATAN: add_section() sudah otomatis mulai halaman baru di Word.
    # JANGAN tambah doc.add_page_break() sebelumnya karena akan buat halaman kosong.
    from docx.oxml.ns import qn as _qn
    from docx.enum.section import WD_ORIENT

    lamp_section = doc.add_section()
    lamp_section.orientation = WD_ORIENT.LANDSCAPE
    lamp_section.page_width   = int(11.69 * 914400)  # A4 landscape
    lamp_section.page_height  = int(8.27 * 914400)
    lamp_section.left_margin  = int(1.5 * 914400 / 2.54)
    lamp_section.right_margin = int(1.5 * 914400 / 2.54)
    lamp_section.top_margin   = int(2.0 * 914400 / 2.54)
    lamp_section.bottom_margin= int(2.0 * 914400 / 2.54)

    doc.add_heading('LAMPIRAN', level=1)

    # Ambil data dari metadata JSON (Agent 1)
    cases_list    = metadata.get('cases', [])
    knavp_detail  = metadata.get('knavp_rule_details', {})
    dual_coding   = metadata.get('dual_coding', {})
    priority_list = metadata.get('priority_cases', [])
    severity_cnt  = metadata.get('severity_counts', {})
    triase        = metadata.get('triase', {})
    total_sample  = metadata.get('total_sample', len(cases_list))
    total_alerts  = metadata.get('total_knavp_alerts', 0)
    avg_skor      = metadata.get('summary_stats', {}).get('avg_knavp_skor', 0)

    def lamp_para(text, bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, italic=False):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.name = 'Times New Roman'
        r.font.size = Pt(size)
        return p

    def lamp_table(headers, data_rows, header_font=9, data_font=8):
        tbl = doc.add_table(rows=1, cols=len(headers))
        tbl.style = 'Table Grid'
        for i, h in enumerate(headers):
            cell = tbl.rows[0].cells[i]
            cell.paragraphs[0].clear()
            r = cell.paragraphs[0].add_run(h)
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(header_font)
        for vals in data_rows:
            row = tbl.add_row().cells
            for ci, val in enumerate(vals):
                if ci < len(row):
                    row[ci].paragraphs[0].clear()
                    r = row[ci].paragraphs[0].add_run(str(val))
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(data_font)
        return tbl

    # ─── Lampiran 1: Ringkasan KKR-DR01 ─────────────────────────────────────────
    doc.add_heading('Lampiran 1. Ringkasan KKR-DR01 (Seluruh Kasus Sampel)', level=2)
    lamp_para('Tabel berikut menyajikan rekapitulasi seluruh kasus sampel beserta hasil validasi '
              'KNAVP, skor risiko, discrepancy dual coding, dan rekomendasi reviewer.')

    l1_headers = ['No', 'Nomor SEP', 'INA-CBG', 'iDRG', 'Skor KNAVP',
                  'Tingkat Risiko', 'Temuan KNAVP', 'Ketidak sesuaian Input', 'Keputusan']
    l1_rows = []
    for idx, c in enumerate(cases_list[:120]):
        rules = c.get('triggered_rules', [])
        l1_rows.append([
            str(idx + 1),
            str(c.get('sep', '')),
            str(c.get('inacbg', '-')),
            str(c.get('idrg_code', '-')),
            str(c.get('knavp_skor', 0)),
            str(c.get('tingkat_risiko', '-')),
            str(len(rules)),
            str(c.get('jumlah_beda_dual_coding', 0)),
            str(c.get('keputusan', '-')),
        ])
    lamp_table(l1_headers, l1_rows)
    lamp_para('')

    # ─── Lampiran 2: Rekapitulasi Hasil Validasi KNAVP ──────────────────────────
    doc.add_heading('Lampiran 2. Rekapitulasi Hasil Validasi KNAVP', level=2)
    lamp_para('Rekapitulasi berikut menggambarkan distribusi hasil validasi algoritma KNAVP '
              'terhadap seluruh kasus sampel yang direview.')

    onsite   = triase.get('onsite',   triase.get('onsite_count', 0))
    sampling = triase.get('sampling', triase.get('sampling_count', 0))
    monitor  = triase.get('monitor',  triase.get('monitoring_count', 0))
    mismatch = dual_coding.get('mismatch_count', dual_coding.get('cases_with_discrepancy', 0))
    mismatch_pct = dual_coding.get('mismatch_pct', dual_coding.get('mismatch_percentage', 0))

    recap_items = [
        ('Total Kasus Di-Review',                        str(total_sample)),
        ('Total Alert KNAVP',                            str(total_alerts)),
        ('Severity High',                                str(severity_cnt.get('High', 0))),
        ('Severity Medium',                              str(severity_cnt.get('Medium', 0))),
        ('Severity Low',                                 str(severity_cnt.get('Low', 0))),
        ('Rata-rata Skor KNAVP',                         str(avg_skor)),
        ('Rekomendasi Lanjut On-Site Audit',             str(onsite)),
        ('Rekomendasi Lanjut Audit Sampling',            str(sampling)),
        ('Rekomendasi Monitoring / Lolos',               str(monitor)),
        ('Kasus Mismatch Dual Coding (INA-CBG vs iDRG)', str(mismatch)),
        ('Persentase Mismatch Dual Coding',              str(mismatch_pct) + '%'),
    ]
    tbl2 = doc.add_table(rows=len(recap_items), cols=2)
    tbl2.style = 'Table Grid'
    for ri, (col1, col2) in enumerate(recap_items):
        cells = tbl2.rows[ri].cells
        for ci, val in enumerate([col1, col2]):
            cells[ci].paragraphs[0].clear()
            r = cells[ci].paragraphs[0].add_run(val)
            r.bold = (ci == 0)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
    lamp_para('')

    # ─── Lampiran 3: Detail Temuan KNAVP per Aturan ─────────────────────────────
    doc.add_page_break()
    doc.add_heading('Lampiran 3. Detail Hasil Audit KNAVP per Aturan', level=2)
    lamp_para('Tabel berikut menyajikan seluruh temuan KNAVP yang teridentifikasi pada sampel, '
              'dikelompokkan berdasarkan kategori aturan validasi koding.')

    CAT_LABELS = {
        'procedure_validation':      'Procedure Validation',
        'medical_evidence':          'Medical Evidence',
        'mutually_exclusive':        'Mutually Exclusive (Includes/Excludes)',
        'underlying_manifestation':  'Underlying & Manifestation',
        'unbundling':                'Unbundling',
        'administrative_validation': 'Administrative Validation',
        'age_validation':            'Age Validation',
        'los_validation':            'LOS Validation',
        'diagnosis_validation':      'Diagnosis Validation',
        'coding_standard':           'Coding Standard',
        'other':                     'Lainnya',
    }

    l3_headers = ['No', 'Kategori', 'Rule ID', 'Nama Aturan', 'Severity', 'Nomor SEP']
    l3_rows = []
    row_num = 1
    for cat_key, rules_list in knavp_detail.items():
        cat_label = CAT_LABELS.get(cat_key, cat_key)
        for rule in rules_list:
            l3_rows.append([
                str(row_num),
                cat_label,
                str(rule.get('rule_id', '-')),
                str(rule.get('nama_aturan', '-')),
                str(rule.get('severity', '-')),
                str(rule.get('sep', '-')),
            ])
            row_num += 1
    if l3_rows:
        lamp_table(l3_headers, l3_rows)
    else:
        lamp_para('Tidak terdapat temuan KNAVP pada kasus sampel.', italic=True if hasattr(lamp_para, '__code__') else False)
    lamp_para('')

    # ─── Lampiran 4: Kasus Prioritas (Tinggi -> Rendah) ─────────────────────────
    doc.add_page_break()
    doc.add_heading('Lampiran 4. Daftar Kasus Prioritas (Diurutkan Tinggi ke Rendah)', level=2)
    lamp_para('Kasus berikut diurutkan berdasarkan tingkat risiko (Tinggi → Sedang) dan skor '
              'KNAVP, serta direkomendasikan untuk tindak lanjut Sampling atau On-Site Audit.')

    l4_headers = ['No', 'Nomor SEP', 'INA-CBG', 'Skor KNAVP', 'Tingkat Risiko',
                  'Temuan KNAVP', 'Ketidak sesuaian Input', 'Rule Temuan', 'Rekomendasi']
    l4_rows = []
    for idx, c in enumerate(priority_list[:30]):
        rules = c.get('triggered_rules', [])
        rule_summary = '; '.join(
            [f"{r.get('rule_id', '')} - {r.get('nama_aturan', '')}" for r in rules[:3]]
        ) or '-'
        l4_rows.append([
            str(idx + 1),
            str(c.get('sep', '')),
            str(c.get('inacbg', '-')),
            str(c.get('knavp_skor', 0)),
            str(c.get('tingkat_risiko', '-')),
            str(c.get('triggered_rules_count', len(rules))),
            str(c.get('jumlah_beda_dc', c.get('jumlah_beda_dual_coding', 0))),
            rule_summary,
            str(c.get('keputusan', '-')),
        ])
    if l4_rows:
        lamp_table(l4_headers, l4_rows, header_font=8, data_font=7)
    lamp_para('')

    # ─── Lampiran 5: Dashboard Hasil Validasi ────────────────────────────────────
    doc.add_heading('Lampiran 5. Dashboard Hasil Validasi (Executive Summary KPI)', level=2)
    compliance_rate = round((monitor / total_sample * 100), 1) if total_sample else 0
    onsite_rate     = round((onsite / total_sample * 100), 1) if total_sample else 0
    risk_index      = round(avg_skor * 10, 1) if avg_skor <= 1 else round(avg_skor, 1)

    kpi_items = [
        f'Tingkat Kepatuhan Koding (Compliance Rate): {compliance_rate}% ({monitor} kasus lolos validasi tanpa temuan kritis)',
        f'Rasio Kasus Prioritas Onsite Audit: {onsite_rate}% ({onsite} kasus)',
        f'Rata-rata Indeks Risiko KNAVP: {avg_skor}',
    ]
    for item in kpi_items:
        lamp_para(f'\u25cf  {item}', size=11)

    lamp_para('Distribusi Status dan Rekomendasi Kasus:', bold=True, size=11)
    dist_items = [
        f'Monitoring / Lolos (Risiko Rendah): {monitor} Kasus ({round(monitor/total_sample*100,1) if total_sample else 0}%)',
        f'Audit Sampling / Klarifikasi (Risiko Sedang): {sampling} Kasus ({round(sampling/total_sample*100,1) if total_sample else 0}%)',
        f'On-Site Audit (Risiko Tinggi): {onsite} Kasus ({round(onsite/total_sample*100,1) if total_sample else 0}%)',
        f'TOTAL KASUS SAMPEL: {total_sample} Kasus (100%)',
    ]
    for item in dist_items:
        lamp_para(f'\u25cf  {item}', size=11)

    lamp_para('')

    # ─── Lampiran 6: Visualisasi Data ────────────────────────────────────────────
    if chart_paths:
        doc.add_page_break()
        doc.add_heading('Lampiran 6. Visualisasi Data', level=2)
        
        for chart_id, c_info in sorted(chart_paths.items()):
            chart_path = c_info['path']
            labels = c_info['labels']
            values = c_info['values']
            title = c_info.get('title', chart_id)
            # Fix any broken unicode dash characters
            title = title.replace('\ufffd', '-')
            if os.path.exists(chart_path):
                try:
                    suffix = chart_id.split('_')[-1]
                    lamp_para(f'Gambar {int(suffix)}. {title}', bold=True, size=10,
                              align=WD_ALIGN_PARAGRAPH.CENTER)
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run()
                    run.add_picture(chart_path, width=Inches(5.5))
                    lamp_para('')
                    
                    # OPSI 1: Tabel Data Mentah untuk kemudahan pembuatan Native Chart
                    lamp_para('Tabel Data Grafik (Sorot isi tabel ini lalu klik Insert > Chart di Word untuk membuat grafik yang bisa diedit):', italic=True, size=9)
                    tbl = doc.add_table(rows=1, cols=2)
                    tbl.style = 'Table Grid'
                    hdr_cells = tbl.rows[0].cells
                    hdr_cells[0].paragraphs[0].add_run('Kategori').bold = True
                    hdr_cells[1].paragraphs[0].add_run('Jumlah').bold = True
                    for i in range(len(labels)):
                        row_cells = tbl.add_row().cells
                        row_cells[0].text = str(labels[i])
                        
                        val = values[i]
                        if isinstance(val, float) and val.is_integer():
                            val_str = str(int(val))
                        else:
                            val_str = str(val)
                        row_cells[1].text = val_str
                        
                        # Fix font size for table cells
                        for cell in row_cells:
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    run.font.name = 'Times New Roman'
                                    run.font.size = Pt(9)
                    # Fix header font size
                    for cell in hdr_cells:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.name = 'Times New Roman'
                                run.font.size = Pt(9)
                                
                    lamp_para('')
                except Exception as e:
                    lamp_para(f'[Chart {chart_id} tidak dapat ditampilkan: {e}]')

    # Simpan DOCX
    fname    = f'LHR_V2_{kode_rs}_{rs_name.replace(" ", "_").replace(".", "")}.docx'
    out_path = os.path.join(DOCX_DIR, fname)
    doc.save(out_path)
    return out_path



def _add_md_table_to_doc(doc, table_lines: list):
    """Convert Markdown table rows to Word table."""
    from docx.shared import Pt

    # Filter out separator lines (|---|---|)
    data_lines = [l for l in table_lines if not re.match(r'^\|[\s\-:|]+\|$', l)]
    if not data_lines:
        return

    rows_data = []
    for line in data_lines:
        cells = [c.strip().strip('*') for c in line.strip('|').split('|')]
        rows_data.append(cells)

    if not rows_data:
        return

    max_cols = max(len(r) for r in rows_data)
    table = doc.add_table(rows=len(rows_data), cols=max_cols)
    table.style = 'Table Grid'

    for r_idx, row_data in enumerate(rows_data):
        for c_idx, cell_text in enumerate(row_data):
            if c_idx < max_cols:
                cell = table.rows[r_idx].cells[c_idx]
                p    = cell.paragraphs[0]
                p.clear()
                run  = p.add_run(cell_text)
                run.bold = (r_idx == 0)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def generate_all_outputs(kode_rs: str, approved_md: str = None, metadata: dict = None) -> dict:
    # Numeric narrative and chart images are generated together from saved review data.
    return {'docx': generate_docx(kode_rs, approved_md or '', metadata or {}, {}), 'charts': {}}


def _generate_all_outputs_legacy(kode_rs: str, approved_md: str = None, metadata: dict = None) -> dict:
    """
    Generate semua output dari approved Markdown.
    Return: dict {docx: path, charts: {id: path}}
    """
    outputs = {}

    # Load approved MD jika tidak diberikan
    if approved_md is None:
        approved_path = os.path.join(APPROVED_DIR, f'approved_{kode_rs}.md')
        if not os.path.exists(approved_path):
            print(f"  [ERROR] Approved MD tidak ditemukan: {approved_path}")
            return outputs
        with open(approved_path, 'r', encoding='utf-8') as f:
            approved_md = f.read()

    # Load metadata
    if metadata is None:
        meta_path = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'data_review', f'data_review_{kode_rs}.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}

    # 1. Generate PNG Charts
    print(f"  [GEN] Generating charts...")
    chart_paths = generate_charts_from_md(approved_md, kode_rs)
    outputs['charts'] = chart_paths
    print(f"  [GEN] {len(chart_paths)} chart(s) dihasilkan")

    # 2. Generate DOCX
    print(f"  [GEN] Generating DOCX...")
    try:
        docx_path = generate_docx(kode_rs, approved_md, metadata, chart_paths)
        outputs['docx'] = docx_path
        print(f"  [GEN] DOCX: {docx_path}")
    except Exception as e:
        print(f"  [ERROR] DOCX gagal: {e}")
        outputs['docx'] = None

    return outputs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate DOCX/PDF/PNG dari Approved Markdown')
    parser.add_argument('--kode_rs', type=str, default='1275655', help='Kode RS')
    args = parser.parse_args()

    print(f"\n[GENERATOR] RS: {args.kode_rs}")
    outputs = generate_all_outputs(args.kode_rs)
    print("\nOutput:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")
