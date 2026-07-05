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
        
        # Check if this is an auto-generated row
        analisis = tindakan.get('analisis_reviewer', '')
        if 'Auto-Logic' in str(analisis) or 'Di-generate otomatis' in str(analisis) or not analisis:
            
            num_rules = len(rules)
            if num_rules == 0:
                tindakan['analisis_reviewer'] = "Analisis sistem (Otomatis): Tidak ditemukan anomali atau ketidaksesuaian coding pada kasus ini."
                tindakan['keputusan_reviewer'] = "Sesuai (Terbukti Valid)"
                tindakan['keputusan'] = "Sesuai (Terbukti Valid)"
                tindakan['tingkat_keyakinan'] = "Tinggi (Sistem/Otomatis)"
                tindakan['alasan_keputusan'] = "Klaim dinilai wajar dan sesuai aturan INA-CBG. Tidak ada flag audit yang terpicu."
                tindakan['alasan'] = tindakan['alasan_keputusan']
            else:
                tindakan['analisis_reviewer'] = f"Analisis sistem (Otomatis): Ditemukan {num_rules} potensi anomali/ketidaksesuaian (flag) yang memerlukan tinjauan lebih lanjut."
                tindakan['keputusan_reviewer'] = "Menunggu Review Manual"
                tindakan['keputusan'] = "Menunggu Review Manual"
                tindakan['tingkat_keyakinan'] = "Menunggu Review"
                tindakan['alasan_keputusan'] = "Memerlukan peninjauan lebih lanjut oleh auditor untuk memastikan validitas temuan sistem."
                tindakan['alasan'] = tindakan['alasan_keputusan']
                
            cur.execute("UPDATE kkr_dr01 SET tindakan_reviewer = ? WHERE sep = ?", 
                       (json.dumps(tindakan), sep))
            updated_count += 1
            
    conn.commit()
    conn.close()
    print(f"Berhasil memperbaiki narasi pada {updated_count} kasus!")

if __name__ == '__main__':
    fix_narratives()
