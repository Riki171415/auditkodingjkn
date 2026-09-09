import re

def fix_all():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Part 1: Fix the 'vs' formatting in Lampiran 1
    # Replace: f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}"
    # With a custom formatting logic.
    # We can inject a small helper before the loop.
    target_loop = """        try:
            dc_res = check_dual_coding_discrepancy(_case_dc)
            for r in dc_res.get('diag_rows', []):
                if not r.get('sesuai'):
                    diag_diff_texts.append(f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}")
            for r in dc_res.get('proc_rows', []):
                if not r.get('sesuai'):
                    proc_diff_texts.append(f"{r.get('ina_code','-')} vs {r.get('idrg_code','-')}: {r.get('keterangan','')}")
        except:"""
        
    new_loop = """        try:
            def format_dc_text(r):
                ina = r.get('ina_code') or '-'
                idrg = r.get('idrg_code') or '-'
                ket = r.get('keterangan', '')
                if ina == '-' and idrg != '-': return f"[+] {idrg} (iDRG): {ket}"
                if idrg == '-' and ina != '-': return f"[-] {ina} (INA): {ket}"
                return f"{ina} \u2192 {idrg}: {ket}"
                
            dc_res = check_dual_coding_discrepancy(_case_dc)
            for r in dc_res.get('diag_rows', []):
                if not r.get('sesuai'):
                    diag_diff_texts.append(format_dc_text(r))
            for r in dc_res.get('proc_rows', []):
                if not r.get('sesuai'):
                    proc_diff_texts.append(format_dc_text(r))
        except:"""

    if target_loop in content:
        content = content.replace(target_loop, new_loop)
        print("Replaced vs logic")
    else:
        print("Failed to replace vs logic")

    # Part 2: Add page breaks before BAB III and LAMPIRAN
    if "document.add_heading('BAB III" in content and "document.add_page_break()\n    # ── BAB III" not in content:
        content = content.replace("    # ── BAB III KESIMPULAN DAN REKOMENDASI ────────────────────────────────────\n    document.add_heading('BAB III", "    document.add_page_break()\n    # ── BAB III KESIMPULAN DAN REKOMENDASI ────────────────────────────────────\n    document.add_heading('BAB III")
        print("Added page break before BAB III")
        
    if "document.add_heading('LAMPIRAN'" in content and "document.add_page_break()\n    # ── LAMPIRAN" not in content:
        content = content.replace("    # ── LAMPIRAN ──────────────────────────────────────────────────────────────\n    document.add_heading('LAMPIRAN'", "    document.add_page_break()\n    # ── LAMPIRAN ──────────────────────────────────────────────────────────────\n    document.add_heading('LAMPIRAN'")
        print("Added page break before LAMPIRAN")

    # Let's make text paragraphs justified
    # Actually, many `add_p` calls already have `align=3` (which is WD_ALIGN_PARAGRAPH.JUSTIFY) or `align=WD_ALIGN_PARAGRAPH.JUSTIFY`.
    # Let's ensure the list items we added earlier for the "Kesesuaian Input" also have justification.
    if "p1.style = 'List Bullet'" in content:
        content = content.replace("p1.style = 'List Bullet'\n        for r in p1.runs: r.font.size = Pt(12)", "p1.style = 'List Bullet'\n        p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY\n        for r in p1.runs: r.font.size = Pt(12)")
        content = content.replace("p2.style = 'List Bullet'\n        for r in p2.runs: r.font.size = Pt(12)", "p2.style = 'List Bullet'\n        p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY\n        for r in p2.runs: r.font.size = Pt(12)")
        content = content.replace("p3.style = 'List Bullet'\n        for r in p3.runs: r.font.size = Pt(12)", "p3.style = 'List Bullet'\n        p3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY\n        for r in p3.runs: r.font.size = Pt(12)")
        print("Justified the list items in section E")

    with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_all()
