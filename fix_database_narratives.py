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
            tindakan['keputusan_reviewer'] = "Tidak diperlukan tindak lanjut"
            tindakan['keputusan'] = "Tidak diperlukan tindak lanjut"
            tindakan['tingkat_keyakinan'] = "Tinggi"
            tindakan['alasan_keputusan'] = "Klaim dinilai wajar dan sesuai aturan INA-CBG. Tidak ada flag audit yang terpicu."
            tindakan['alasan'] = tindakan['alasan_keputusan']
        else:
            # Check if any triggered rule explicitly recommends On-Site
            requires_onsite = False
            for r in rules:
                rek = r.get('rekomendasi_reviewer', '').lower()
                if 'on-site' in rek or 'onsite' in rek:
                    requires_onsite = True
                    break
            
            tindakan['analisis_reviewer'] = f"Ditemukan {num_rules} potensi anomali/ketidaksesuaian (flag) yang memerlukan tinjauan lebih lanjut."
            
            if requires_onsite:
                tindakan['keputusan_reviewer'] = "Direkomendasikan On-Site Audit"
                tindakan['keputusan'] = "Direkomendasikan On-Site Audit"
                tindakan['tingkat_keyakinan'] = "Tinggi"
                tindakan['alasan_keputusan'] = "Sistem menemukan aturan yang secara spesifik merekomendasikan konfirmasi rekam medis secara langsung (On-Site Audit)."
                tindakan['alasan'] = tindakan['alasan_keputusan']
            else:
                tindakan['keputusan_reviewer'] = "Perlu Monitoring"
                tindakan['keputusan'] = "Perlu Monitoring"
                tindakan['tingkat_keyakinan'] = "Tinggi"
                tindakan['alasan_keputusan'] = "Sistem menemukan potensi ketidaksesuaian coding, namun aturan tidak mewajibkan On-Site Audit. Direkomendasikan untuk melakukan monitoring."
                tindakan['alasan'] = tindakan['alasan_keputusan']
            
        cur.execute("UPDATE kkr_dr01 SET tindakan_reviewer = ? WHERE sep = ?", 
                   (json.dumps(tindakan), sep))
        updated_count += 1
            
    conn.commit()
    conn.close()
    print(f"Berhasil memperbaiki narasi pada {updated_count} kasus!")

if __name__ == '__main__':
    fix_narratives()
