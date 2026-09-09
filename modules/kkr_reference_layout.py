"""KKR-DR01 - Reference layout PDF (canvas-drawn, A4 portrait).

Perbaikan (2026-09-08):
  * FONT_SCALE dikembalikan ke 1.0 agar proporsi text rapi sesuai desain awal.
  * QR Code scaling FIX dipertahankan agar tidak melebar/ngeblur/menimpa teks.
  * Deskripsi ICD dilookup dari kamus ICD.
  * Kode '(IM)' tetap TAMPIL, otomatis dicentang SESUAI, dan DIKECUALIKAN dari hitungan beda.
  * Isi payload QR Code eksklusif string KODE RS dan NO SEP.
"""
import io
import json
import math
from xml.sax.saxutils import escape
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics import renderPDF

NAVY = '#08265c'
TEAL = '#006071'
LINE = '#9bbacb'
PALE = '#f1f6f8'
TGL_VALIDASI = '15 Juni 2026'
FONT_SCALE = 1.05  # Slight 5% boost for readability without breaking layout

def _get_icd_desc(code, icd_dict):
    if not code: return '-'
    c = str(code).strip().upper()
    if c in icd_dict: return icd_dict[c]
    c2 = c.replace('.', '')
    if c2 in icd_dict: return icd_dict[c2]
    while len(c) >= 3:
        c = c[:-1]
        if c in icd_dict: return icd_dict[c]
        c2 = c.replace('.', '')
        if c2 in icd_dict: return icd_dict[c2]
    return '-'

def _match_code(code_i, code_r):
    if not code_i or not code_r: return False
    ci = str(code_i).strip().upper()
    cr = str(code_r).strip().upper().split('+')[0]
    return ci == cr or ci.startswith(cr) or cr.startswith(ci)

