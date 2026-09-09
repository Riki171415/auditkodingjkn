"""Deterministic Word reports using the retained report template and snapshot."""
from collections import Counter
from copy import deepcopy
from datetime import date
from pathlib import Path
import io

from docx import Document
from docx.shared import Pt, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

from modules.report_data import ONSITE, SAMPLING, MONITORING, UNKNOWN, summarize

BASE = Path(__file__).resolve().parents[1]

def _replace_rows(table, rows, header=True):
    prototype = deepcopy(table.rows[-1]._tr)
    for row in list(table.rows)[1 if header else 0:]:
        table._tbl.remove(row._tr)
    for values in rows:
        table._tbl.append(deepcopy(prototype))
        for cell, value in zip(table.rows[-1].cells, values):
            cell.text = str(value if value is not None else '')
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(8 if len(values) > 3 else 10)
        # Allow long rows to flow rather than clipping inherited fixed heights.
        for height in table.rows[-1]._tr.xpath('./w:trPr/w:trHeight'):
            height.getparent().remove(height)
            

    if header:
        pr = table.rows[0]._tr.get_or_add_trPr()
        repeat = OxmlElement('w:tblHeader')
        pr.append(repeat)

def _title_case_rs(name):
    """Convert RS name to Title Case matching LHR_V2 convention."""
    keep_upper = {'RS', 'RSU', 'RSUD', 'RSUP', 'RSIA', 'DR.', 'DR', 'PROF.', 'PROF',
                  'NTB', 'H.', 'H', 'RI', 'PKU', 'EMC', 'PHC', 'LHR', 'UGM'}
    words = str(name).split()
    result = []
    for w in words:
        if w.upper() in keep_upper or w.upper().rstrip('.') in keep_upper:
            result.append(w.upper())
        elif '-' in w:
            result.append('-'.join(p.title() for p in w.split('-')))
        else:
            result.append(w.title())
    return ' '.join(result)


def _number(value):
    return f'{value:,}'.replace(',', '.')


