import re
def clean_dict():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    bad_string = """                "Diperlukan verifikasi tanggal lahir pasien dan kesesuaian kode dengan kelompok usia yang tepat.",
                "Temuan ini berupa ketidaksesuaian antara kode diagnosis dengan data administratif pasien "
                "(jenis kelamin atau kelompok umur). Diperlukan klarifikasi identitas pasien dan "
                "kesesuaian pengkodean dengan data rekam medis yang tersedia.",
            'age_validation':
                f"Berdasarkan hasil validasi KNAVP terhadap {len(cases)} kasus yang direviu pada {rs_name}, secara keseluruhan terdapat {total_temuan_all} temuan pelanggaran aturan. "
                f"Dari seluruh pelanggaran tersebut, kelompok temuan paling dominan adalah {dom_label} sebanyak {dom_count} temuan. "
                "Temuan ini mengindikasikan penggunaan kode diagnosis yang tidak sesuai dengan kelompok umur pasien. "
                "Diperlukan verifikasi tanggal lahir pasien dan kesesuaian kode dengan kelompok usia yang tepat.","""
                
    good_string = """                "Diperlukan verifikasi tanggal lahir pasien dan kesesuaian kode dengan kelompok usia yang tepat.","""
    
    if bad_string in content:
        content = content.replace(bad_string, good_string)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Duplicate dictionary keys cleaned up!")
    else:
        print("bad_string not found!")

if __name__ == '__main__':
    clean_dict()
