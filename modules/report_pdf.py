"""KKR PDF from the same saved-review snapshot as Word/Excel. No invented data."""
from pathlib import Path
import io
import json
import sqlite3
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

NA='Tidak tersedia pada sumber'
FIELD_KEYS=[
    ('Nomor SEP','sep'), ('Kode RS','kode_rs'), ('Nama RS','nama_rs'),
    ('Kode INA-CBG','inacbg'), ('Kode iDRG','idrg_code'),
    ('Deskripsi INA-CBG','deskripsi_inacbg'), ('Deskripsi iDRG','deskripsi_idrg'),
    ('Tarif INA-CBG (Rp)','tarif_inacbg'), ('Tarif RS (Rp)','tarif_rs'),
    ('Skor KNAVP dasar','knavp_skor'), ('Tingkat risiko tersimpan','tingkat_risiko'),
    ('Jumlah perbedaan dual coding','jumlah_beda_dual_coding'), ('Jumlah alert KNAVP','alert_count'),
    ('Keputusan sistem tersimpan','keputusan_sistem'),
    ('Sumber rekomendasi','sumber_rekomendasi'),
    ('Diagnosis INA-CBG','diaglist'), ('Prosedur INA-CBG','proclist'),
    ('Diagnosis iDRG','diaglist_idrg'), ('Prosedur iDRG','proclist_idrg')]
END_MARKER='AKHIR RINGKASAN TERSIMPAN'

def printable(value):
    text=str(value if value is not None and value!='' else NA)
    for a,b in [('–','-'),('—','-'),('‑','-'),('→','->'),('≥','>='),('≤','<='),('“','"'),('”','"'),('’',"'"),('•','-')]:
        text=text.replace(a,b)
    return text

def fields(case):
    c=dict(case,alert_count=len(case['triggered_rules']))
    return {label:printable(c.get(key)) for label,key in FIELD_KEYS}

