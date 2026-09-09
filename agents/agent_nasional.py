import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from modules.db_manager import get_recap_desk_review
from agents.shared.gemini_client import call_gemini

OUTPUT_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'final_md')
os.makedirs(OUTPUT_DIR, exist_ok=True)

SYSTEM_PROMPT = """Anda adalah Senior Auditor Tingkat Nasional dari Pusat Pembiayaan Kesehatan, Kementerian Kesehatan RI. 
Tugas Anda adalah menyusun teks Laporan Akhir Nasional Hasil Desk Review Audit Koding berdasarkan data statistik agregat yang riil.
Gaya Bahasa: Profesional, tajam, analitis, ekstensif, dan birokratis (seperti dokumen resmi kementerian). 
Instruksi Penting: 
1. Buat paragraf yang panjang dan elaboratif. Jangan terlalu singkat. Setiap subbab minimal terdiri dari 2-3 paragraf panjang.
2. Istilah asing (seperti Desk Review, On-Site Audit, up-coding, dual coding, fraud, dll) HARUS dicetak miring (*italic*).
3. Anda WAJIB menggunakan semua data angka yang diberikan dalam narasi, buat sedetail mungkin.
4. Jangan menambahkan tabel, HANYA narasi panjang dan list numbering jika diperlukan.
5. Pada BAB II Subbab A, masukkan tag [CHART_DISTRIBUSI_KEPUTUSAN] persis di tempat grafik akan diletakkan (tanpa format lain).
6. Pada BAB II Subbab B, masukkan tag [CHART_TOP_RULES] persis di tempat grafik akan diletakkan (tanpa format lain).
7. List numbering harus selalu dimulai dari angka 1, menggunakan format '1. ', '2. ', dst.

STRUKTUR LAPORAN WAJIB:
# BAB I: PENDAHULUAN
## A. Latar Belakang (Jelaskan sangat panjang tentang sistem JKN, INA-CBG, dan pentingnya audit ini)
## B. Tujuan (Umum dan Khusus)
## C. Dasar Hukum (Gunakan dasar hukum JKN dan Audit Koding yang relevan)

# BAB II: HASIL PELAKSANAAN REVIEW KODING NASIONAL
## A. Gambaran Data Agregat Nasional (Ceritakan panjang lebar hasil klasifikasi, lalu sisipkan [CHART_DISTRIBUSI_KEPUTUSAN])
## B. Matriks Pelanggaran Aturan (KNAVP) (Analisis secara mendalam tentang pelanggaran yang paling banyak terjadi, lalu sisipkan [CHART_TOP_RULES])
## C. Analisis Diskrepansi Dual Coding (Analisis tentang perbedaan INA-CBG dan iDRG dari data)

# BAB III: KESIMPULAN DAN REKOMENDASI
## A. Kesimpulan (Lebih dari 3 poin panjang yang mencakup seluruh aspek temuan)
## B. Rekomendasi (Lebih dari 3 poin panjang untuk faskes, auditor lapangan, maupun kemenkes)
"""

def generate_markdown_ai():
    print("Mengekstraksi data statistik nasional...")
    recap = get_recap_desk_review()
    
    total_kasus = len(recap)
    if total_kasus == 0:
        print("Tidak ada data desk review untuk periode ini.")
        return
        
    discrepancy_count = 0
    rule_counts = {}
    keputusan_counts = {'Direkomendasikan On-Site Audit': 0, 'Audit Sampling': 0, 'Lolos/Monitoring': 0}
    rs_set = set()
    
    for r in recap:
        try: fd = json.loads(r.get('tindakan_reviewer') or '{}')
        except: fd = {}
            
        beda_dc = int(fd.get('jumlah_beda_dual_coding', 0) or 0)
        if beda_dc > 0: discrepancy_count += 1
            
        triggered = r.get('triggered_rules', [])
        
        for rule in triggered:
            cat = rule.get('kelompok_rule', 'Lainnya')
            rule_counts[cat] = rule_counts.get(cat, 0) + 1
            
        kep = fd.get('keputusan_sistem', 'Tidak perlu tindak lanjut')
        if kep == 'Direkomendasikan On-Site Audit':
            keputusan_counts['Direkomendasikan On-Site Audit'] += 1
        elif kep == 'Audit Sampling':
            keputusan_counts['Audit Sampling'] += 1
        else:
            keputusan_counts['Lolos/Monitoring'] += 1
            
        rs_set.add(r.get('kode_rs', '-'))
        
    sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)
    top_5_rules = sorted_rules[:5]
    total_rules = sum(rule_counts.values())

    stats_json = {
        "total_kasus_direview": total_kasus,
        "total_rumah_sakit": len(rs_set),
        "distribusi_hasil_keputusan": keputusan_counts,
        "kasus_diskrepansi_dual_coding": discrepancy_count,
        "persentase_diskrepansi": round((discrepancy_count / total_kasus * 100), 1) if total_kasus > 0 else 0,
        "total_pelanggaran_knavp": total_rules,
        "top_5_pelanggaran_terbanyak": [{"kategori": cat, "jumlah": cnt} for cat, cnt in top_5_rules]
    }
    
    user_prompt = f"{SYSTEM_PROMPT}\n\nBerikut adalah DATA STATISTIK AGREGAT yang WAJIB dimasukkan ke dalam narasi secara mendetail:\n{json.dumps(stats_json, indent=2)}\n\nSilakan tuliskan seluruh narasi Laporan Akhir Nasional sekarang!"
    
    print("Menghubungi Gemini untuk mengarang narasi secara mendetail...")
    response_text = call_gemini(user_prompt, temperature=0.7, max_tokens=15000)
    
    if not response_text:
        print("Gagal menghubungi Gemini atau response kosong.")
        return
        
    out_path = os.path.join(OUTPUT_DIR, "final_md_nasional.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(response_text)
        
    print(f"Berhasil! Markdown Laporan Nasional tersimpan di: {out_path}")

if __name__ == "__main__":
    generate_markdown_ai()
