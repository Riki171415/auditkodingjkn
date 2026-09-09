import win32com.client
import os
import time
import json
from modules.db_manager import get_recap_desk_review

def update_charts():
    print("Mengupdate grafik di dalam Word (OLE Excel)...")
    recap = get_recap_desk_review()
    
    kep_counts = {'Direkomendasikan On-Site Audit': 0, 'Audit Sampling': 0, 'Lolos/Monitoring': 0}
    rule_counts = {}
    for r in recap:
        try: fd = json.loads(r.get('tindakan_reviewer') or '{}')
        except: fd = {}
        kep = fd.get('keputusan_sistem', 'Lolos/Monitoring')
        if kep in kep_counts: kep_counts[kep] += 1
        else: kep_counts['Lolos/Monitoring'] += 1
        
        triggered = r.get('triggered_rules', [])
        for rule in triggered:
            cat = rule.get('kelompok_rule', 'Lainnya')
            rule_counts[cat] = rule_counts.get(cat, 0) + 1
            
    sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    if not sorted_rules: sorted_rules = [("Tidak ada", 1)]

    word = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
    
        p = os.path.abspath('exports/word_reports/Laporan_Akhir_Nasional_V2.docx')
        doc = word.Documents.Open(p, False, False, False)
        charts = [s for s in doc.InlineShapes if s.HasChart]
        
        if len(charts) >= 4:
            # Chart 0: Top 5 Kategori Rule (Column Chart)
            wb0 = charts[0].Chart.ChartData.Workbook
            ws0 = wb0.Worksheets(1)
            ws0.Range("A2:B10").ClearContents()
            ws0.Cells(1, 1).Value = "Kategori"
            ws0.Cells(1, 2).Value = "Jumlah"
            for i, (k, v) in enumerate(sorted_rules, start=2):
                ws0.Cells(i, 1).Value = k
                ws0.Cells(i, 2).Value = v
            wb0.Close(SaveChanges=True)
            
            # Chart 1: Keputusan (Pie Chart)
            wb1 = charts[1].Chart.ChartData.Workbook
            ws1 = wb1.Worksheets(1)
            ws1.Range("A2:B10").ClearContents()
            ws1.Cells(1, 1).Value = "Keputusan"
            ws1.Cells(1, 2).Value = "Jumlah"
            for i, (k, v) in enumerate(kep_counts.items(), start=2):
                ws1.Cells(i, 1).Value = k
                ws1.Cells(i, 2).Value = v
            wb1.Close(SaveChanges=True)

            # Chart 2: Same as Chart 0
            wb2 = charts[2].Chart.ChartData.Workbook
            ws2 = wb2.Worksheets(1)
            ws2.Range("A2:B10").ClearContents()
            ws2.Cells(1, 1).Value = "Kategori"
            ws2.Cells(1, 2).Value = "Jumlah"
            for i, (k, v) in enumerate(sorted_rules, start=2):
                ws2.Cells(i, 1).Value = k
                ws2.Cells(i, 2).Value = v
            wb2.Close(SaveChanges=True)
            
            # Chart 3: Same as Chart 1
            wb3 = charts[3].Chart.ChartData.Workbook
            ws3 = wb3.Worksheets(1)
            ws3.Range("A2:B10").ClearContents()
            ws3.Cells(1, 1).Value = "Keputusan"
            ws3.Cells(1, 2).Value = "Jumlah"
            for i, (k, v) in enumerate(kep_counts.items(), start=2):
                ws3.Cells(i, 1).Value = k
                ws3.Cells(i, 2).Value = v
            wb3.Close(SaveChanges=True)
            
            print("Berhasil mengupdate 4 grafik dengan data asli.")
        else:
            print(f"Hanya ditemukan {len(charts)} grafik, update tidak dilakukan.")
            
        doc.Save()
        doc.Close()
    except Exception as e:
        print("Error:", e)
    finally:
        if word:
            word.Quit()

if __name__ == '__main__':
    update_charts()
