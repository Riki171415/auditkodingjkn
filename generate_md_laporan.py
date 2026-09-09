import os
import json
from collections import defaultdict
from modules.db_manager import get_recap_desk_review

def generate_md_report(nama_rs_filter="ADAM MALIK"):
    recap = get_recap_desk_review()
    
    # Filter for RS
    rs_cases = [r for r in recap if r.get('nama_rs') and nama_rs_filter.upper() in r.get('nama_rs', '').upper()]
    if not rs_cases:
        print(f"Tidak ada data untuk RS dengan nama: {nama_rs_filter}")
        return
    
    nama_rs = rs_cases[0]['nama_rs']
    kode_rs = rs_cases[0]['kode_rs']
    
    total_kasus = len(rs_cases)
    rawat_inap = sum(1 for c in rs_cases if 'ri' in str(c.get('inacbg', '')).lower() or not str(c.get('inacbg', '')).endswith('-0'))
    rawat_jalan = total_kasus - rawat_inap
    
    # Validation Results
    rules_counts = defaultdict(int)
    
    for case in rs_cases:
        triggered = case.get('triggered_rules', [])
        for rule in triggered:
            kelompok = rule.get('kelompok_rule', 'Lainnya')
            if not kelompok:
                kelompok = 'Lainnya'
            rules_counts[kelompok] += 1
                
    kasus_prioritas = []
    for case in rs_cases:
        fd = {}
        try:
            if case.get('tindakan_reviewer'):
                fd = json.loads(case['tindakan_reviewer'])
        except:
            pass
            
        keputusan = fd.get('keputusan_sistem', '')
        if keputusan == 'Direkomendasikan On-Site Audit':
            rules = case.get('triggered_rules', [])
            rule_str = ", ".join([r.get('rule_id', '') for r in rules])
            if not rule_str:
                rule_str = "-"
            kasus_prioritas.append({
                'sep': case['sep'],
                'rule': rule_str,
                'prioritas': fd.get('tingkat_risiko', 'Tinggi'),
                'rekomendasi': 'On-Site Audit'
            })
            
    # Markdown output
    md_content = f"# BAB II\n# HASIL DESK REVIEW\n\n"
    md_content += f"## A. Gambaran Data\n\n"
    md_content += f"| Uraian | Jumlah |\n"
    md_content += f"|---|---|\n"
    md_content += f"| Total Kasus | {total_kasus} |\n"
    md_content += f"| Rawat Jalan | {rawat_jalan} |\n"
    md_content += f"| Rawat Inap | {rawat_inap} |\n"
    md_content += f"| Total Kasus Direview | {total_kasus} |\n\n"
    
    md_content += f"## B. Hasil Validasi\n\n"
    md_content += f"| Kelompok Aturan | Jumlah Temuan |\n"
    md_content += f"|---|---|\n"
    
    if not rules_counts:
        md_content += f"| Tidak ada temuan | 0 |\n"
    else:
        for rule_name, count in rules_counts.items():
            md_content += f"| {rule_name} | {count} |\n"
    md_content += "\n"
    
    md_content += f"## C. Analisis Temuan\n\n"
    
    total_temuan = sum(rules_counts.values())
    sorted_rules = sorted([(k, v) for k, v in rules_counts.items() if v > 0], key=lambda x: x[1], reverse=True)
    
    if total_temuan > 0:
        top_rules = [f"*{k}*" for k, v in sorted_rules if v == sorted_rules[0][1]]
        if len(top_rules) > 1:
            dominant_str = " dan ".join([", ".join(top_rules[:-1]), top_rules[-1]]) if len(top_rules) > 2 else " dan ".join(top_rules)
            dominant_count_str = f"masing-masing sebanyak {sorted_rules[0][1]} temuan"
        else:
            dominant_str = top_rules[0]
            dominant_count_str = f"sebanyak {sorted_rules[0][1]} temuan"
            
        other_rules = [f"*{k}* sebanyak {v} temuan" for k, v in sorted_rules if v < sorted_rules[0][1]]
        
        if other_rules:
            if len(other_rules) > 1:
                other_str = ", diikuti oleh " + ", ".join(other_rules[:-1]) + " dan " + other_rules[-1]
            else:
                other_str = ", diikuti oleh " + other_rules[0]
        else:
            other_str = ""
            
        md_content += f"Berdasarkan hasil validasi KNAVP terhadap {total_kasus} kasus yang direviu pada {nama_rs}, secara keseluruhan terdapat {total_temuan} temuan pelanggaran aturan. Dari seluruh pelanggaran tersebut, kelompok temuan yang paling dominan adalah {dominant_str} dengan {dominant_count_str}{other_str}. Temuan-temuan ini memerlukan klarifikasi lebih lanjut terhadap rekam medis dan pengkodean sesuai panduan ICS dan kaidah koding nasional yang berlaku.\n\n"
    else:
        md_content += f"Berdasarkan hasil validasi KNAVP terhadap {total_kasus} kasus yang direviu pada {nama_rs}, tidak ditemukan adanya pelanggaran aturan. Kesesuaian pengodean sudah cukup baik dan perlu dipertahankan sesuai panduan ICS dan kaidah koding nasional yang berlaku.\n\n"
    
    md_content += f"## D. Kasus Prioritas\n\n"
    md_content += f"| No | Nomor SEP | Rule | Prioritas | Rekomendasi |\n"
    md_content += f"|---|---|---|---|---|\n"
    for i, p in enumerate(kasus_prioritas, 1):
        md_content += f"| {i} | {p['sep']} | {p['rule']} | {p['prioritas']} | {p['rekomendasi']} |\n"
    if not kasus_prioritas:
        md_content += f"| - | - | - | - | - |\n"
    md_content += "\n"
    
    discrepancy_count = 0
    total_diff_codes = 0
    lampiran_rows = []
    
    for i, case in enumerate(rs_cases, 1):
        fd = {}
        try:
            if case.get('tindakan_reviewer'):
                fd = json.loads(case['tindakan_reviewer'])
        except:
            pass
            
        diff_count = int(fd.get('jumlah_beda_dual_coding', 0) or 0)
        if diff_count > 0:
            discrepancy_count += 1
            total_diff_codes += diff_count
            
        diag_ina = [c.strip() for c in str(case.get('diaglist', '') or '').split(';') if c.strip()]
        diag_idrg = [c.strip() for c in str(case.get('diaglist_idrg', case.get('idrg_diaglist', case.get('diaglist', ''))) or '').split(';') if c.strip()]
        proc_ina = [c.strip() for c in str(case.get('proclist', '') or '').split(';') if c.strip()]
        proc_idrg = [c.strip() for c in str(case.get('proclist_idrg', case.get('idrg_proclist', case.get('proclist', ''))) or '').split(';') if c.strip()]
        
        diag_diff = list(set(diag_ina) ^ set(diag_idrg))
        proc_diff = list(set(proc_ina) ^ set(proc_idrg))
        
        diag_str = ", ".join(diag_diff) if diag_diff else "Sesuai"
        proc_str = ", ".join(proc_diff) if proc_diff else "Sesuai"
        lampiran_rows.append(f"| {i} | {case['sep']} | {case.get('deskripsi_inacbg', '-')} | {diag_str} | {proc_str} |\n")
        
    sesuai_count = total_kasus - discrepancy_count
    perc_discrepancy = round((discrepancy_count / total_kasus) * 100, 1) if total_kasus > 0 else 0
    perc_sesuai = round((sesuai_count / total_kasus) * 100, 1) if total_kasus > 0 else 0

    md_content += f"## E. Kesesuaian Input INACBG-iDRG (Disrespancy Koding)\n\n"
    md_content += f"Berdasarkan hasil evaluasi terhadap {total_kasus} berkas klaim di {nama_rs}, ditemukan sebanyak {discrepancy_count} berkas klaim atau {perc_discrepancy}% yang mengalami ketidaksesuaian antara input diagnosis atau tindakan pada sistem INACBG dan iDRG, dengan total keseluruhan mencapai {total_diff_codes} perbedaan kode medis. Sebaliknya, sebanyak {sesuai_count} berkas klaim atau {perc_sesuai}% sisanya telah menunjukkan kesesuaian data input antara kedua sistem tersebut.\n\n"
    
    # Lampiran Ringkasan KKR
    md_content += f"# Lampiran: Rincian Kesesuaian Input (Ringkasan KKR)\n\n"
    md_content += f"| No | Nomor SEP | Deskripsi Kasus | Temuan Discrepancy Diagnosa | Temuan Discrepancy Prosedur |\n"
    md_content += f"|---|---|---|---|---|\n"
    for row in lampiran_rows:
        md_content += row

    output_filename = f"Laporan_BAB_II_{kode_rs}_{nama_rs.replace(' ', '_')}.md"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Berhasil mengenerate MD untuk {nama_rs} di {output_path}")

if __name__ == '__main__':
    generate_md_report("ADAM MALIK")
