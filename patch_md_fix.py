import re

def patch_report_word():
    with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/modules/report_word.py', 'r', encoding='utf-8') as f:
        code = f.read()

    target = "md_text = md_path.read_text(encoding='utf-8')"
    replacement = '''md_text = md_path.read_text(encoding='utf-8')
        
        # FIX AI HALLUCINATIONS/STALE DATA IN NARRATIVE TEXT:
        # Per-RS reports exact sentence replacement
        if not national:
            pattern = r'Hasil penilaian risiko menunjukkan bahwa dari \d+ kasus sampel, sebanyak \d+ kasus direkomendasikan untuk On-Site Audit, \d+ kasus untuk Audit Sampling, dan \d+ kasus dinyatakan dapat dimonitoring secara berkala\.'
            repl = f'Hasil penilaian risiko menunjukkan bahwa dari {stats["total"]} kasus sampel, sebanyak {stats["onsite"]} kasus direkomendasikan untuk On-Site Audit, {stats["sampling"]} kasus untuk Audit Sampling, dan {stats["monitoring"]} kasus dinyatakan dapat dimonitoring secara berkala.'
            md_text = re.sub(pattern, repl, md_text, flags=re.IGNORECASE)
            
        # National report replacements
        if national:
            md_text = re.sub(r'teridentifikasinya \d+ kasus klaim yang direkomendasikan secara tegas untuk dilakukan \*On-Site Audit\*', f'teridentifikasinya {stats["onsite"]} kasus klaim yang direkomendasikan secara tegas untuk dilakukan *On-Site Audit*', md_text)
            md_text = re.sub(r'keberadaan \d+ kasus \*Audit Sampling\* dan \d+ kasus \*On-Site Audit\*', f'keberadaan {stats["sampling"]} kasus *Audit Sampling* dan {stats["onsite"]} kasus *On-Site Audit*', md_text)
            md_text = re.sub(r'sebanyak \d+ kasus terbukti Lolos/Monitoring, namun ditemukan \d+ kasus yang memerlukan \*Audit Sampling\* serta \d+ kasus berdampak tinggi yang direkomendasikan untuk tindakan penelusuran \*On-Site Audit\*', f'sebanyak {stats["monitoring"]} kasus terbukti Lolos/Monitoring, namun ditemukan {stats["sampling"]} kasus yang memerlukan *Audit Sampling* serta {stats["onsite"]} kasus berdampak tinggi yang direkomendasikan untuk tindakan penelusuran *On-Site Audit*', md_text)
            md_text = re.sub(r'mengidentifikasi sebanyak \d+ kasus diskrepansi \*dual coding\*', f'mengidentifikasi sebanyak {stats["dc_cases"]} kasus diskrepansi *dual coding*', md_text)
            md_text = re.sub(r'Temuan \d+ kasus diskrepansi ini', f'Temuan {stats["dc_cases"]} kasus diskrepansi ini', md_text)
'''

    if target in code and "FIX AI HALLUCINATIONS" not in code:
        code = code.replace(target, replacement)
        with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/modules/report_word.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("report_word.py patched successfully!")
    else:
        print("Target string not found or already patched.")

patch_report_word()
