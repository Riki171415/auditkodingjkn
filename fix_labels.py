import sys

def fix_chart_labels():
    with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/modules/report_word.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    old_charts = "    charts = [(['Direview','Dengan alert'], [stats['total'],stats['cases_with_alerts']]),\n              (['On-Site','Sampling','Monitoring','Belum tersedia'], [stats[k] for k in ('onsite','sampling','monitoring','unknown')]),\n              (list(categories) or ['Tidak ada alert'], list(categories.values()) or [0]),\n              (['Ada perbedaan tersimpan','Tanpa perbedaan tersimpan'],[stats['dc_cases'],stats['total']-stats['dc_cases']])]"
    
    new_charts = "    charts = [(['Total Sampel'], [stats['total']]),\n              (['On-Site Audit','Audit Sampling','Monitoring/Lolos'], [stats['onsite'],stats['sampling'],stats['monitoring']]),\n              (list(categories) or ['Tidak ada alert'], list(categories.values()) or [0]),\n              (['Mismatch','Sinkron'],[stats['dc_cases'],stats['total']-stats['dc_cases']])]"
    
    if old_charts in code:
        code = code.replace(old_charts, new_charts)
        with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/modules/report_word.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("Chart labels fixed!")
    else:
        print("Could not find old charts definition.")

fix_chart_labels()
