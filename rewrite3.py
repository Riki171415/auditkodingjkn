import os

with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('    dom_kat, dom_count = max(rule_counts')
end_idx = content.find('    add_p(_narasi_map.get(dom_kat, _default_narasi)')

new_logic = '''    dom_kat, dom_count = max(rule_counts.items(), key=lambda x: x[1]) if rule_counts else ("-", 0)
    dom_label = dom_kat
    if dom_kat != "-":
        dom_label = GROUPED_RULES.get(dom_kat, {}).get('title', dom_kat)

    total_temuan_all = sum(rule_counts.values())
    sorted_rules = sorted([(GROUPED_RULES.get(k, {}).get('title', k), v) for k, v in rule_counts.items() if v > 0], key=lambda x: x[1], reverse=True)
    
    if total_temuan_all > 0:
        top_rules = [k for k, v in sorted_rules if v == sorted_rules[0][1]]
        if len(top_rules) > 1:
            dominant_str = " dan ".join([", ".join(top_rules[:-1]), top_rules[-1]]) if len(top_rules) > 2 else " dan ".join(top_rules)
            dominant_count_str = f"masing-masing sebanyak {sorted_rules[0][1]} temuan"
        else:
            dominant_str = top_rules[0]
            dominant_count_str = f"sebanyak {sorted_rules[0][1]} temuan"
            
        other_rules = [f"{k} sebanyak {v} temuan" for k, v in sorted_rules if v < sorted_rules[0][1]]
        if other_rules:
            if len(other_rules) > 1:
                other_str = ", diikuti oleh " + ", ".join(other_rules[:-1]) + " dan " + other_rules[-1]
            else:
                other_str = ", diikuti oleh " + other_rules[0]
        else:
            other_str = ""
            
        intro_text = f"Berdasarkan hasil validasi KNAVP terhadap {len(cases)} kasus yang direviu pada {rs_name}, secara keseluruhan terdapat {total_temuan_all} temuan pelanggaran aturan. Dari seluruh pelanggaran tersebut, kelompok temuan yang paling dominan adalah {dominant_str} dengan {dominant_count_str}{other_str}. "
    else:
        intro_text = f"Berdasarkan hasil validasi KNAVP terhadap {len(cases)} kasus yang direviu pada {rs_name}, tidak ditemukan adanya pelanggaran aturan. Kesesuaian pengodean sudah cukup baik dan perlu dipertahankan sesuai panduan ICS dan kaidah koding nasional yang berlaku. "

    _narasi_map = {
        'mutually_exclusive':
            intro_text + "Temuan ini mengindikasikan pengkodean diagnosis yang secara eksplisit sudah termasuk (Includes) atau "
            "dikecualikan (Excludes) dalam kode lain, sehingga tidak seharusnya dikode secara bersamaan. "
            "Diperlukan penelusuran kaidah Includes/Excludes dalam ICD-10 dan ICS.",
        'underlying_manifestation':
            intro_text + "Temuan ini mengindikasikan kode manifestasi yang digunakan tanpa underlying cause yang tepat, "
            "atau underlying cause yang tidak sesuai pasangan manifestasinya. "
            "Kondisi ini berpotensi mempengaruhi akurasi grouping dan tingkat keparahan (CCL/PCCL).",
        'procedure_validation':
            intro_text + "Temuan ini mengindikasikan adanya tindakan/prosedur medis yang dikodekan tanpa didukung diagnosis indikasi "
            "yang sesuai, atau sebaliknya. Diperlukan verifikasi laporan operasi dan bukti klinis "
            "untuk memastikan kesesuaian kode prosedur dengan kondisi pasien yang sebenarnya.",
        'unbundling':
            intro_text + "Temuan ini mengindikasikan pemecahan (unbundling) paket tindakan yang seharusnya sudah tercakup dalam satu "
            "kode prosedur utama, sehingga diklaim sebagai tindakan terpisah. "
            "Diperlukan verifikasi terhadap rekam medis dan laporan tindakan untuk memastikan "
            "tidak terjadi double-billing atas komponen tindakan yang sudah termasuk dalam paket.",
        'medical_evidence':
            intro_text + "Temuan ini mengindikasikan kode diagnosis berbobot tinggi (komplikasi/komorbiditas) yang diklaim "
            "tanpa didukung bukti klinis/laboratorium yang memadai dalam rekam medis. "
            "Diperlukan On-Site Audit untuk memverifikasi kelengkapan dokumentasi klinis.",
        'administrative_validation':
            intro_text + "Temuan ini berupa ketidaksesuaian antara kode diagnosis dengan data administratif pasien "
            "(jenis kelamin atau kelompok umur). Diperlukan klarifikasi identitas pasien dan "
            "kesesuaian pengkodean dengan data rekam medis yang tersedia.",
        'age_validation':
            intro_text + "Temuan ini mengindikasikan penggunaan kode diagnosis yang tidak sesuai dengan kelompok umur pasien. "
            "Diperlukan verifikasi tanggal lahir pasien dan kesesuaian kode dengan kelompok usia yang tepat.",
        'los_validation':
            intro_text + "Temuan ini mengindikasikan lama rawat (LOS) yang melebihi ambang batas kewajaran "
            "berdasarkan perbandingan dengan ALOS nasional dan CMI rumah sakit ini. "
            "Diperlukan verifikasi klinis untuk memastikan bahwa perpanjangan masa rawat memiliki "
            "justifikasi medis yang terdokumentasi dalam rekam medis.",
    }
    _default_narasi = (
        intro_text + "Temuan-temuan ini memerlukan klarifikasi lebih lanjut terhadap rekam medis dan pengkodean "
        "sesuai panduan ICS dan kaidah koding nasional yang berlaku."
    )
'''

content = content[:start_idx] + new_logic + content[end_idx:]

with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)