def _export_detail_pdf(case,snapshot_id,demographics=None):
    demographics=demographics or {}
    form=json.loads(case.get('tindakan_reviewer') or '{}')
    buf=io.BytesIO()
    width=A4[0]-3*cm
    normal=ParagraphStyle('KKRText',fontName='Helvetica',fontSize=8.3,leading=11,spaceAfter=2)
    small=ParagraphStyle('KKRSmall',parent=normal,fontSize=7,leading=9,textColor=colors.HexColor('#475569'))
    head=ParagraphStyle('KKRSection',parent=normal,fontName='Helvetica-Bold',fontSize=10,leading=13,spaceBefore=7,spaceAfter=5,textColor=colors.HexColor('#1E3A5F'))
    title=ParagraphStyle('KKRTitle',parent=head,fontSize=14,leading=17)
    def p(value,style=normal):return Paragraph(escape(printable(value)).replace('\n','<br/>'),style)
    def table(items):
        t=Table([[p(k),p(v)] for k,v in items],colWidths=[6.1*cm,width-6.1*cm],hAlign='LEFT')
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#CBD5E1')),('BACKGROUND',(0,0),(0,-1),colors.HexColor('#EFF6FF')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
        return t
    story=[p('KERTAS KERJA REVIEWER - DESK REVIEW (KKR-DR01)',title),p('TGL Berlaku: 1 Juni 2026',small),p('SALINAN REKONSILIASI - BUKAN PENGESAHAN ULANG',small),p('1. RINGKASAN HASIL REVIEW TERSIMPAN',head),table(fields(case).items()),p(END_MARKER,small),Spacer(1,5),p('Monitoring menggabungkan monitoring dan tidak perlu tindak lanjut. Keputusan reviewer asli berbeda fungsi dari rekomendasi tindak lanjut; keduanya ditampilkan terpisah. Jumlah perbedaan di atas berasal dari KKR tersimpan, bukan perbandingan kode grup INA-CBG/iDRG.',small),PageBreak()]
    story += [p('2. IDENTITAS TAMBAHAN DARI SUMBER',head),table([
        ('Nama pasien',demographics.get('Nama_Pasien')),
        ('Jenis kelamin (kode sumber)',demographics.get('SEX')),
        ('Tanggal lahir',demographics.get('Birth_date')),
        ('Tanggal masuk',demographics.get('admission_date')),
        ('Tanggal pulang',demographics.get('discharge_date')),
        ('Kelas rawat',demographics.get('kelas_rawat')),
        ('Lama rawat / LOS (hari)',case.get('alos')),
        ('Nomor klaim / peserta',NA),('DPJP',NA)]),
        p('Identitas yang tidak tersedia tidak diisi dengan data buatan. Identitas tambahan berasal dari data.db dengan pasangan Kode RS dan Nomor SEP; tidak digunakan untuk mengubah keputusan audit.',small),
        p('3. TEMUAN ATURAN AUDIT TERSIMPAN',head)]
    if not case['triggered_rules']:
        story.append(p('Tidak ada alert aturan yang tersimpan. Ini bukan penetapan bahwa pengodean pasti benar.'))
    for i,rule in enumerate(case['triggered_rules'],1):
        story.append(p(f'{i}. {rule.get("rule_id", "")} - {rule.get("nama_aturan", "")}',head))
        story.append(table([('Severity',rule.get('severity')),('Kategori',rule.get('kategori') or rule.get('kelompok_rule')),('Bobot',rule.get('bobot')),('Skor',rule.get('skor')),('Bukti / pesan',rule.get('evidence') or rule.get('pesan_validasi'))]))
    story += [p('4. CATATAN REVIEW ASLI',head),p('Teks berikut disalin dari kertas kerja tersimpan, tanpa penilaian klinis ulang.',small),table([
        ('Analisis reviewer',form.get('analisis_reviewer')),
        ('Alasan keputusan',case.get('alasan_keputusan')),
        ('Tingkat keyakinan',form.get('tingkat_keyakinan')),
        ('Tanggal review tersimpan',case.get('tanggal_review'))]),
        p('5. KEPUTUSAN DAN REKOMENDASI',head),table([
        ('Keputusan Reviewer',case.get('keputusan_reviewer_asli')),
        ('Rekomendasi',case.get('rekomendasi_laporan'))]),
        p('6. JEJAK REKONSILIASI',head),p('Snapshot SHA256: '+snapshot_id,small),
        p('Ringkasan ini dicocokkan dengan Excel per RS dan Excel nasional pada snapshot yang sama. Salinan ini tidak menambahkan tanda tangan atau menyatakan adanya persetujuan baru dari reviewer.',small)]
        
    # Identity QR codes already appear on the cover; do not repeat a detached
    # signature-looking block on an otherwise empty appendix page.
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Helvetica',7);canvas.setFillColor(colors.HexColor('#475569'))
        canvas.drawString(1.5*cm,1.0*cm,f'KKR-DR01 | RS {case["kode_rs"]} | SEP {case["sep"]}')
        canvas.drawRightString(A4[0]-1.5*cm,1.0*cm,f'Lampiran | Halaman {doc.page + 1}')
        canvas.restoreState()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=1.5*cm,rightMargin=1.5*cm,topMargin=1.3*cm,bottomMargin=1.7*cm,
                          title=f'KKR-DR01 {case["kode_rs"]} {case["sep"]}',author='Salinan rekonsiliasi data tersimpan',subject=f'saved-review-v1; snapshot {snapshot_id}')
    from functools import partial
    from reportlab.pdfgen.canvas import Canvas
    doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=partial(Canvas,invariant=1))
    return buf.getvalue()


def export_pdf(case, snapshot_id, demographics=None):
    """Generate KKR-DR01 PDF - cover only (no appendix lampiran pages)."""
    from modules.kkr_reference_layout import cover_pdf
    return cover_pdf(case, snapshot_id, demographics, page_count=1)


def export_saved_pdf(sep,kode_rs=None):
    """Current download: saved KKR only; never stale file/JSON cache or fabricated identities."""
    from modules.db_manager import get_recap_desk_review
    from modules.report_data import build_snapshot
    rows=get_recap_desk_review(sep=sep,kode_rs=kode_rs)
    if len(rows)!=1:
        raise ValueError('Review tersimpan tidak ditemukan atau pasangan Kode RS/SEP tidak unik')
    snapshot=build_snapshot(rows);case=snapshot['cases'][0]
    db=Path(__file__).resolve().parents[1]/'data.db'
    conn=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True);conn.row_factory=sqlite3.Row
    try:
        row=conn.execute('SELECT Nama_Pasien,SEX,Birth_date,admission_date,discharge_date,kelas_rawat FROM individual_data WHERE kode_rs=? AND sep=?',(case['kode_rs'],case['sep'])).fetchone()
    finally:
        conn.close()
    return export_pdf(case,snapshot['snapshot_id'],dict(row) if row else {})