def cover_pdf(case, snapshot_id, demographics=None, page_count=None):
    from modules.data_loader import get_icd_dict
    icd_dict = get_icd_dict()

    d = demographics or {}
    raw = case.get('tindakan_reviewer') or '{}'
    form = json.loads(raw) if isinstance(raw, str) else raw

    def _codes(key):
        return [s.strip() for s in str(case.get(key) or '').split(';') if s.strip()]

    def is_im_code(code):
        if not code: return False
        if str(code).strip().upper() == '(IM)': return True
        desc = _get_icd_desc(code, icd_dict)
        return '(IM)' in str(desc).upper()

    def _align_codes_local(list_i, list_r):
        aligned = []
        used_r = set()
        for ci in list_i:
            best_match = None
            for j, cr in enumerate(list_r):
                if j not in used_r and _match_code(ci, cr):
                    best_match = cr
                    used_r.add(j)
                    break
            if best_match:
                aligned.append((ci, best_match))
            else:
                aligned.append((ci, ''))
                
        for j, cr in enumerate(list_r):
            if j not in used_r:
                aligned.append(('', cr))
                
        return aligned

    diag_inacbg = _codes('diaglist')
    diag_idrg   = _codes('diaglist_idrg')
    proc_inacbg = _codes('proclist')
    proc_idrg   = _codes('proclist_idrg')

    aligned_diag = _align_codes_local(diag_inacbg, diag_idrg)
    aligned_proc = _align_codes_local(proc_inacbg, proc_idrg)

    # Dynamic calculation of differences
    diff_count = 0
    for code_i, code_r in aligned_diag:
        if (code_i or code_r) and not _match_code(code_i, code_r):
            if not is_im_code(code_i) and not is_im_code(code_r):
                diff_count += 1
    for code_i, code_r in aligned_proc:
        if (code_i or code_r) and not _match_code(code_i, code_r):
            if not is_im_code(code_i) and not is_im_code(code_r):
                diff_count += 1

    rules    = case.get('triggered_rules') or []
    sep_val  = str(case.get('sep') or '')
    kode_rs_val = str(case.get('kode_rs') or '')
    nama_pasien = str(d.get('Nama_Pasien') or case.get('nama_pasien') or '-')
    reviewer_name = form.get('reviewer_name') or case.get('reviewer_name') or '-'
    nip_val  = form.get('nip_reviewer') or '-'

    buf = io.BytesIO()
    c = Canvas(buf, pagesize=A4, invariant=1)
    W, H = A4
    SX = W / 1024
    SY = H / 1536

    def _y(y_virt): return H - y_virt * SY

    def box(x, y, w, h, fill=None, stroke=LINE):
        c.saveState()
        c.setStrokeColor(colors.HexColor(stroke))
        c.setLineWidth(.65)
        if fill:
            c.setFillColor(colors.HexColor(fill))
            c.rect(x*SX, _y(y+h), w*SX, h*SY, fill=1, stroke=1)
        else:
            c.rect(x*SX, _y(y+h), w*SX, h*SY, fill=0, stroke=1)
        c.restoreState()

    def text(x, y, value, size=11, bold=False, color=NAVY, align='left'):
        c.saveState()
        c.setFillColor(colors.HexColor(color))
        fs = max(4, size * min(SX, SY) * FONT_SCALE)
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', fs)
        ry = _y(y + size)
        rx = x * SX
        draw = (c.drawCentredString if align == 'center' else c.drawRightString if align == 'right' else c.drawString)
        draw(rx, ry, str(value if value is not None else '-'))
        c.restoreState()

    def get_para_height(w, value, size=10, bold=False):
        fs = max(4, size * min(SX, SY) * FONT_SCALE)
        style = ParagraphStyle('cell', fontName='Helvetica-Bold' if bold else 'Helvetica',
                               fontSize=fs, leading=fs*1.15)
        p = Paragraph(escape(str(value)).replace('\n', '<br/>'), style)
        _, ph = p.wrap(w * SX, 9999)
        return ph / SY

    def para(x, y, w, h, value, size=10, bold=False, align=0, color=NAVY):
        value = str(value if value not in (None, '') else '-')
        fs = max(4, size * min(SX, SY) * FONT_SCALE)
        style = ParagraphStyle('cell', fontName='Helvetica-Bold' if bold else 'Helvetica',
                               fontSize=fs, leading=fs*1.15,
                               textColor=colors.HexColor(color), alignment=align)
        p = Paragraph(escape(value).replace('\n', '<br/>'), style)
        pw = w * SX
        _, ph = p.wrap(pw, 9999)
        p.drawOn(c, x*SX, _y(y + (ph/SY)))

    def section(x, y, w, h, title, tab=None):
        if h > 0: box(x, y, w, h)
        box(x, y, tab or w, 24, TEAL, TEAL)
        text(x+12, y+4, title, 12, True, '#ffffff')

    def field(x, y, label, value, labelw=168, w=400):
        ls = 10.6
        raw_width = c.stringWidth(label, 'Helvetica-Bold', ls * min(SX, SY) * FONT_SCALE)
        avail_lw = (labelw-8) * SX
        if raw_width > avail_lw:
            ls = ls * (avail_lw / raw_width)
            
        text(x, y, label, ls, True)
        text(x+labelw, y, ':', 10.6)
        
        value = str(value if value not in (None, '') else '-')
        avail_w = (w-labelw-12) * SX
        
        val_fs = 10.3 * min(SX, SY) * FONT_SCALE
        if c.stringWidth(value, 'Helvetica', val_fs) > avail_w:
            para(x+labelw+12, y - 1.5, w-labelw-12, 10.6, value, 9.8)
        else:
            text(x+labelw+12, y, value, 10.3)

    def tick(x, y, checked=False):
        box(x, y, 9, 9, stroke=NAVY)
        if checked:
            c.saveState(); c.setStrokeColor(colors.HexColor(TEAL)); c.setLineWidth(1.6)
            p2 = c.beginPath(); p2.moveTo(x*SX+1*SX, _y(y+4)); p2.lineTo(x*SX+4*SX, _y(y+8)); p2.lineTo(x*SX+8*SX, _y(y+1))
            c.drawPath(p2); c.restoreState()

    def qr_draw(x, y, size, payload=None):
        if payload is None:
            # SIMPLE STRING AS REQUESTED
            payload = f"KODE RS: {kode_rs_val} | NO SEP: {sep_val}"
        drawing = createBarcodeDrawing('QR', value=payload)
        scale_x = (size * SX) / drawing.width
        scale_y = (size * SY) / drawing.height
        
        c.saveState()
        c.translate(x * SX, _y(y + size))
        c.scale(scale_x, scale_y)
        renderPDF.draw(drawing, c, 0, 0)
        c.restoreState()

    class Cursor:
        def __init__(self):
            self.y = 168
            self.page = 1
        
        def check_break(self, needed):
            if self.y + needed > 1420:
                self.draw_footer()
                c.showPage()
                self.page += 1
                self.y = 50
                
        def draw_footer(self):
            fy = 1440
            box(17, fy, 376, 75); box(394, fy, 299, 75); box(694, fy, 313, 75)
            text(30, fy+7, 'KETERANGAN HASIL VALIDASI OTOMATIS', 9.5, True, TEAL)
            para(30, fy+24, 350, 44, 'Hasil dibuat otomatis berdasarkan aturan KNAVP dan data klaim tanpa telaah rekam medis. Rekomendasi On-Site Audit memerlukan tindak lanjut pada tahap audit.', 9.2)
            text(408, fy+7, 'TINGKAT KEYAKINAN SISTEM', 9.2, True, TEAL)
            for i, (label, col) in enumerate([('Rendah : indikasi lemah / data terbatas.', '#078599'), ('Sedang : indikasi cukup, belum konklusif.', '#eea500'), ('Tinggi : indikasi kuat dari data tersedia.', '#d70000')]):
                c.setFillColor(colors.HexColor(col)); c.circle(419*SX, _y(fy+32+i*14), 4, fill=1, stroke=0); text(432, fy+27+i*14, label, 8.4)
            text(705, fy+10, 'VALIDASI DOKUMEN', 9.5, True, TEAL); para(705, fy+27, 210, 35, 'QR memuat identitas dan snapshot dokumen; bukan bukti pengesahan reviewer.', 9)
            qr_draw(928, fy+8, 60)
            text(512, fy+79, 'Dokumen ini adalah hasil validasi otomatis dan bukan penetapan Fraud. Tanda - berarti data belum tersedia.', 8.9, align='center')

    cursor = Cursor()

    # ================= HEADER =================
    box(9, 9, 1006, 1518)
    c.saveState(); c.translate(21*SX, _y(91))
    c.setFillColor(colors.HexColor('#008b9a')); c.roundRect(22*SX, 0, 21*SX, 67*SY, 10*SX, stroke=0, fill=1)
    c.roundRect(0, 24*SY, 42*SX, 21*SY, 10*SX, stroke=0, fill=1); c.setFillColor(colors.HexColor('#d0db00'))
    for flip in (1, -1):
        c.saveState(); c.translate(23*SX, 34*SY); c.scale(1, flip); p2 = c.beginPath()
        p2.moveTo(0, 0); p2.lineTo(20*SX, 20*SY); p2.curveTo(31*SX, 31*SY, 43*SX, 20*SY, 35*SX, 8*SY)
        p2.curveTo(32*SX, 2*SY, 26*SX, 0, 20*SX, 0); p2.close(); c.drawPath(p2, stroke=0, fill=1); c.restoreState()
    c.setStrokeColor(colors.white); c.setLineWidth(1.4)
    c.line(22*SX, 4*SY, 22*SX, 64*SY); c.line(23*SX, 34*SY, 59*SX, 34*SY)
    c.line(23*SX, 34*SY, 42*SX, 54*SY); c.line(23*SX, 34*SY, 42*SX, 14*SY); c.restoreState()
    text(88, 42, 'KEMENTERIAN KESEHATAN', 12, True, '#111111')
    text(88, 58, 'REPUBLIK INDONESIA', 12, True, '#111111')
    text(528, 10, 'KKR-DR01', 35, True, align='center')
    text(528, 48, 'KERTAS KERJA REVIEWER - DESK REVIEW', 21, True, '#111111', 'center')
    text(528, 76, 'HASIL VALIDASI OTOMATIS', 20, True, '#007b83', 'center')
    text(528, 101, 'AUDIT CODING DAN VERIFIKASI DUAL CODING', 16, True, align='center')
    text(528, 124, 'Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)', 12, True, align='center')
    box(299, 143, 436, 21, '#087f85', '#087f85')
    text(517, 145, 'BERDASARKAN DATA KLAIM - TANPA TELAAH REKAM MEDIS', 12, True, '#ffffff', 'center')
    box(798, 17, 209, 113)
    for i, (k, v) in enumerate([('KODE DOKUMEN', 'KKR-DR01'), ('VERSI', '1.0'), ('TANGGAL BERLAKU', '1 Juni 2026'), ('HALAMAN', f'1 dari {page_count or 1}')]):
        text(808, 30+i*24, k, 9.8, True); text(917, 30+i*24, ':', 10); text(930, 30+i*24, str(v), 9.5, True)

    # ================= SECTION 1 =================
    cursor.check_break(250)
    y1 = cursor.y
    section(17, y1, 990, 237, '1. IDENTITAS KLAIM (DATA KLAIM DATA CENTER)', 374)
    box(449, y1+24, 411, 213); box(860, y1+24, 147, 213)
    left = [('Nomor Klaim', case.get('nomor_klaim')), ('Nomor SEP', sep_val), ('Nomor Peserta', case.get('nomor_peserta')),
            ('Nama Peserta', nama_pasien), ('Tanggal Lahir / Umur', d.get('Birth_date')),
            ('Jenis Kelamin', {'1': 'Laki-laki', '2': 'Perempuan', 'L': 'Laki-laki', 'P': 'Perempuan'}.get(str(d.get('SEX', '')), d.get('SEX'))),
            ('Fasilitas Kesehatan (FKRTL)', case.get('nama_rs')), ('Kode FPKTL', case.get('kode_rs')), ('Kelas Rawat', d.get('kelas_rawat'))]
    for i, (k, v) in enumerate(left): field(30, y1+35+i*22, k, v, w=410)
    right = [('Tanggal Pelayanan', f"{d.get('admission_date') or '-'} s.d. {d.get('discharge_date') or '-'}"), ('Jenis Pelayanan', case.get('jenis_pelayanan')),
             ('DPJP (Data Klaim)', case.get('dpjp')), ('Sumber Data', 'INA-CBG / iDRG'), ('Waktu Proses Sistem', case.get('updated_at')),
             ('Versi Grouper', case.get('versi_grouper')), ('Jumlah Diagnosa (Klaim)', len(diag_inacbg)), ('Jumlah Prosedur (Klaim)', len(proc_inacbg))]
    for i, (k, v) in enumerate(right): field(464, y1+35+i*23, k, v, labelw=127, w=380)
    text(934, y1+44, 'BARCODE KLAIM', 11, True, '#111111', 'center')
    qr_draw(880, y1+50, 90)
    text(934, y1+148, '( Tempel / Scan )', 8, align='center')
    cursor.y += 247

    # ================= SECTION 2 =================
    cursor.check_break(240)
    y2 = cursor.y
    section(17, y2, 990, 230, '2. INFORMASI GROUPING DAN TARIF', 294)
    box(17, y2+25, 492, 27); text(263, y2+31, 'INA-CBG (Klaim)', 10, True, align='center')
    box(509, y2+25, 498, 27); text(758, y2+31, 'iDRG (Dual Coding)', 10, True, align='center')
    
    cw = [103, 210, 80, 99, 109, 190, 87, 112]
    cx = 17
    for w, title in zip(cw, ['Kode INA-CBG', 'Deskripsi INA-CBG', 'Group', 'Tarif (Rp)', 'Kode iDRG', 'Deskripsi iDRG', 'CCL', 'Tarif (Rp)']):
        box(cx, y2+52, w, 28, fill=PALE); text(cx+(w/2), y2+58, title, 9.4, True, align='center'); cx += w
    cx = 17
    def money(v):
        try: return 'Rp ' + f'{float(v):,.0f}'.replace(',', '.') if v is not None else '-'
        except (TypeError, ValueError): return '-'
    vals = [case.get('inacbg'), case.get('deskripsi_inacbg'), case.get('inacbg_group'), case.get('tarif_inacbg'), case.get('idrg_code'), case.get('deskripsi_idrg'), case.get('ccl_label'), case.get('tarif_idrg')]
    for w, val in zip(cw, vals):
        box(cx, y2+80, w, 32); para(cx+5, y2+85, w-10, 24, val, 9.4, align=1 if w in (80,87) else 0); cx += w

    delta = None
    try: delta = float(case['tarif_inacbg']) - float(case['tarif_rs'])
    except (KeyError, TypeError, ValueError): pass
    box(24, y2+121, 292, 23, fill=PALE); text(170, y2+126, 'KOMPONEN TARIF', 10, True, align='center')
    box(316, y2+121, 215, 23, fill=PALE); text(423, y2+126, 'NILAI (Rp)', 10, True, align='center')
    for i, (k, v) in enumerate([('Tarif Klaim (INA-CBG)', money(case.get('tarif_inacbg'))), ('Tarif RS (Tarif Standar)', money(case.get('tarif_rs'))), ('Selisih (Tarif Klaim - Tarif RS)', money(delta))]):
        box(24, y2+144+i*24, 292, 24); para(29, y2+149+i*24, 282, 14, k, 10)
        box(316, y2+144+i*24, 215, 24); para(321, y2+149+i*24, 205, 14, v, 10, align=1)
    
    box(546, y2+130, 452, 86); text(558, y2+143, 'Catatan:', 11, True)
    para(558, y2+164, 425, 44, 'Informasi iDRG merupakan hasil dual coding otomatis oleh sistem berdasarkan data klaim tanpa telaah rekam medis.', 11)
    cursor.y += 240

    # ================= SECTION 3 =================
    cursor.check_break(200)
    y3 = cursor.y
    section(17, y3, 990, -1, '3. INFORMASI DUAL CODING - HASIL PERBANDINGAN OTOMATIS', 435) # h=-1 so no outer box yet
    box(17, y3+24, 27, 25, fill=PALE); text(17+13, y3+30, 'No.', 10.5, True, align='center')
    box(44, y3+24, 478, 25, fill=PALE); text(44+239, y3+30, 'DIAGNOSA', 10.5, True, align='center')
    box(522, y3+24, 485, 25, fill=PALE); text(522+242, y3+30, 'PROSEDUR / TINDAKAN', 10.5, True, align='center')
    
    dx_w1 = [152, 163, 97, 66]
    dx_t1 = ['INA-CBG (Klaim)', 'iDRG (Dual Coding)', 'Hasil Perbandingan', 'Ket. Sistem']
    cx = 44; 
    for w, t in zip(dx_w1, dx_t1): box(cx, y3+49, w, 34, fill=PALE); text(cx+w/2, y3+54, t, 9, True, align='center'); cx+=w
    dx_w2 = [72, 80, 76, 87, 48, 49, 66]
    dx_t2 = ['Kode ICD-10', 'Deskripsi', 'Kode ICD-10', 'Deskripsi', 'Sesuai', 'Tidak Sesuai', '']
    cx = 44; 
    for w, t in zip(dx_w2, dx_t2): box(cx, y3+83, w, 32, fill=PALE); text(cx+w/2, y3+88, t, 8.2, True, align='center'); cx+=w

    px_w1 = [160, 164, 99, 62]
    px_t1 = ['INA-CBG (Klaim)', 'iDRG (Dual Coding)', 'Hasil Perbandingan', 'Ket. Sistem']
    cx = 522; 
    for w, t in zip(px_w1, px_t1): box(cx, y3+49, w, 34, fill=PALE); text(cx+w/2, y3+54, t, 9, True, align='center'); cx+=w
    px_w2 = [86, 74, 89, 75, 49, 50, 62]
    px_t2 = ['ICD-9-CM / ICD-10-PCS', 'Deskripsi', 'ICD-9-CM / ICD-10-PCS', 'Deskripsi', 'Sesuai', 'Tidak Sesuai', '']
    cx = 522; 
    for w, t in zip(px_w2, px_t2): box(cx, y3+83, w, 32, fill=PALE); text(cx+w/2, y3+88, t, 7.8, True, align='center'); cx+=w

    cur_yy = y3 + 115
    max_items = max(6, len(aligned_diag), len(aligned_proc))
    
    for i in range(max_items):
        if i < len(aligned_diag):
            d_code_i, d_code_r = aligned_diag[i]
        else:
            d_code_i, d_code_r = '', ''

        d_desc_i = _get_icd_desc(d_code_i, icd_dict) if d_code_i else ''
        d_desc_r = _get_icd_desc(d_code_r, icd_dict) if d_code_r else ''
        
        has_d = bool(d_code_i or d_code_r)
        if has_d:
            if is_im_code(d_code_i) or is_im_code(d_code_r):
                d_diff = False # FORCE Sesuai
            else:
                d_diff = not _match_code(d_code_i, d_code_r)
        else:
            d_diff = False
            
        d_color = '#DC2626' if d_diff else NAVY

        if i < len(aligned_proc):
            p_code_i, p_code_r = aligned_proc[i]
        else:
            p_code_i, p_code_r = '', ''

        p_desc_i = _get_icd_desc(p_code_i, icd_dict) if p_code_i else ''
        p_desc_r = _get_icd_desc(p_code_r, icd_dict) if p_code_r else ''
        
        has_p = bool(p_code_i or p_code_r)
        if has_p:
            if is_im_code(p_code_i) or is_im_code(p_code_r):
                p_diff = False # FORCE Sesuai
            else:
                p_diff = not _match_code(p_code_i, p_code_r)
        else:
            p_diff = False
            
        p_color = '#DC2626' if p_diff else NAVY

        h_d1 = get_para_height(dx_w2[1]-6, d_desc_i, 8) if d_desc_i else 10
        h_d2 = get_para_height(dx_w2[3]-6, d_desc_r, 8) if d_desc_r else 10
        h_p1 = get_para_height(px_w2[1]-6, p_desc_i, 8) if p_desc_i else 10
        h_p2 = get_para_height(px_w2[3]-6, p_desc_r, 8) if p_desc_r else 10
        row_h = max(24, h_d1 + 10, h_d2 + 10, h_p1 + 10, h_p2 + 10)

        cursor.y = cur_yy
        cursor.check_break(row_h)
        if cursor.y < cur_yy: 
            box(17, y3, 990, 1400 - y3)
            cur_yy = cursor.y
            y3 = cursor.y

        box(17, cur_yy, 27, row_h); text(17+13, cur_yy+10, str(i+1), 9, align='center')
        
        cx = 44
        vals_d = [d_code_i, d_desc_i, d_code_r, d_desc_r, '', '', '']
        for w, val in zip(dx_w2, vals_d):
            box(cx, cur_yy, w, row_h)
            if val: para(cx+3, cur_yy+5, w-6, row_h-10, val, 8, color=d_color)
            cx += w
        if has_d:
            tick(44+72+80+76+87+5, cur_yy+8, not d_diff)
            tick(44+72+80+76+87+53, cur_yy+8, d_diff)

        cx = 522
        vals_p = [p_code_i, p_desc_i, p_code_r, p_desc_r, '', '', '']
        for w, val in zip(px_w2, vals_p):
            box(cx, cur_yy, w, row_h)
            if val: para(cx+3, cur_yy+5, w-6, row_h-10, val, 8, color=p_color)
            cx += w
        if has_p:
            tick(522+86+74+89+75+5, cur_yy+8, not p_diff)
            tick(522+86+74+89+75+53, cur_yy+8, p_diff)

        cur_yy += row_h

    cursor.y = cur_yy
    cursor.check_break(30)
    if cursor.y < cur_yy: 
        box(17, y3, 990, 1400 - y3)
        cur_yy = cursor.y
        y3 = cursor.y
        
    text(28, cur_yy+12, 'Keterangan: Teks berwarna merah menunjukkan adanya ketidaksesuaian kode (setelah mengabaikan modifier/tingkat keparahan) antara INA-CBG dan iDRG.', 9)
    box(17, y3, 990, cur_yy - y3 + 24)
    cursor.y = cur_yy + 35

    # ================= SECTION 4 =================
    cursor.check_break(250)
    y4 = cursor.y
    section(17, y4, 631, 227, '4. HASIL VALIDASI RULE OTOMATIS (KNAVP)')
    cols = [37, 72, 114, 194, 72, 53, 43, 46]
    cx = 17
    for w, t in zip(cols, ['No.', 'Rule ID\n(KNAVP)', 'Kelompok Rule', 'Deskripsi Rule / Pesan Validasi', 'Status\nTerindikasi', 'Tidak', 'Bobot', 'Skor']):
        box(cx, y4+24, w, 39, fill=PALE); para(cx+3, y4+29, w-6, 29, t, 8.8, True, align=1); cx+=w
    
    MAX_P1 = 6
    cur_y4 = y4 + 63
    for i in range(MAX_P1):
        r = rules[i] if i < len(rules) else {}
        sev = r.get('severity') or r.get('bobot') or ''
        sk = r.get('bobot') or r.get('skor') or ''
        cx = 17
        vals = [str(i+1), r.get('rule_id'), r.get('kategori') or r.get('kelompok_rule'), r.get('pesan_validasi') or r.get('nama_aturan'), '', '', sev, sk]
        for w, v in zip(cols, vals):
            box(cx, cur_y4, w, 24); para(cx+3, cur_y4+4, w-6, 16, str(v or ''), 8); cx+=w
        tick(468, cur_y4+7, bool(r)); tick(527, cur_y4+7)
        cur_y4 += 24
        
    text(28, cur_y4+8, f'(+{len(rules)-MAX_P1} rule lainnya di halaman berikutnya)' if len(rules) > MAX_P1 else 'Kolom kosong berarti tidak ada rule yang terindikasi.', 8.5, color='#c40000' if len(rules) > MAX_P1 else NAVY)

    # Risk panel
    box(660, y4, 347, 227); text(673, y4+7, 'RINGKASAN SKOR DAN RISIKO (OTOMATIS)', 12, True, TEAL)
    box(660, y4+29, 347, 198); text(674, y4+39, 'TOTAL SKOR', 13, True); text(674, y4+61, '(Jumlah bobot rule terindikasi)', 10.5)
    box(816, y4+42, 164, 37, stroke=TEAL); text(898, y4+46, str(case.get('knavp_skor', '-')), 22, True, align='center')
    text(674, y4+99, 'TINGKAT RISIKO', 13, True); text(674, y4+119, '(Otomatis)', 11)
    risk = str(case.get('tingkat_risiko') or 'Belum diisi')
    for i, (name, span) in enumerate([('Rendah', 'Skor 0-3'), ('Sedang', 'Skor 4-7'), ('Tinggi', 'Skor >= 8')]):
        tick(678, y4+139+i*20, risk.lower() == name.lower()); text(694, y4+136+i*20, name, 11); text(762, y4+137+i*20, span, 10)
    cx, cy = 909, y4+170; palette = ['#47acaa', '#8dbc45', '#cee12a', '#ffe000', '#ff9800', '#f74d1c', '#df0d16']
    for i, col in enumerate(palette):
        c.setStrokeColor(colors.HexColor(col)); c.setLineWidth(12)
        c.arc(cx*SX-60*SX, _y(cy+60), cx*SX+60*SX, _y(cy-60), startAng=180-(i+1)*180/7, extent=180/7-1)
    if risk.lower() in ('rendah', 'sedang', 'tinggi'):
        ang = math.radians({'rendah': 150, 'sedang': 90, 'tinggi': 35}[risk.lower()])
        c.setStrokeColor(colors.HexColor(NAVY)); c.setLineWidth(4)
        c.line(cx*SX, _y(cy), cx*SX+52*SX*math.cos(ang), _y(cy)+52*SY*math.sin(ang))
        c.setFillColor(colors.HexColor(NAVY)); c.circle(cx*SX, _y(cy), 6, fill=1, stroke=0)
    else: text(909, cy+9, risk, 9, align='center')
    cursor.y += 240

    # ================= SECTION 5 =================
    cursor.check_break(170)
    y5 = cursor.y
    section(17, y5, 783, 156, '5. REKOMENDASI DAN KEPUTUSAN SISTEM', 333); box(350, y5+24, 450, 132); text(32, y5+30, 'REKOMENDASI SISTEM (OTOMATIS)', 10.5, True)
    dec = str(case.get('keputusan_sistem') or '')
    for i, (label, key) in enumerate([('Monitoring (Tidak perlu tindak lanjut)', 'tidak perlu'), ('Sampling (Audit sampling)', 'sampling'), ('Direkomendasikan On-Site Audit', 'site')]):
        tick(44, y5+51+i*18, key in dec.lower()); text(64, y5+48+i*18, label, 10, color='#c40000' if i == 2 else NAVY)
    
    rekom_str = case.get('alasan_keputusan') or dec
    if 'Total Skor KNAVP' in rekom_str:
        parts = rekom_str.split('|')
        if len(parts) >= 3:
            parts[2] = f" Perbedaan Dual Coding: {diff_count}"
            rekom_str = "|".join(parts)
            
    text(43, y5+105, 'Alasan Rekomendasi Sistem:', 10); para(43, y5+122, 287, 27, rekom_str, 9)
    box(411, y5+25, 324, 21, fill=PALE); text(411+162, y5+30, 'PARAMETER REKOMENDASI SISTEM', 9, True, align='center')
    for i, (label, val) in enumerate([('Total Skor', str(case.get('knavp_skor'))), ('Jumlah Rule Terindikasi', str(len(rules))), ('Jumlah Perbedaan Dual Coding', str(diff_count)), ('Tingkat Risiko', risk), ('Keputusan Sistem', dec)]):
        box(411, y5+46+i*19, 170, 19); para(411+5, y5+46+i*19+4, 160, 11, label, 8.6)
        box(581, y5+46+i*19, 154, 19); para(581+5, y5+46+i*19+4, 144, 11, val, 8.6)
    box(800, y5, 207, 156); text(904, y5+10, 'QR CODE HASIL DESK REVIEW', 10, True, align='center'); qr_draw(866, y5+29, 78); para(823, y5+114, 166, 30, 'Identitas dokumen dan snapshot data tersimpan', 10, align=1)
    cursor.y += 170

    # ================= SECTION 6 & 7 =================
    cursor.check_break(150)
    y6 = cursor.y
    section(17, y6, 356, 137, '6. CATATAN SISTEM'); text(28, y6+28, 'Catatan / Informasi Tambahan dari Sistem:', 9.8)
    para(29, y6+49, 328, 65, form.get('catatan_sistem') or form.get('catatan_tambahan'), 10)

    section(390, y6, 617, 137, '7. VALIDASI REVIEWER')
    para(398, y6+29, 424, 35, 'Dengan ini reviewer menyatakan bahwa hasil Desk Review (validasi otomatis) telah diperiksa dan sesuai dengan output sistem.', 10)
    for i, (label, val) in enumerate([('Nama Reviewer', reviewer_name), ('NIP', nip_val), ('Tanggal Validasi', TGL_VALIDASI)]):
        field(398, y6+70+i*20, label, val, 107, 427)
    box(847, y6+25, 131, 107); text(912, y6+32, 'TTD DIGITAL REVIEWER', 9, True, align='center')
    try: qr_draw(862, y6+43, 72, json.dumps({'reviewer': reviewer_name, 'sep': sep_val, 'tgl': TGL_VALIDASI}, separators=(',', ':'))); text(912, y6+123, '(Scan / Digital Signature)', 7.5, align='center')
    except Exception: para(859, y6+60, 107, 55, 'QR tidak tersedia', 9, align=1)

    cursor.draw_footer()
    c.showPage()

    # ================= EXTRA PAGES (Rules > 6) =================
    remaining = rules[MAX_P1:]
    page_num = cursor.page + 1
    ROW_H = 18
    COLS_PTS = [(W-60)*f for f in [0.04, 0.10, 0.16, 0.42, 0.10, 0.07, 0.05, 0.06]]
    hdr_lbl = ['No.', 'Rule ID', 'Kelompok', 'Deskripsi / Pesan Validasi', 'Status', 'Tidak', 'Bobot', 'Skor']
    for chunk_start in range(0, len(remaining), 30):
        chunk = remaining[chunk_start:chunk_start+30]
        c.setFillColor(colors.HexColor('#f7faff')); c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(colors.HexColor(NAVY)); c.rect(0, H-50, W, 50, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 12); c.drawCentredString(W/2, H-32, 'KKR-DR01  -  LANJUTAN DAFTAR RULE KNAVP')
        c.setFont('Helvetica', 9); c.drawCentredString(W/2, H-46, 'SEP: ' + sep_val + '   |   Halaman ' + str(page_num))
        cur_y = H - 65; c.setFillColor(colors.HexColor(TEAL)); c.rect(30, cur_y-ROW_H, W-60, ROW_H, fill=1, stroke=0)
        xx = 30
        for w_pt, hdr in zip(COLS_PTS, hdr_lbl):
            c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 7.5); c.drawString(xx+3, cur_y-ROW_H+6, hdr); xx += w_pt
        cur_y -= ROW_H
        for j, r in enumerate(chunk, chunk_start+MAX_P1+1):
            if cur_y < 60: c.showPage(); page_num += 1; cur_y = H - 40
            fill_col = '#eef4ff' if j % 2 == 0 else '#ffffff'
            c.setFillColor(colors.HexColor(fill_col)); c.rect(30, cur_y-ROW_H, W-60, ROW_H, fill=1, stroke=0)
            sev = r.get('severity') or r.get('bobot') or ''
            sk = r.get('bobot') or r.get('skor') or ''
            vals = [str(j), str(r.get('rule_id') or ''), str(r.get('kategori') or r.get('kelompok_rule') or ''), str(r.get('pesan_validasi') or r.get('nama_aturan') or ''), 'Ya' if r else '', '', str(sev), str(sk)]
            xx = 30
            for w_pt, val in zip(COLS_PTS, vals):
                c.setFillColor(colors.HexColor(NAVY)); c.setFont('Helvetica', 7.5)
                c.drawString(xx+3, cur_y-ROW_H+6, val[:55] + '...' if len(val) > 55 else val); xx += w_pt
            cur_y -= ROW_H
        c.showPage(); page_num += 1
    c.save()
    return buf.getvalue()