def write_report(cases, path, snapshot_id, hospitals=None):
    """National appendix aggregates every RS; per-RS appendix lists every case."""
    national = hospitals is not None
    stats = summarize(cases)
    code = 'NASIONAL' if national else str(cases[0]['kode_rs'])
    raw_name = f'Nasional ({len(hospitals)} RS)' if national else cases[0]['nama_rs']
    # Use Title Case for RS name on cover (matching LHR_V2 convention)
    name = raw_name if national else _title_case_rs(raw_name)
    doc = Document(BASE / 'Template_Laporan_RS.docx')
    cover = [
        name, code, 'Januari \u2013 Desember 2025', '15 Juni 2026',
        f'LHR-DR/2026/{code}',
        'Tim Reviewer Koding \u2014 Pusat Pembiayaan Kesehatan, Kemenkes RI'
    ]
    for row, value in zip(doc.tables[0].rows, cover):
        row.cells[1].text = ': ' + value
    doc.core_properties.comments = f'Kontrak saved-review-v1; snapshot SHA256 {snapshot_id}'
    update_fields = doc.settings.element.find(qn('w:updateFields'))
    if update_fields is None:
        update_fields = OxmlElement('w:updateFields')
        doc.settings.element.append(update_fields)
    update_fields.set(qn('w:val'), 'true')

    # Replace all old chart drawings, including their editable stale data links.
    chart_paragraphs = []
    for p in doc.paragraphs:
        if p._p.xpath('.//c:chart'):
            chart_paragraphs.append(p)
            for run in list(p._p):
                if run.tag != qn('w:pPr'):
                    p._p.remove(run)
    for rid, rel in list(doc.part.rels.items()):
        if rel.reltype.endswith('/chart'):
            doc.part.drop_rel(rid)

    placeholder = next(p for p in doc.paragraphs if '{KONTEN_LAPORAN}' in p.text)
    
    # Historical Markdown narratives contain independently calculated totals and
    # must never be mixed with the immutable reporting snapshot.  Keep their
    # files for traceability, but build every published narrative from `stats`.
    md_path = BASE / 'exports' / 'agent_outputs' / 'final_md' / (f'final_md_{code}.md' if not national else 'final_md_nasional.md')
    blocks = []
    chart_info = {}
    
    if md_path.exists():
        import re
        md_text = md_path.read_text(encoding='utf-8')
        
        # FIX AI HALLUCINATIONS/STALE DATA IN NARRATIVE TEXT:
        if not national:
            # Triase Results
            md_text = re.sub(r'Pertama, sejumlah \d+ kasus direkomendasikan untuk On-Site Audit', f'Pertama, sejumlah {stats["onsite"]} kasus direkomendasikan untuk On-Site Audit', md_text, flags=re.IGNORECASE)
            md_text = re.sub(r'Kedua, sebanyak \d+ kasus direkomendasikan untuk Audit Sampling', f'Kedua, sebanyak {stats["sampling"]} kasus direkomendasikan untuk Audit Sampling', md_text, flags=re.IGNORECASE)
            md_text = re.sub(r'Ketiga, sejumlah \d+ kasus dinyatakan dapat masuk dalam kategori Monitoring', f'Ketiga, sejumlah {stats["monitoring"]} kasus dinyatakan dapat masuk dalam kategori Monitoring', md_text, flags=re.IGNORECASE)
            md_text = re.sub(r'Rata-rata skor KNAVP dari seluruh kasus sampel adalah [\d,]+', f'Rata-rata skor KNAVP dari seluruh kasus sampel adalah {stats["avg_score"]:.2f}'.replace('.', ','), md_text, flags=re.IGNORECASE)
            
            # Rekomendasi
            md_text = re.sub(r'Tidak diperlukan tindak lanjut segera bagi \d+ kasus', f'Tidak diperlukan tindak lanjut segera bagi {stats["monitoring"]} kasus', md_text, flags=re.IGNORECASE)
            md_text = re.sub(r'Pelaksanaan klarifikasi dan audit sampling terhadap \d+ kasus', f'Pelaksanaan klarifikasi dan audit sampling terhadap {stats["sampling"]} kasus', md_text, flags=re.IGNORECASE)
            md_text = re.sub(r'Pelaksanaan on-site audit terhadap \d+ kasus', f'Pelaksanaan on-site audit terhadap {stats["onsite"]} kasus', md_text, flags=re.IGNORECASE)
            
            # Other Stats
            md_text = re.sub(r'sistem berhasil mengidentifikasi \d+ kasus yang memiliki setidaknya satu indikasi', f'sistem berhasil mengidentifikasi {stats["cases_with_alerts"]} kasus yang memiliki setidaknya satu indikasi', md_text, flags=re.IGNORECASE)
            md_text = re.sub(r'sistem validasi mendeteksi \d+ indikasi ketidaksesuaian koding', f'sistem validasi mendeteksi {stats["alerts"]} indikasi ketidaksesuaian koding', md_text, flags=re.IGNORECASE)
            md_text = re.sub(r'terbagi atas \d+ kasus dengan severity tinggi \(High\), \d+ kasus dengan severity sedang \(Medium\), dan \d+ kasus dengan severity rendah \(Low\)', f'terbagi atas {stats["severity"].get("High", 0)} kasus dengan severity tinggi (High), {stats["severity"].get("Medium", 0)} kasus dengan severity sedang (Medium), dan {stats["severity"].get("Low", 0)} kasus dengan severity rendah (Low)', md_text, flags=re.IGNORECASE)
            
        # National report replacements
        if national:
            md_text = re.sub(r'teridentifikasinya \d+ kasus klaim yang direkomendasikan secara tegas untuk dilakukan \*On-Site Audit\*', f'teridentifikasinya {stats["onsite"]} kasus klaim yang direkomendasikan secara tegas untuk dilakukan *On-Site Audit*', md_text)
            md_text = re.sub(r'keberadaan \d+ kasus \*Audit Sampling\* dan \d+ kasus \*On-Site Audit\*', f'keberadaan {stats["sampling"]} kasus *Audit Sampling* dan {stats["onsite"]} kasus *On-Site Audit*', md_text)
            md_text = re.sub(r'sebanyak \d+ kasus terbukti Lolos/Monitoring, namun ditemukan \d+ kasus yang memerlukan \*Audit Sampling\* serta \d+ kasus berdampak tinggi yang direkomendasikan untuk tindakan penelusuran \*On-Site Audit\*', f'sebanyak {stats["monitoring"]} kasus terbukti Lolos/Monitoring, namun ditemukan {stats["sampling"]} kasus yang memerlukan *Audit Sampling* serta {stats["onsite"]} kasus berdampak tinggi yang direkomendasikan untuk tindakan penelusuran *On-Site Audit*', md_text)
            md_text = re.sub(r'mengidentifikasi sebanyak \d+ kasus diskrepansi \*dual coding\*', f'mengidentifikasi sebanyak {stats["dc_cases"]} kasus diskrepansi *dual coding*', md_text)
            md_text = re.sub(r'Temuan \d+ kasus diskrepansi ini', f'Temuan {stats["dc_cases"]} kasus diskrepansi ini', md_text)

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
                
            if line.startswith('```'):
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    i += 1
            elif line.startswith('#'):
                header_text = line.lstrip('#').strip()
                blocks.append((header_text, True))
            elif line.strip() and not re.match(r'^[-*_]{3,}$', line.strip()):
                content = line.strip()
                # Basic markdown bold/italic removal for Word
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                content = re.sub(r'\*(.*?)\*', r'\1', content)
                blocks.append((content, False))
            i += 1
    else:
        # Fallback to standard hardcoded summary
        blocks = [
            ('BAB I PENDAHULUAN', True),
            ('A. Latar Belakang dan Ruang Lingkup', True),
            (f'Laporan ini menyajikan hasil desk review yang tersimpan untuk {name}, sebanyak {_number(stats["total"])} kasus. Cakupan nasional adalah gabungan seluruh kasus pada laporan per RS. Penyeragaman laporan tidak mengubah data klinis, skor, temuan aturan, atau keputusan reviewer pada database.', False),
            ('B. Dasar Penyusunan dan Definisi Indikator', True),
            ('Sumber: kertas kerja KKR-DR01 pada audit.db yang dipasangkan dengan data kasus pada data.db menggunakan Kode RS dan Nomor SEP. Rekomendasi laporan dinormalisasi dari keputusan sistem tersimpan; jika kosong, hanya keputusan tindak lanjut reviewer yang eksplisit dipakai. Keputusan validitas reviewer tetap disajikan terpisah dalam Excel. Tidak dilakukan penilaian ulang klinis.', False),
            ('Monitoring menggabungkan label monitoring dan tidak perlu tindak lanjut. Kategori ini bukan bukti kepatuhan klinis atau ketiadaan kesalahan. Perbedaan dual coding menggunakan jumlah perbedaan yang tersimpan pada KKR, bukan ketidaksamaan kode grup INA-CBG dengan iDRG. Skor KNAVP dasar, tingkat risiko tersimpan, dan rekomendasi adalah indikator berbeda; laporan tidak menerapkan ambang baru.', False),
            ('BAB II HASIL DESK REVIEW', True),
            ('A. Gambaran Data dan Rekomendasi', True),
            (f'Dari {_number(stats["total"])} kasus: {_number(stats["onsite"])} direkomendasikan On-Site Audit, {_number(stats["sampling"])} Sampling/Klarifikasi, {_number(stats["monitoring"])} Monitoring/tidak perlu tindak lanjut, dan {_number(stats["unknown"])} belum memiliki rekomendasi yang dapat diklasifikasikan. Jumlah seluruh kategori sama dengan total kasus.', False),
            ('B. Hasil Validasi KNAVP', True),
            (f'Terdapat {_number(stats["alerts"])} temuan aturan pada {_number(stats["cases_with_alerts"])} kasus. Satu kasus dapat memiliki lebih dari satu temuan. Rata-rata skor KNAVP dasar adalah {stats["avg_score"]:.2f}; rata-rata nasional dihitung dari seluruh skor kasus, bukan rata-rata sederhana antar-RS.', False),
            ('C. Dual Coding dan Kasus Prioritas', True),
            (f'Sebanyak {_number(stats["dc_cases"])} kasus memiliki perbedaan dual coding tersimpan, dengan {_number(stats["dc_total"])} perbedaan secara keseluruhan. Jumlah kasus berbeda dengan jumlah perbedaan. Daftar prioritas mencakup {_number(stats["onsite"] + stats["sampling"])} kasus dengan rekomendasi On-Site atau Sampling.', False),
            ('BAB III KESIMPULAN DAN REKOMENDASI', True),
            ('A. Kesimpulan', True),
            (f'Ringkasan, daftar kasus, dan grafik laporan ini menggunakan snapshot yang sama dengan Excel. Distribusi tindak lanjut adalah {stats["onsite"]} On-Site, {stats["sampling"]} Sampling, {stats["monitoring"]} Monitoring, dan {stats["unknown"]} belum terklasifikasi. Temuan sistem merupakan bahan tindak lanjut dan tidak dengan sendirinya membuktikan fraud atau kerugian.', False),
            ('B. Rekomendasi', True),
            ('Tindak lanjuti kasus sesuai rekomendasi yang tersimpan, konfirmasikan bukti pendukung melalui reviewer, dan dokumentasikan perubahan keputusan di kertas kerja sebelum menerbitkan ulang seluruh laporan.', False),
        ]

    for text, heading in blocks:
        p = placeholder.insert_paragraph_before(text)
        p.paragraph_format.space_after = Pt(6)
        if text.startswith('BAB '):
            p.paragraph_format.page_break_before = True
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.bold = heading
            
        # INJECT THE PRIORITY CASES TABLE RIGHT AFTER THE HEADER
        if heading and ('D. Kasus Prioritas' in text or 'C. Dual Coding' in text or 'C. Analisis Diskrepansi Dual Coding' in text):
            # Calculate priority cases specifically for this table
            table_priority = sorted(
                [c for c in cases if c['jumlah_beda_dual_coding'] > 0 or len(c['triggered_rules']) > 0],
                key=lambda c: (c['rekomendasi_laporan'] != ONSITE, c['rekomendasi_laporan'] != SAMPLING, -c['knavp_skor'], str(c['sep']))
            )
            
            # Create a 5-column table at the end of the doc
            new_tbl = doc.add_table(rows=1, cols=5)
            new_tbl.style = 'Table Grid'
            new_tbl.autofit = False
            new_tbl.allow_autofit = False
            
            widths = [Inches(0.4), Inches(1.5), Inches(2.2), Inches(1.0), Inches(1.4)]
            for idx, col in enumerate(new_tbl.columns):
                col.width = widths[idx]
                
            hdr_cells = new_tbl.rows[0].cells
            for idx, th in enumerate(["No", "Nomor SEP", "Rule", "Prioritas", "Rekomendasi"]):
                hdr_cells[idx].text = th
                hdr_cells[idx].width = widths[idx]
                for run in hdr_cells[idx].paragraphs[0].runs:
                    run.font.bold = True
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(10)
            
            for idx, c in enumerate(table_priority[:10], 1):
                row_cells = new_tbl.add_row().cells
                row_cells[0].text = str(idx)
                sep_text = c['sep'] + (f"\n[RS: {c.get('kode_rs')}]" if national else "")
                row_cells[1].text = sep_text
                row_cells[2].text = ', '.join(r.get('nama_aturan','') for r in c['triggered_rules'])
                row_cells[3].text = str(c.get('tingkat_risiko', ''))
                row_cells[4].text = str(c.get('rekomendasi_laporan', ''))
                
                for c_idx, cell in enumerate(row_cells):
                    cell.width = widths[c_idx]
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.name = 'Times New Roman'
                            run.font.size = Pt(9)
                            
            # Move the table to right after this paragraph
            p._p.addnext(new_tbl._tbl)
            
            # If there are more than 10 cases, add a note
            if len(table_priority) > 10 or True:
                note_p = OxmlElement('w:p')
                note_r = OxmlElement('w:r')
                note_t = OxmlElement('w:t')
                note_t.text = f"Menampilkan {min(len(table_priority), 10)} data prioritas teratas. Untuk melihat keseluruhan {len(table_priority)} data kasus secara lengkap, silakan merujuk pada Lampiran 1. Ringkasan KKR-DR01 (Seluruh Kasus Sampel)."
                note_r.append(note_t)
                note_p.append(note_r)
                
                # Apply styling
                pPr = OxmlElement('w:pPr')
                spacing = OxmlElement('w:spacing')
                spacing.set(qn('w:before'), '120')
                spacing.set(qn('w:after'), '120')
                pPr.append(spacing)
                
                i_tag = OxmlElement('w:i')
                rPr = OxmlElement('w:rPr')
                rPr.append(i_tag)
                
                sz = OxmlElement('w:sz')
                sz.set(qn('w:val'), '20') # 10pt
                rPr.append(sz)
                
                rFonts = OxmlElement('w:rFonts')
                rFonts.set(qn('w:ascii'), 'Times New Roman')
                rFonts.set(qn('w:hAnsi'), 'Times New Roman')
                rPr.append(rFonts)
                note_r.insert(0, rPr)
                
                note_p.insert(0, pPr)
                new_tbl._tbl.addnext(note_p)
                
            # Add a small spacing paragraph right after the table / note
            spacer_p = OxmlElement('w:p')
            if len(table_priority) > 10 or True:
                note_p.addnext(spacer_p)
            else:
                new_tbl._tbl.addnext(spacer_p)
            
        if heading and text.startswith('BAB '):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif not heading:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
    placeholder.text = ''

    for p in doc.paragraphs:
        text = p.text
        if text.startswith('●') or text.startswith('\u25cf'):
            bullet = '●  '
            if 'Kepatuhan' in text:
                compliance = (stats['total'] - stats['dc_cases']) / max(stats['total'], 1)
                p.text = bullet + f'Tingkat Kepatuhan Koding (Compliance Rate): {compliance:.1%}.'
            elif 'Rasio' in text:
                onsite_rate = stats['onsite'] / max(stats['total'], 1)
                p.text = bullet + f'Rasio Kasus Prioritas On-Site Audit: {onsite_rate:.1%} ({stats["onsite"]} kasus).'
            elif 'Rata-rata' in text:
                p.text = bullet + f'Rata-rata Indeks Risiko KNAVP: {stats["avg_score"]:.2f}'
            elif 'Monitoring' in text:
                p.text = bullet + f'Monitoring / Lolos (Risiko Rendah): {stats["monitoring"]} Kasus.'
            elif 'Sampling' in text:
                p.text = bullet + f'Audit Sampling / Klarifikasi (Risiko Sedang): {stats["sampling"]} Kasus.'
            elif 'On-Site' in text:
                p.text = bullet + f'On-Site Audit (Risiko Tinggi): {stats["onsite"]} Kasus.'
            elif 'TOTAL KASUS' in text:
                p.text = bullet + f'TOTAL KASUS SAMPEL: {stats["total"]} Kasus (100%).'
            else:
                p.text = bullet + f'Lainnya: {stats["unknown"]} Kasus.'
        if text.startswith('Gambar '):
            p.text = text.replace('1275655', code).replace('Populasi vs Sampel', 'Kasus Direview dan Kasus dengan Alert').replace('Kesesuaian Input INA-CBG vs iDRG', 'Perbedaan Dual Coding Tersimpan')
        if national and text.startswith('Lampiran 1.'):
            p.text = 'Lampiran 1. Rekapitulasi Seluruh RS'
        if national and text.startswith('Tabel berikut menyajikan rekapitulasi seluruh kasus'):
            p.text = 'Tabel mencakup seluruh RS. Rincian lengkap seluruh kasus disajikan pada Excel nasional dan Word/Excel per RS dalam paket snapshot yang sama.'
    if national:
        headers = ['No', 'RS (Kode)', 'Total', 'On-Site', 'Sampling', 'Monitoring', 'Beda DC', 'Tot Alert', 'Rerata Skor', 'Alert Kasus']
        # The template has 13 columns. Remove the last 3 to fit the 10 columns for National
        while len(doc.tables[2].rows[0].cells) > 10:
            for row in doc.tables[2].rows:
                row._tr.remove(row.cells[-1]._tc)
                
        for cell, value in zip(doc.tables[2].rows[0].cells, headers):
            cell.text = value
        rows = [[i, f"{h['nama_rs']} ({h['kode_rs']})", h['summary']['total'], h['summary']['onsite'], h['summary']['sampling'], h['summary']['monitoring'], h['summary']['dc_cases'], h['summary']['alerts'], round(h['summary']['avg_score'], 2), h['summary']['cases_with_alerts']] for i, h in enumerate(hospitals,1)]
    else:
        rows = [[i,c['sep'],c.get('diaglist'),c.get('proclist'),c.get('inacbg'),c.get('deskripsi_inacbg'),c.get('idrg_code'),c.get('deskripsi_idrg'),c['knavp_skor'],c['tingkat_risiko'],len(c['triggered_rules']),c['jumlah_beda_dual_coding'],c['rekomendasi_laporan']] for i,c in enumerate(cases,1)]
    _replace_rows(doc.tables[2], rows)
    # Table[2]: 11 rows matching LHR_V2 format exactly
    pct_mismatch = f'{stats["dc_cases"] / max(stats["total"], 1):.1%}'
    metrics_v2 = [
        ['Total Kasus Di-Review',                         stats['total']],
        ['Total Alert KNAVP',                             stats['alerts']],
        ['Severity High',                                 stats['severity'].get('High', 0)],
        ['Severity Medium',                               stats['severity'].get('Medium', 0)],
        ['Severity Low',                                  stats['severity'].get('Low', 0)],
        ['Rata-rata Skor KNAVP',                          stats['avg_score']],
        ['Rekomendasi Lanjut On-Site Audit',              stats['onsite']],
        ['Rekomendasi Lanjut Audit Sampling',             stats['sampling']],
        ['Rekomendasi Monitoring / Lolos',                stats['monitoring']],
        ['Kasus Mismatch Dual Coding (INA-CBG vs iDRG)', stats['dc_cases']],
        ['Jumlah Perbedaan Dual Coding',                  stats['dc_total']],
        ['Persentase Mismatch Dual Coding',               pct_mismatch],
    ]
    _replace_rows(doc.tables[3], metrics_v2, header=False)
    
    # Table[4]: alerts
    if national:
        alerts = [[i,rule.get('kategori') or rule.get('kelompok_rule') or 'Lainnya',rule.get('rule_id'),rule.get('nama_aturan'),rule.get('severity'),c['sep'],c.get('diaglist') + f"\n(RS: {c.get('kode_rs')})",c.get('proclist'),c.get('alos')] for i,(c,rule) in enumerate(((c,r) for c in cases for r in c['triggered_rules']),1)]
    else:
        alerts = [[i,rule.get('kategori') or rule.get('kelompok_rule') or 'Lainnya',rule.get('rule_id'),rule.get('nama_aturan'),rule.get('severity'),c['sep'],c.get('diaglist'),c.get('proclist'),c.get('alos')] for i,(c,rule) in enumerate(((c,r) for c in cases for r in c['triggered_rules']),1)]
    
    _replace_rows(doc.tables[4], alerts)
    
    # Table[5]: priority
    priority = sorted(
        [c for c in cases if c['jumlah_beda_dual_coding'] > 0 or len(c['triggered_rules']) > 0],
        key=lambda c: (c['rekomendasi_laporan'] != ONSITE, c['rekomendasi_laporan'] != SAMPLING, -c['knavp_skor'], str(c['sep']))
    )
    
    if national:
        _replace_rows(doc.tables[5], [[i,c['sep'],c.get('inacbg'),c.get('deskripsi_inacbg'),c.get('diaglist') + f"\n[RS: {c.get('kode_rs')}]",c.get('proclist'),c['knavp_skor'],c['tingkat_risiko'],len(c['triggered_rules']),c['jumlah_beda_dual_coding'],', '.join(r.get('nama_aturan','') for r in c['triggered_rules']),c['rekomendasi_laporan']] for i,c in enumerate(priority,1)])
    else:
        _replace_rows(doc.tables[5], [[i,c['sep'],c.get('inacbg'),c.get('deskripsi_inacbg'),c.get('diaglist'),c.get('proclist'),c['knavp_skor'],c['tingkat_risiko'],len(c['triggered_rules']),c['jumlah_beda_dual_coding'],', '.join(r.get('nama_aturan','') for r in c['triggered_rules']),c['rekomendasi_laporan']] for i,c in enumerate(priority,1)])

    categories = Counter(r.get('kategori') or r.get('kelompok_rule') or 'Lainnya' for c in cases for r in c['triggered_rules'])
    charts = [(['Total Sampel'], [stats['total']]),
              (['On-Site Audit','Audit Sampling','Monitoring/Lolos'], [stats['onsite'],stats['sampling'],stats['monitoring']]),
              (list(categories) or ['Tidak ada alert'], list(categories.values()) or [0]),
              (['Mismatch','Sinkron'],[stats['dc_cases'],stats['total']-stats['dc_cases']])]
    

    # Update Tables 5-8 in place to preserve Lampiran 5 template formatting
    c_pop = f"chart_{code}_004"
    c_rek = f"chart_{code}_001"
    c_kat = f"chart_{code}_002"
    c_mis = f"chart_{code}_003"
    
    table_mappings = [
        (5, c_pop),
        (6, c_rek),
        (7, c_kat),
        (8, c_mis)
    ]
    
    final_charts = []
    
    for t_idx, c_id in table_mappings:
        c_idx = [5,6,7,8].index(t_idx)
        c_labels, c_values = charts[c_idx]
        
        if len(doc.tables) > t_idx and c_id in chart_info:
            c_data = chart_info[c_id]
            final_charts.append((c_data['labels'], c_data['values']))
            table = doc.tables[t_idx]
            for row in table.rows[1:]:
                try:
                    k = row.cells[0].text.strip().lower()
                    for idx_lbl, lbl in enumerate(c_data['labels']):
                        if k in lbl.lower() or lbl.lower() in k:
                            row.cells[1].text = str(c_data['values'][idx_lbl])
                            break
                except Exception:
                    pass
        elif len(doc.tables) > t_idx:
            # Fallback to dynamically calculated charts
            final_charts.append((c_labels, c_values))
            label_to_val = {str(k).lower(): v for k, v in zip(c_labels, c_values)}
            table = doc.tables[t_idx]
            for row in table.rows[1:]:
                try:
                    k = row.cells[0].text.strip().lower()
                    for lbl, val in label_to_val.items():
                        if k in lbl or lbl in k:
                            row.cells[1].text = str(val)
                            break
                except Exception:
                    pass
        else:
            final_charts.append(([], []))
    from PIL import Image, ImageDraw, ImageFont
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(font_path), 20) if font_path.exists() else ImageFont.load_default()
    for p, (labels, values) in zip(chart_paragraphs, final_charts):
        if not labels:
            continue
        img = Image.new('RGB', (1200, max(190, len(labels)*55+45)), 'white')
        draw = ImageDraw.Draw(img)
        maximum = max(values+[1])
        for i,(label,value) in enumerate(zip(labels,values)):
            y=25+i*55
            draw.text((10,y),label,fill='#1E3A5F',font=font)
            width=round(value/maximum*600)
            if width:
                draw.rectangle((450,y,450+width,y+27),fill='#1E3A5F')
            draw.text((465+width,y),str(value),fill='black',font=font)
        buffer=io.BytesIO()
        img.save(buffer,format='PNG')
        buffer.seek(0)
        p.add_run().add_picture(buffer,width=Inches(6.3))
        
    # Also replace explicitly typed markdown placeholders in the document body
    mapping = {
        '[CHART_DISTRIBUSI_KEPUTUSAN]': 1,
        '[CHART_TOP_RULES]': 2
    }
    for p_mark in doc.paragraphs:
        for marker, idx in mapping.items():
            if marker in p_mark.text:
                p_mark.text = p_mark.text.replace(marker, '')
                labels, values = final_charts[idx]
                if labels:
                    img = Image.new('RGB', (1200, max(190, len(labels)*55+45)), 'white')
                    draw = ImageDraw.Draw(img)
                    maximum = max(values+[1])
                    for i,(label,value) in enumerate(zip(labels,values)):
                        y=25+i*55
                        draw.text((10,y),label,fill='#1E3A5F',font=font)
                        width=round(value/maximum*600)
                        if width:
                            draw.rectangle((450,y,450+width,y+27),fill='#1E3A5F')
                        draw.text((465+width,y),str(value),fill='black',font=font)
                    buffer=io.BytesIO()
                    img.save(buffer,format='PNG')
                    buffer.seek(0)
                    p_mark.add_run().add_picture(buffer,width=Inches(6.3))

    if national:
        # Create a special table for On-Site Recommendations as requested by user
        doc.add_page_break()
        p = doc.add_paragraph('Lampiran Tambahan: Daftar RS Rekomendasi On-Site Audit', style='Heading 2')
        onsite_cases = [c for c in cases if c.get('rekomendasi_laporan') == ONSITE]
        
        if not onsite_cases:
            doc.add_paragraph('Tidak ada kasus yang direkomendasikan untuk On-Site Audit pada periode ini.')
        else:
            onsite_table = doc.add_table(rows=1, cols=4, style='Table Grid')
            onsite_table.autofit = False
            onsite_table.allow_autofit = False
            widths_4col = [Inches(0.4), Inches(2.0), Inches(1.5), Inches(2.6)]
            for col, width in zip(onsite_table.columns, widths_4col):
                col.width = width
                
            hdr_cells = onsite_table.rows[0].cells
            for idx, th in enumerate(['No', 'Rumah Sakit', 'No SEP', 'Diagnosis & Prosedur']):
                hdr_cells[idx].text = th
                hdr_cells[idx].width = widths_4col[idx]
            
            for i, c in enumerate(onsite_cases, 1):
                row_cells = onsite_table.add_row().cells
                row_cells[0].text = str(i)
                
                # Fetch nama_rs from hospitals mapping if available
                nama_rs = next((h['nama_rs'] for h in (hospitals or []) if h['kode_rs'] == c.get('kode_rs')), '')
                row_cells[1].text = f"{nama_rs}\n({c.get('kode_rs')})"
                
                row_cells[2].text = c.get('sep', '')
                row_cells[3].text = f"Diag: {c.get('diaglist', '')}\nProc: {c.get('proclist', '')}"
                
                # Format cell fonts
                for c_idx, cell in enumerate(row_cells):
                    cell.width = widths_4col[c_idx]
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.name = 'Times New Roman'
                            run.font.size = Pt(9)

        # --- Audit Sampling Table ---
        doc.add_page_break()
        p2 = doc.add_paragraph('Lampiran Tambahan: Daftar RS Rekomendasi Audit Sampling', style='Heading 2')
        sampling_cases = [c for c in cases if c.get('rekomendasi_laporan') == SAMPLING]
        
        if not sampling_cases:
            doc.add_paragraph('Tidak ada kasus yang direkomendasikan untuk Audit Sampling pada periode ini.')
        else:
            sampling_table = doc.add_table(rows=1, cols=4, style='Table Grid')
            sampling_table.autofit = False
            sampling_table.allow_autofit = False
            for col, width in zip(sampling_table.columns, widths_4col):
                col.width = width
                
            hdr_cells2 = sampling_table.rows[0].cells
            for idx, th in enumerate(['No', 'Rumah Sakit', 'No SEP', 'Diagnosis & Prosedur']):
                hdr_cells2[idx].text = th
                hdr_cells2[idx].width = widths_4col[idx]
            
            for i, c in enumerate(sampling_cases, 1):
                row_cells = sampling_table.add_row().cells
                row_cells[0].text = str(i)
                
                nama_rs = next((h['nama_rs'] for h in (hospitals or []) if h['kode_rs'] == c.get('kode_rs')), '')
                row_cells[1].text = f"{nama_rs}\n({c.get('kode_rs')})"
                
                row_cells[2].text = c.get('sep', '')
                row_cells[3].text = f"Diag: {c.get('diaglist', '')}\nProc: {c.get('proclist', '')}"
                
                for c_idx, cell in enumerate(row_cells):
                    cell.width = widths_4col[c_idx]
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.name = 'Times New Roman'
                            run.font.size = Pt(9)

    # Apply explicit fixed widths for Google Docs compatibility on Lampiran tables
    if national:
        _set_table_widths(doc.tables[2], [0.3, 2.0, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.8])
    else:
        _set_table_widths(doc.tables[2], [0.3, 1.0, 1.0, 1.0, 0.8, 1.0, 0.8, 1.0, 0.5, 0.6, 0.5, 0.5, 0.6])
    
    _set_table_widths(doc.tables[3], [4.0, 1.5])
    _set_table_widths(doc.tables[4], [0.4, 1.0, 0.8, 2.0, 0.8, 1.2, 1.2, 1.2, 0.5])
    _set_table_widths(doc.tables[5], [0.3, 1.0, 0.8, 1.0, 1.2, 1.2, 0.6, 0.6, 0.5, 0.5, 1.5, 0.8])

    Path(path).parent.mkdir(parents=True,exist_ok=True)
    doc.save(path)
    return str(path)


def _set_table_widths(table, widths_in_inches):
    from docx.shared import Inches
    table.autofit = False
    table.allow_autofit = False
    for i, w in enumerate(widths_in_inches):
        if i < len(table.columns):
            table.columns[i].width = Inches(w)
        for row in table.rows:
            if i < len(row.cells):
                row.cells[i].width = Inches(w)
