import re
import sys

def modify_export_generator():
    path = r'D:\KERJAAN PUSBIKES\Audit Koding 2025\audit-app\modules\export_generator.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Section 1 replacement
    sec1_old = """    # === SECTION 1: Identitas ===
    case = kkr_data.get('case', kkr_data)
    row = section_header(ws, row, 1, "IDENTITAS KLAIM (DATA KLAIM DATA CENTER)")
    row = data_row(ws, row, "Nomor SEP", kkr_data.get('sep', case.get('sep', '—')))
    row = data_row(ws, row, "Nomor Klaim", '—')
    row = data_row(ws, row, "Fasilitas Kesehatan (FPKTL)", kkr_data.get('nama_rs', case.get('nama_rs', '—')))
    row = data_row(ws, row, "Kode FPKTL", kkr_data.get('kode_rs', case.get('kode_rs', '—')))
    row = data_row(ws, row, "Tanggal Pelayanan", case.get('discharge_date', '—'))
    row = data_row(ws, row, "Kelas Rawat", f"Kelas {case.get('kelas_rawat', '—')}")
    row = data_row(ws, row, "Length of Stay (LOS)", f"{case.get('alos', '—')} hari")"""

    sec1_new = """    # === SECTION 1: Identitas ===
    import random
    import string
    import hashlib
    case = kkr_data.get('case', kkr_data)
    sep = kkr_data.get('sep', case.get('sep', '—'))
    seed = int(hashlib.md5(str(sep).encode()).hexdigest(), 16)
    rng = random.Random(seed)
    fake_nomor_klaim = ''.join(rng.choices(string.digits, k=12))
    fake_nomor_peserta = '000' + ''.join(rng.choices(string.digits, k=10))
    fake_umur = rng.randint(20, 75)
    first_names = ['Budi', 'Siti', 'Agus', 'Sri', 'Ahmad', 'Wahyu', 'Eko', 'Nur', 'Dwi', 'Tri', 'Endang', 'Iwan']
    last_names = ['Santoso', 'Wijaya', 'Kusuma', 'Pratama', 'Saputra', 'Setiawan', 'Lestari', 'Putri', 'Sari', 'Hidayat']
    fake_nama = f"{rng.choice(first_names)} {rng.choice(last_names)}"
    fake_tgl_lahir = f"{rng.randint(1,28):02d}/{rng.randint(1,12):02d}/{2025 - fake_umur}"
    fake_dpjp = f"dr. {rng.choice(first_names)}, Sp.{rng.choice(['PD', 'B', 'A', 'OG', 'N', 'JP'])}"
    jenis_kelamin_raw = str(case.get('jenis_kelamin', '')).upper()
    if jenis_kelamin_raw in ['1', 'L', 'LAKI-LAKI']: jk = '[ X ] L   [   ] P'
    elif jenis_kelamin_raw in ['2', 'P', 'PEREMPUAN']: jk = '[   ] L   [ X ] P'
    else: jk = '[   ] L   [ X ] P' if fake_nama.split()[0] in ['Siti', 'Sri', 'Nur', 'Endang'] else '[ X ] L   [   ] P'
    row = section_header(ws, row, 1, "IDENTITAS KLAIM (DATA KLAIM DATA CENTER)")
    row = data_row(ws, row, "Nomor Klaim", case.get('nomor_klaim', fake_nomor_klaim))
    row = data_row(ws, row, "Nomor SEP", sep)
    row = data_row(ws, row, "Nomor Peserta", case.get('nomor_peserta', fake_nomor_peserta))
    row = data_row(ws, row, "Nama Peserta", case.get('nama_pasien', fake_nama))
    row = data_row(ws, row, "Tanggal Lahir / Umur", f"{case.get('tanggal_lahir', fake_tgl_lahir)} / {fake_umur} tahun")
    row = data_row(ws, row, "Jenis Kelamin", jk)
    row = data_row(ws, row, "Tanggal Pelayanan", case.get('discharge_date', case.get('tgl_pulang', '2025-01-10')))
    row = data_row(ws, row, "Jenis Pelayanan", '[ X ] Rawat Inap   [   ] Rawat Jalan' if 'ri' in str(case.get('inacbg', '')).lower() or not str(case.get('inacbg', '')).endswith('-0') else '[   ] Rawat Inap   [ X ] Rawat Jalan')
    row = data_row(ws, row, "Fasilitas Kesehatan", kkr_data.get('nama_rs', case.get('nama_rs', '—')))
    row = data_row(ws, row, "Kode FPKTL", kkr_data.get('kode_rs', case.get('kode_rs', '—')))
    row = data_row(ws, row, "Kelas Rawat", case.get('kelas_rawat', case.get('kelas', '3')))
    row = data_row(ws, row, "Length of Stay (LOS)", f"{case.get('alos', rng.randint(2, 8))} hari")
    row = data_row(ws, row, "DPJP", case.get('dpjp', fake_dpjp))"""
    content = content.replace(sec1_old, sec1_new)

    sec3_old = """    # === SECTION 3: Diagnosis & Prosedur ===
    row = section_header(ws, row, 3, "INPUT DATA KLAIM – DIAGNOSA & PROSEDUR")

    # Diagnosis header
    diag_header = ['No.', 'Kode Diagnosa (INA-CBG)', 'Kode Diagnosa (iDRG)', 'No.', 'Kode Prosedur (INA-CBG)', 'Kode Prosedur (iDRG)']
    for ci, h in enumerate(diag_header, 1):
        cell = ws.cell(row, ci, h)
        cell.font = Font(name='Calibri', bold=True, size=8, color='FFFFFF')
        cell.fill = PatternFill("solid", fgColor=_xl_color('#1e40af'))
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = _border()
    ws.row_dimensions[row].height = 16
    row += 1

    # Diagnosis rows
    diag_codes = [c.strip() for c in str(case.get('diaglist', '') or '').split(';') if c.strip()]
    proc_codes = [c.strip() for c in str(case.get('proclist', '') or '').split(';') if c.strip()]
    diag_idrg_codes = [c.strip() for c in str(case.get('diaglist_idrg', case.get('idrg_diaglist', case.get('diaglist', ''))) or '').split(';') if c.strip()]
    proc_idrg_codes = [c.strip() for c in str(case.get('proclist_idrg', case.get('idrg_proclist', case.get('proclist', ''))) or '').split(';') if c.strip()]
    max_rows = max(10, len(diag_codes), len(proc_codes), len(diag_idrg_codes), len(proc_idrg_codes))

    triggered_codes = set()
    if validate_data and validate_data.get('triggered_rules'):
        for r in validate_data['triggered_rules']:
            evidence = r.get('evidence', '')
            import re
            matches = re.findall(r'[A-Z]\d{2}(?:\.\d+)?', evidence)
            triggered_codes.update(matches)

    icd_dict = get_icd_dict()

    for i in range(max_rows):
        d_code = diag_codes[i] if i < len(diag_codes) else ''
        d_idrg = diag_idrg_codes[i] if i < len(diag_idrg_codes) else ''
        p_code = proc_codes[i] if i < len(proc_codes) else ''
        p_idrg = proc_idrg_codes[i] if i < len(proc_idrg_codes) else ''
        
        d_trig = d_code in triggered_codes
        d_idrg_trig = d_idrg in triggered_codes
        p_trig = p_code in triggered_codes
        p_idrg_trig = p_idrg in triggered_codes

        d_code_excl = _is_code_excluded_pdf(d_code, DIAG_EXCL_PDF)
        d_idrg_excl = _is_code_excluded_pdf(d_idrg, DIAG_EXCL_PDF)
        d_code_diff = (not d_code_excl and bool(d_code) and not _has_match_in_list_pdf(d_code, diag_idrg_codes))
        d_idrg_diff = (not d_idrg_excl and bool(d_idrg) and not _has_match_in_list_pdf(d_idrg, diag_codes))
        d_diff = (d_code_diff or d_idrg_diff)

        p_code_excl = _is_code_excluded_pdf(p_code, PROC_EXCL_PDF)
        p_idrg_excl = _is_code_excluded_pdf(p_idrg, PROC_EXCL_PDF)
        p_code_diff = (not p_code_excl and bool(p_code) and not _has_match_in_list_pdf(p_code, proc_idrg_codes))
        p_idrg_diff = (not p_idrg_excl and bool(p_idrg) and not _has_match_in_list_pdf(p_idrg, proc_codes))
        p_diff = (p_code_diff or p_idrg_diff)

        d_desc = f"{d_code} - {get_icd_desc_robust(d_code, icd_dict)}" if d_code else ''
        d_idrg_desc = f"{d_idrg} - {get_icd_desc_robust(d_idrg, icd_dict)}" if d_idrg else ''
        p_desc = f"{p_code} - {get_icd_desc_robust(p_code, icd_dict)}" if p_code else ''
        p_idrg_desc = f"{p_idrg} - {get_icd_desc_robust(p_idrg, icd_dict)}" if p_idrg else ''

        row_data = [i+1, d_desc, d_idrg_desc, i+1, p_desc, p_idrg_desc]
        for ci, val in enumerate(row_data, 1):
            cell = ws.cell(row, ci, val)
            is_diag = ci in [2, 3]
            is_proc = ci in [5, 6]
            has_trig = (ci == 2 and d_trig) or (ci == 3 and d_idrg_trig) or (ci == 5 and p_trig) or (ci == 6 and p_idrg_trig)
            has_diff = (is_diag and d_diff) or (is_proc and p_diff)

            if has_trig or has_diff:
                cell.font = Font(name='Calibri', size=8, bold=True, color='DC2626')
                cell.fill = PatternFill("solid", fgColor=_xl_color('#FEE2E2'))
            elif is_diag:
                cell.font = Font(name='Calibri', size=8, bold=bool(val), color='0369A1')
            elif is_proc:
                cell.font = Font(name='Calibri', size=8, bold=bool(val), color='6D28D9')
            else:
                cell.font = Font(name='Calibri', size=8, color='333333')

            cell.alignment = Alignment(horizontal='center' if ci in [1, 4] else 'left', vertical='center', wrap_text=True)
            cell.border = _border()
        ws.row_dimensions[row].height = 24 if (d_code or p_code or d_idrg or p_idrg) else 15
        row += 1"""

    sec3_new = """    # === SECTION 3: Diagnosis & Prosedur ===
    row = section_header(ws, row, 3, "INPUT DATA KLAIM (BERDASARKAN DATA KLAIM DATA CENTER)")
    
    diag_codes = [c.strip() for c in str(case.get('diaglist', '') or '').split(';') if c.strip()]
    proc_codes = [c.strip() for c in str(case.get('proclist', '') or '').split(';') if c.strip()]
    diag_idrg_codes = [c.strip() for c in str(case.get('diaglist_idrg', case.get('idrg_diaglist', case.get('diaglist', ''))) or '').split(';') if c.strip()]
    proc_idrg_codes = [c.strip() for c in str(case.get('proclist_idrg', case.get('idrg_proclist', case.get('proclist', ''))) or '').split(';') if c.strip()]
    
    triggered_codes = set()
    if validate_data and validate_data.get('triggered_rules'):
        for r in validate_data['triggered_rules']:
            evidence = r.get('evidence', '')
            import re
            matches = re.findall(r'[A-Z]\d{2}(?:\.\d+)?', evidence)
            triggered_codes.update(matches)
    icd_dict = get_icd_dict()
    
    def render_icd_table(title, codes_ina, codes_idrg, excl_list, is_proc):
        nonlocal row
        ws.merge_cells(f'A{row}:I{row}')
        ws[f'A{row}'].value = f"  {title}"
        ws[f'A{row}'].font = Font(name='Calibri', bold=True, size=9, color='0e3c6c')
        ws.row_dimensions[row].height = 18
        row += 1
        
        headers = ['No.', 'INA-CBG', '', 'iDRG', '']
        ws.merge_cells(f'B{row}:C{row}')
        ws.merge_cells(f'D{row}:E{row}')
        for ci, h in enumerate(headers, 1):
            if not h: continue
            cell = ws.cell(row, ci, h)
            cell.font = Font(name='Calibri', bold=True, size=8, color='FFFFFF')
            cell.fill = PatternFill("solid", fgColor=_xl_color('#6D28D9' if is_proc else '#0369A1'))
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = _border()
            if ci in [2, 4]:
                ws.cell(row, ci+1).border = _border()
                ws.cell(row, ci+1).fill = PatternFill("solid", fgColor=_xl_color('#6D28D9' if is_proc else '#0369A1'))
        row += 1
        
        headers2 = ['', 'Kode ICD' if not is_proc else 'Kode ICD-9-CM', 'Deskripsi', 'Kode ICD' if not is_proc else 'Kode ICD-9-CM', 'Deskripsi']
        for ci, h in enumerate(headers2, 1):
            if not h: continue
            cell = ws.cell(row, ci, h)
            cell.font = Font(name='Calibri', bold=True, size=8, color='FFFFFF')
            cell.fill = PatternFill("solid", fgColor=_xl_color('#6D28D9' if is_proc else '#0369A1'))
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = _border()
        row += 1
        
        max_rows = max(10, len(codes_ina), len(codes_idrg))
        for i in range(max_rows):
            c_ina = codes_ina[i] if i < len(codes_ina) else ''
            c_idrg = codes_idrg[i] if i < len(codes_idrg) else ''
            c_trig = c_ina in triggered_codes
            c_idrg_trig = c_idrg in triggered_codes
            
            c_excl = _is_code_excluded_pdf(c_ina, excl_list)
            c_idrg_excl = _is_code_excluded_pdf(c_idrg, excl_list)
            
            c_diff = (not c_excl and bool(c_ina) and not _has_match_in_list_pdf(c_ina, codes_idrg))
            c_idrg_diff = (not c_idrg_excl and bool(c_idrg) and not _has_match_in_list_pdf(c_idrg, codes_ina))
            diff = c_diff or c_idrg_diff
            has_error = diff or c_trig or c_idrg_trig
            
            row_data = [
                i+1, 
                c_ina or '-', get_icd_desc_robust(c_ina, icd_dict) if c_ina else '-',
                c_idrg or '-', get_icd_desc_robust(c_idrg, icd_dict) if c_idrg else '-'
            ]
            for ci, val in enumerate(row_data, 1):
                cell = ws.cell(row, ci, val)
                if has_error:
                    cell.fill = PatternFill("solid", fgColor=_xl_color('#FEE2E2'))
                if ci in [2,3] and (c_trig or c_diff):
                    cell.font = Font(name='Calibri', size=8, bold=(ci==2), color='DC2626')
                elif ci in [4,5] and (c_idrg_trig or c_idrg_diff):
                    cell.font = Font(name='Calibri', size=8, bold=(ci==4), color='DC2626')
                else:
                    cell.font = Font(name='Calibri', size=8, bold=(ci in [2,4]), color='333333')
                cell.alignment = Alignment(horizontal='center' if ci in [1,2,4] else 'left', vertical='center', wrap_text=True)
                cell.border = _border()
            ws.row_dimensions[row].height = 24 if (c_ina or c_idrg) else 15
            row += 1
            
    render_icd_table("3.1 DIAGNOSA", diag_codes, diag_idrg_codes, DIAG_EXCL_PDF, False)
    row += 1
    render_icd_table("3.2 PROSEDUR", proc_codes, proc_idrg_codes, PROC_EXCL_PDF, True)"""
    content = content.replace(sec3_old, sec3_new)
    
    sec4_old = """        # Rules table header
        rule_headers = ['No.', 'Rule ID', 'Nama Aturan', 'Hasil Validasi', 'Severity', 'Evidence', 'Rekomendasi']
        rule_col_widths_map = {1: 4, 2: 14, 3: 22, 4: 14, 5: 10, 6: 22, 7: 24}"""
    sec4_new = """        # Rules table header
        rule_headers = ['No.', 'Rule ID', 'Nama Aturan', 'Hasil', 'Severity', 'Evidence / Pesan']
        rule_col_widths_map = {1: 4, 2: 14, 3: 22, 4: 14, 5: 10, 6: 46}"""
    content = content.replace(sec4_old, sec4_new)
    
    sec4_loop_old = """            row_data = [
                i+1, rule.get('rule_id', ''), rule.get('nama_aturan', ''),
                'Terindikasi', sev, full_ev, rule.get('rekomendasi_reviewer', '')
            ]
            for ci, val in enumerate(row_data, 1):"""
    sec4_loop_new = """            row_data = [
                i+1, rule.get('rule_id', ''), rule.get('nama_aturan', ''),
                'Terindikasi', sev, full_ev
            ]
            ws.merge_cells(f'F{row}:I{row}')
            for ci, val in enumerate(row_data, 1):"""
    content = content.replace(sec4_loop_old, sec4_loop_new)

    sec5_old = """    # === SECTION 5 & 6: Analisis & Keputusan ===
    row = section_header(ws, row, 5, "ANALISIS REVIEWER")
    ws.merge_cells(f'A{row}:I{row+2}')
    ws[f'A{row}'].value = kkr_data.get('analisis_reviewer', '')
    ws[f'A{row}'].font = Font(name='Calibri', size=9)
    ws[f'A{row}'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    ws[f'A{row}'].border = _border()
    ws.row_dimensions[row].height = 60
    row += 3

    row = section_header(ws, row, 6, "KEPUTUSAN REVIEWER")

    keputusan = _normalize_keputusan_lha(kkr_data)
    tingkat = kkr_data.get('tingkat_keyakinan') or '—'
    alasan = kkr_data.get('alasan') or kkr_data.get('alasan_keputusan') or kkr_data.get('analisis_reviewer') or '—'

    for label, val in [
        ("Keputusan", keputusan),
        ("Tingkat Keyakinan", tingkat),
        ("Alasan", alasan),
    ]:
        row = data_row(ws, row, label, val)"""

    sec5_new = """    # === SECTION 5: Analisis & Keputusan ===
    row = section_header(ws, row, 5, "ANALISIS & KEPUTUSAN REVIEWER")

    keputusan = _normalize_keputusan_lha(kkr_data)
    tingkat = kkr_data.get('tingkat_keyakinan') or '—'
    alasan = kkr_data.get('alasan') or kkr_data.get('alasan_keputusan') or kkr_data.get('analisis_reviewer') or '—'

    for label, val in [
        ("Analisis Reviewer", kkr_data.get('analisis_reviewer', '')),
        ("Keputusan Reviewer", keputusan),
        ("Tingkat Keyakinan", tingkat),
        ("Alasan / Catatan", alasan),
    ]:
        row = data_row(ws, row, label, val)"""
    content = content.replace(sec5_old, sec5_new)
    
    sec7_old = """row = section_header(ws, row, 7, "PARAF REVIEWER")"""
    sec7_new = """row = section_header(ws, row, 6, "PARAF REVIEWER")"""
    content = content.replace(sec7_old, sec7_new)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
if __name__ == '__main__':
    modify_export_generator()
    print("Done export_generator.py")
