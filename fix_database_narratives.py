import sqlite3
import json

def fix_narratives():
    conn = sqlite3.connect('audit.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT sep, tindakan_reviewer, triggered_rules_json FROM kkr_dr01")
    rows = cur.fetchall()
    
    updated_count = 0
    for row in rows:
        sep = row['sep']
        tindakan = json.loads(row['tindakan_reviewer'] or '{}')
        rules = json.loads(row['triggered_rules_json'] or '[]')
        
        # Update all records for MVP demonstration purposes
        num_rules = len(rules)
        if num_rules == 0:
            tindakan['analisis_reviewer'] = "Tidak ditemukan anomali atau ketidaksesuaian coding pada kasus ini."
            tindakan['keputusan_reviewer'] = "Sesuai (Terbukti Valid)"
            tindakan['keputusan'] = "Sesuai (Terbukti Valid)"
            tindakan['tingkat_keyakinan'] = "Tinggi"
            tindakan['alasan_keputusan'] = "Klaim dinilai wajar dan sesuai aturan INA-CBG. Tidak ada flag audit yang terpicu."
            tindakan['alasan'] = tindakan['alasan_keputusan']
        else:
            tindakan['analisis_reviewer'] = f"Ditemukan {num_rules} potensi anomali/ketidaksesuaian (flag) yang memerlukan tinjauan lebih lanjut."
            tindakan['keputusan_reviewer'] = "Direkomendasikan On-Site Audit"
            tindakan['keputusan'] = "Direkomendasikan On-Site Audit"
            tindakan['tingkat_keyakinan'] = "Tinggi"
            tindakan['alasan_keputusan'] = "Sistem menemukan potensi ketidaksesuaian coding (flag). Direkomendasikan untuk melakukan konfirmasi rekam medis secara langsung (On-Site Audit)."
            tindakan['alasan'] = tindakan['alasan_keputusan']
            
        cur.execute("UPDATE kkr_dr01 SET tindakan_reviewer = ? WHERE sep = ?", 
                   (json.dumps(tindakan), sep))
        updated_count += 1
            
    conn.commit()
    conn.close()
    print(f"Berhasil memperbaiki narasi pada {updated_count} kasus!")

if __name__ == '__main__':
    fix_narratives()
