import os
import re
import json
import argparse
import pickle
import shutil
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK

def set_normal_style(run):
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)

def format_rs_title(name):
    # Convert 'RS EKA HOSPITAL' to 'RS Eka Hospital'
    words = name.split()
    keep_upper = {'RS', 'RSU', 'RSUD', 'RSUP', 'RSIA', 'DR.', 'DR', 'PROF.', 'PROF', 'NTB', 'RSMDJ'}
    res = []
    for w in words:
        # Check if the word is an acronym or starts with an acronym (like DR.)
        if w.upper() in keep_upper:
            res.append(w.upper())
        elif '-' in w:
            res.append('-'.join([part.title() for part in w.split('-')]))
        else:
            res.append(w.title())
    return " ".join(res)

def _add_formatted_runs(p, text):
    en_terms = ['desk review', 'rule-based engine', 'expert review', 'on-site audit', 'sampling', 'medical evidence', 'unbundling', 'procedure validation', 'severity', 'mismatch', 'dual coding', 'false positive', 'compliance rate', 'executive summary']
    for term in en_terms:
        text = re.sub(rf'(?i)(?<!\*)(?<=\b)({term})(?=\b)(?!\*)', r'*\1*', text)
        
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
            clean_text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', part)
            run = p.add_run(clean_text)
            set_normal_style(run)
        else:
            run = p.add_run(part)
            set_normal_style(run)

def inject_per_sentence(text):
    if "(lihat lampiran" in text.lower(): return text
    sentences = text.split('. ')
    new_sentences = []
    for s in sentences:
        lower_s = s.lower()
        refs = []
        if "distribusi temuan tersebut tersebar" in lower_s or "distribusi anomali per kategori" in lower_s: refs.append("Lampiran 2")
        if "medical evidence" in lower_s or "analisis mendalam terhadap temuan knavp" in lower_s: refs.append("Lampiran 3")
        if "prioritas tinggi ini memerlukan perhatian segera" in lower_s or ("prioritas tinggi" in lower_s and "prioritas sedang" in lower_s): refs.append("Lampiran 4")
        if "seluruh kasus sampel dikategorikan ke dalam tiga kelompok tindak lanjut" in lower_s or "rata-rata skor knavp" in lower_s: refs.append("Lampiran 5")
        if "tingkat diskrepansi dual coding sebesar" in lower_s or "diskrepansi antara koding ina-cbg dan idrg" in lower_s: refs.append("Lampiran 1 dan Lampiran 6")
        
        if refs:
            seen = set()
            unique_refs = [x for x in refs if not (x in seen or seen.add(x))]
            if len(unique_refs) == 1: refs_str = unique_refs[0]
            elif len(unique_refs) == 2: refs_str = " dan ".join(unique_refs)
            else: refs_str = ", ".join(unique_refs[:-1]) + ", dan " + unique_refs[-1]
            s = s.rstrip('.') + f" *(lihat {refs_str})*"
        new_sentences.append(s)
    res = '. '.join(new_sentences)
    if text.endswith('.') and not res.endswith('.'): res += '.'
    return res

def parse_markdown_blocks(md_text):
    blocks = []
    lines = md_text.split('\n')
    i = 0
    in_toc = False
    while i < len(lines):
        line = lines[i]
        if '<!-- TOC_START -->' in line:
            in_toc = True
            i += 1
            continue
        if '<!-- TOC_END -->' in line:
            in_toc = False
            i += 1
            continue
        if in_toc:
            i += 1
            continue
            
        if line.startswith('```chart'):
            i += 1
            chart_block = []
            while i < len(lines) and not lines[i].startswith('```'):
                chart_block.append(lines[i])
                i += 1
            cdata = {'labels': [], 'values': []}
            c_lines = '\n'.join(chart_block).strip().split('\n')
            curr = None
            for cl in c_lines:
                if re.match(r'^[a-z_]+:', cl):
                    k, _, v = cl.partition(':')
                    curr = k.strip()
                    if v.strip():
                        cdata[curr] = v.strip()
                elif cl.strip().startswith('-') and curr:
                    val = cl.strip()[1:].strip()
                    if curr == 'values':
                        cdata[curr].append(float(val))
                    else:
                        cdata[curr].append(val)
            blocks.append({'type': 'chart', 'data': cdata})
        elif line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('#').strip()
            blocks.append({'type': 'header', 'level': level, 'content': header_text})
        elif line.strip() and not re.match(r'^[-*_]{3,}$', line.strip()):
            blocks.append({'type': 'text', 'content': line.strip()})
        i += 1
    return blocks

def generate_docx(kode_rs, md_text, metadata, chart_info):
    """Never reuse unversioned AI narrative/metadata for quantitative reporting."""
    from modules.report_data import load_snapshot
    from modules.report_word import write_report
    snapshot = load_snapshot()
    cases = [c for c in snapshot['cases'] if str(c['kode_rs']) == str(kode_rs)]
    if not cases:
        raise ValueError(f'Tidak ada review untuk RS {kode_rs}')
    clean_name = re.sub(r'[^A-Za-z0-9]', '_', format_rs_title(cases[0]['nama_rs']))
    out_path = os.path.join('exports', 'laporan_review_per_rs', f'LHR_V2_{kode_rs}_{clean_name}.docx')
    return write_report(cases, out_path, snapshot['snapshot_id'])


def _generate_docx_legacy(kode_rs, md_text, metadata, chart_info):
    from edit2docs import edit_chart
    OUTPUT_DIR = os.path.join('exports', 'laporan_review_per_rs')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rs_name = metadata.get('_meta', {}).get('rs_name', str(kode_rs))
    rs_name = format_rs_title(rs_name)
    clean_rs_name = re.sub(r'[^A-Za-z0-9]', '_', rs_name)
    out_path = os.path.join(OUTPUT_DIR, f"LHR_V2_{kode_rs}_{clean_rs_name}.docx")
    
    # 1. PREPARE TEXT BLOCKS
    blocks = parse_markdown_blocks(md_text)
    
    # Extract charts info
    chart_info = {}
    for b in blocks:
        if b['type'] == 'chart':
            c_id = b['data'].get('id', 'unknown')
            chart_info[c_id] = b['data']

    # Pre-process blocks to append Lampiran references inline at the end of sections
    current_section = None
    for b in blocks:
        if b['type'] == 'header':
            header_lower = b['content'].lower()
            if "gambaran data" in header_lower:
                current_section = 'gambaran'
            elif "hasil validasi knavp" in header_lower:
                current_section = 'knavp'
            elif "kasus prioritas" in header_lower:
                current_section = 'prioritas'
            else:
                current_section = None
        elif b['type'] == 'text':
            b['section'] = current_section

    ref_map = {
        'gambaran': '(Lihat Lampiran 1: KKR-DR01)',
        'knavp': '(Lihat Lampiran 2 dan Lampiran 3)',
        'prioritas': '(Lihat Lampiran 4)'
    }
    for sec, ref_text in ref_map.items():
        for i in range(len(blocks)-1, -1, -1):
            if blocks[i].get('type') == 'text' and blocks[i].get('section') == sec:
                content = blocks[i]['content']
                if content.endswith('.'):
                    blocks[i]['content'] = content[:-1] + f" {ref_text}."
                else:
                    blocks[i]['content'] = content + f" {ref_text}"
                break
    
    # 2. LOAD TEMPLATE
    shutil.copy('Template_Laporan_RS.docx', out_path)
    doc = Document(out_path)
    
    def iter_all_paragraphs(document):
        for p in document.paragraphs:
            yield p
        for t in document.tables:
            for r in t.rows:
                for c in r.cells:
                    for p in c.paragraphs:
                        yield p

    for p in iter_all_paragraphs(doc):
        if '{NAMA_RS}' in p.text:
            p.text = p.text.replace('{NAMA_RS}', rs_name)
        if '{KODE_RS}' in p.text:
            p.text = p.text.replace('{KODE_RS}', str(kode_rs))
            
        if '1275655' in p.text:
            if 'Gambar' in p.text or 'Grafik' in p.text:
                p.text = p.text.replace('1275655', rs_name)
            else:
                p.text = p.text.replace('1275655', str(kode_rs))
        if 'RSU H ADAM MALIK' in p.text:
            p.text = p.text.replace('RSU H ADAM MALIK', rs_name)

    # Inject KONTEN_LAPORAN (only in top-level paragraphs)
    for p in doc.paragraphs:
        if '{KONTEN_LAPORAN}' in p.text:
            p.text = '' # Clear placeholder
            for block in blocks:
                if block['type'] == 'header':
                    if block['content'].startswith('BAB ') and not block['content'].startswith('BAB I '):
                        pb_p = p.insert_paragraph_before('')
                        pb_p.add_run().add_break(WD_BREAK.PAGE)
                        
                    new_p = p.insert_paragraph_before('')
                    run = new_p.add_run(block['content'])
                    run.bold = True
                    run.font.name = 'Times New Roman'
                    if block['level'] == 1:
                        run.font.size = Pt(14)
                        new_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        run.font.size = Pt(12)
                elif block['type'] == 'text':
                    b_content = block['content']
                    if b_content.startswith('- ') or b_content.startswith('* '):
                        new_p = p.insert_paragraph_before('', style='List Bullet')
                        _add_formatted_runs(new_p, b_content[2:])
                        new_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    elif re.match(r'^\d+\.\s', b_content):
                        new_p = p.insert_paragraph_before('', style='List Number')
                        text_without_number = re.sub(r'^\d+\.\s', '', b_content)
                        _add_formatted_runs(new_p, text_without_number)
                        new_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    else:
                        new_p = p.insert_paragraph_before('')
                        _add_formatted_runs(new_p, b_content)
                        new_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        new_p.paragraph_format.first_line_indent = Inches(0.5)

    def clear_table_rows(table):
        for row in table.rows[1:]:
            table._tbl.remove(row._tr)

    # UPDATE STATIC TABLES IN THE TEMPLATE (Lampiran & Charts)
    try:
        cases = metadata.get('cases', [])
        
        # Load Diaglist and Proclist from SQLite for the current RS
        sep_to_diag = {}
        sep_to_proc = {}
        sep_to_desc_ina = {}
        sep_to_desc_idrg = {}
        sep_to_los = {}
        try:
            from modules.data_loader import get_sampled_cases_by_rs
            df_cases = get_sampled_cases_by_rs(kode_rs)
            if not df_cases.empty:
                sep_to_diag = dict(zip(df_cases['sep'], df_cases['diaglist']))
                sep_to_proc = dict(zip(df_cases['sep'], df_cases['proclist']))
                sep_to_desc_ina = dict(zip(df_cases['sep'], df_cases['deskripsi_inacbg']))
                sep_to_desc_idrg = dict(zip(df_cases['sep'], df_cases['deskripsi_idrg']))
                sep_to_los = dict(zip(df_cases['sep'], df_cases['alos']))
        except Exception as e:
            print("WARN: Could not load extra columns from DB:", e)

        def get_header_map(table):
            if not table.rows: return {}
            return {c.text.strip().lower(): i for i, c in enumerate(table.rows[0].cells)}

        def set_cells(cells, hmap, values):
            for k, v in values.items():
                if k in hmap:
                    cell = cells[hmap[k]]
                    cell.text = str(v)
                    f_size = 7 if k in ['diaglist', 'proclist', 'deskripsi ina-cbg', 'deskripsi inacbg', 'deskripsi idrg'] else 9
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.size = Pt(f_size)
                            run.font.name = 'Times New Roman'

        def clean_skor(skor):
            return int(skor) if skor == int(skor) else skor

        # Table 1: Lampiran 1 (Rekapitulasi Evaluasi Data)
        if len(doc.tables) > 1:
            t1 = doc.tables[1]
            hmap = get_header_map(t1)
            clear_table_rows(t1)
            for i, d in enumerate(cases, 1):
                row = t1.add_row()
                sep = d.get('sep', '')
                vals = {
                    'no': i,
                    'nomor sep': sep,
                    'ina-cbg': d.get('inacbg', ''),
                    'idrg': d.get('idrg_code', ''),
                    'skor knavp': clean_skor(d.get('knavp_skor', 0.0)),
                    'tingkat risiko': d.get('tingkat_risiko', ''),
                    'temuan knavp': len(d.get('triggered_rules', [])),
                    'ketidak sesuaian input': d.get('jumlah_beda_dual_coding', 0),
                    'keputusan': d.get('keputusan', ''),
                    'diaglist': sep_to_diag.get(sep, ''),
                    'proclist': sep_to_proc.get(sep, ''),
                    'deskripsi ina-cbg': sep_to_desc_ina.get(sep, ''),
                    'deskripsi inacbg': sep_to_desc_ina.get(sep, ''),
                    'deskripsi idrg': sep_to_desc_idrg.get(sep, ''),
                    'los': sep_to_los.get(sep, '')
                }
                set_cells(row.cells, hmap, vals)

        # Table 2: Lampiran 2 (Statistik Temuan KNAVP)
        if len(doc.tables) > 2:
            t2 = doc.tables[2]
            stats = metadata.get('knavp_validation', {})
            t2.cell(0, 1).text = str(metadata.get('total_sample', 120))
            t2.cell(1, 1).text = str(stats.get('total_alerts', 0))
            t2.cell(2, 1).text = str(stats.get('high_severity', 0))
            # Missing some rows if the template has them, let's just replace if row exists
            row_map = {
                'Total Kasus Di-Review': str(metadata.get('total_sample', 120)),
                'Total Alert KNAVP': str(stats.get('total_alerts', 0)),
                'Severity High': str(stats.get('high_severity', 0)),
                'Severity Medium': str(stats.get('medium_severity', 0)),
                'Severity Low': str(stats.get('low_severity', 0)),
                'Rata-rata Skor KNAVP': str(round(stats.get('avg_skor', 0), 2)),
                'Rekomendasi Lanjut On-Site Audit': str(metadata.get('triase', {}).get('onsite', 0)),
                'Rekomendasi Lanjut Audit Sampling': str(metadata.get('triase', {}).get('sampling', 0)),
                'Rekomendasi Monitoring / Lolos': str(metadata.get('triase', {}).get('lolos', 0)),
                'Kasus Mismatch Dual Coding (INA-CBG vs iDRG)': str(metadata.get('dual_coding', {}).get('mismatch_cases', 0)),
                'Persentase Mismatch Dual Coding': f"{metadata.get('dual_coding', {}).get('mismatch_percentage', 0)}%"
            }
            for row in t2.rows:
                key = row.cells[0].text.strip()
                if key in row_map:
                    row.cells[1].text = row_map[key]

        # Table 3: Lampiran 3 (Daftar Alert KNAVP)
        if len(doc.tables) > 3:
            t3 = doc.tables[3]
            hmap = get_header_map(t3)
            clear_table_rows(t3)
            idx = 1
            for case in cases:
                sep = case.get('sep', '')
                for rule in case.get('triggered_rules', []):
                    sev = rule.get('severity', '')
                    if sev in ['High', 'Medium']:
                        row = t3.add_row()
                        vals = {
                            'no': idx,
                            'kategori': rule.get('kelompok_rule', ''),
                            'rule id': rule.get('rule_id', ''),
                            'nama aturan': rule.get('nama_aturan', ''),
                            'severity': sev,
                            'nomor sep': sep,
                            'diaglist': sep_to_diag.get(sep, ''),
                            'proclist': sep_to_proc.get(sep, ''),
                            'deskripsi ina-cbg': sep_to_desc_ina.get(sep, ''),
                    'deskripsi inacbg': sep_to_desc_ina.get(sep, ''),
                            'deskripsi inacbg': sep_to_desc_ina.get(sep, ''),
                            'deskripsi idrg': sep_to_desc_idrg.get(sep, ''),
                            'los': sep_to_los.get(sep, '')
                        }
                        set_cells(row.cells, hmap, vals)
                        idx += 1

        # Table 4: Lampiran 4 (Daftar Kasus Prioritas)
        if len(doc.tables) > 4:
            t4 = doc.tables[4]
            hmap = get_header_map(t4)
            clear_table_rows(t4)
            pcases = metadata.get('priority_cases', [])
            for i, pcase in enumerate(pcases, 1):
                row = t4.add_row()
                sep = pcase.get('sep', '')
                vals = {
                    'no': i,
                    'nomor sep': sep,
                    'ina-cbg': pcase.get('inacbg', ''),
                    'skor knavp': clean_skor(pcase.get('knavp_skor', 0.0)),
                    'tingkat risiko': pcase.get('tingkat_risiko', ''),
                    'temuan knavp': len(pcase.get('triggered_rules', [])),
                    'ketidak sesuaian input': pcase.get('jumlah_beda_dc', pcase.get('jumlah_beda_dual_coding', 0)),
                    'rule temuan': ', '.join([r.get('nama_aturan', '') for r in pcase.get('triggered_rules', [])]),
                    'rekomendasi': pcase.get('keputusan', ''),
                    'diaglist': sep_to_diag.get(sep, ''),
                    'proclist': sep_to_proc.get(sep, ''),
                    'deskripsi ina-cbg': sep_to_desc_ina.get(sep, ''),
                    'deskripsi inacbg': sep_to_desc_ina.get(sep, ''),
                    'deskripsi idrg': sep_to_desc_idrg.get(sep, ''),
                    'los': sep_to_los.get(sep, '')
                }
                set_cells(row.cells, hmap, vals)

        # Chart Summary Tables (5 to 8)
        c_pop = f"chart_{kode_rs}_004"
        c_rek = f"chart_{kode_rs}_001"
        c_kat = f"chart_{kode_rs}_002"
        c_mis = f"chart_{kode_rs}_003"

        # 5: Populasi vs Sampel (c_pop)
        if len(doc.tables) > 5 and c_pop in chart_info:
            t5 = doc.tables[5]
            for row in t5.rows[1:]:
                k = row.cells[0].text.strip()
                if k in chart_info[c_pop]['labels']:
                    idx = chart_info[c_pop]['labels'].index(k)
                    row.cells[1].text = str(int(chart_info[c_pop]['values'][idx]))

        # 6: Rekomendasi (c_rek)
        if len(doc.tables) > 6 and c_rek in chart_info:
            t6 = doc.tables[6]
            for row in t6.rows[1:]:
                k = row.cells[0].text.strip()
                # Try partial match because chart labels might be slightly different
                for i, lab in enumerate(chart_info[c_rek]['labels']):
                    if k.lower() in lab.lower() or lab.lower() in k.lower():
                        row.cells[1].text = str(int(chart_info[c_rek]['values'][i]))
                        break

        # 7: Kategori Temuan (c_kat)
        if len(doc.tables) > 7 and c_kat in chart_info:
            t7 = doc.tables[7]
            for row in t7.rows[1:]:
                k = row.cells[0].text.strip()
                for i, lab in enumerate(chart_info[c_kat]['labels']):
                    if k.lower() in lab.lower() or lab.lower() in k.lower():
                        row.cells[1].text = str(int(chart_info[c_kat]['values'][i]))
                        break

        # 8: Mismatch (c_mis)
        if len(doc.tables) > 8 and c_mis in chart_info:
            t8 = doc.tables[8]
            for row in t8.rows[1:]:
                k = row.cells[0].text.strip()
                for i, lab in enumerate(chart_info[c_mis]['labels']):
                    if k.lower() in lab.lower() or lab.lower() in k.lower():
                        row.cells[1].text = str(int(chart_info[c_mis]['values'][i]))
                        break
    except Exception as e:
        print("WARN: Failed to update template tables:", e)

    doc.save(out_path)
    
    # 3. EDIT CHARTS USING edit2docs
    if chart_info:
        chart_edits = []
        mapping = {'002': 0, '001': 1, '004': 2, '003': 3}
        for c_id, c_data in chart_info.items():
            suffix = c_id.split('_')[-1]
            if suffix in mapping:
                chart_edits.append({
                    "chart": mapping[suffix],
                    "title": c_data.get('title', ''),
                    "categories": c_data['labels'],
                    "series": [{"name": "Jumlah", "values": c_data['values']}]
                })
        if chart_edits:
            edit_chart(out_path, chart_edits, output=out_path)
    
    print(f"  [GEN] DOCX (Template Native): {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kode_rs', required=True)
    args = parser.parse_args()

    md_path = os.path.join('exports', 'agent_outputs', 'approved', f"approved_{args.kode_rs}.md")
    if not os.path.exists(md_path):
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # User requested string replacement
    md_text = re.sub(r'(?i)Tim Auditor Pusat Pembiayaan Kesehatan', 'Tim Reviewer Pusat Pembiayaan Kesehatan', md_text)
    
    # Check charts for edits
    chart_info = {}
    blocks = parse_markdown_blocks(md_text)
    for b in blocks:
        if b['type'] == 'chart':
            c_id = b['data'].get('id', 'unknown')
            chart_info[c_id] = b['data']

    meta_path = os.path.join('exports', 'agent_outputs', 'data_review', f'data_review_{args.kode_rs}.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {}

    print(f"[TEMPLATE_GENERATOR] RS: {args.kode_rs}")
    generate_docx(args.kode_rs, md_text, metadata, chart_info)

if __name__ == '__main__':
    main()
