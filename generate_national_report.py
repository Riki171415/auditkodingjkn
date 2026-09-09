import os
import json
import sys

# Tambahkan path agar bisa import agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.shared.gemini_client import call_gemini

def main():
    data_dir = 'exports/agent_outputs/data_review/'
    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    total_rs = len(files)
    total_sampel = 0
    total_alerts = 0
    triase = {'Onsite': 0, 'Sampling': 0, 'Monitor': 0}
    severity = {'High': 0, 'Medium': 0, 'Low': 0}
    dual_coding_mismatches = 0
    
    for file in files:
        with open(os.path.join(data_dir, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            total_sampel += data.get('total_sample', 0)
            total_alerts += data.get('total_knavp_alerts', 0)
            
            sev = data.get('severity_counts', {})
            severity['High'] += sev.get('High', 0)
            severity['Medium'] += sev.get('Medium', 0)
            severity['Low'] += sev.get('Low', 0)
            
            for c in data.get('cases', []):
                if c.get('jumlah_beda_dual_coding', 0) > 0:
                    dual_coding_mismatches += 1
                
                skr = c.get('knavp_skor', 0)
                if skr >= 50:
                    triase['Onsite'] += 1
                elif skr >= 20:
                    triase['Sampling'] += 1
                else:
                    triase['Monitor'] += 1
                    
    prompt = f"""
Anda adalah Senior Auditor Medis dari Pusat Pembiayaan Kesehatan (Pusbikes) Kemenkes RI.
Tugas Anda adalah menulis Laporan Eksekutif Nasional (Laporan Akhir Gabungan) hasil Audit Koding JKN Tahun 2025.
Laporan ini ditujukan kepada Pimpinan Pusbikes dan Inspektorat Jenderal (Itjen).
Gunakan bahasa Indonesia yang sangat formal, profesional, natural, dan analitis.
Jangan mengarang data fiktif.

Berikut adalah data agregat hasil audit dari {total_rs} Rumah Sakit seluruh Indonesia:
- Total Sampel Kasus yang Dievaluasi: {total_sampel} kasus
- Total Peringatan (Alerts) KNAVP: {total_alerts} peringatan
- Rincian Tingkat Keparahan Peringatan KNAVP:
  - Risiko Tinggi (High): {severity['High']}
  - Risiko Sedang (Medium): {severity['Medium']}
  - Risiko Rendah (Low): {severity['Low']}
- Hasil Triase (Rekomendasi Tindak Lanjut):
  - Membutuhkan On-Site Audit (Prioritas Utama): {triase['Onsite']} kasus
  - Membutuhkan Audit Sampling (Klarifikasi Dokumen): {triase['Sampling']} kasus
  - Lolos Validasi (Monitoring Berkala): {triase['Monitor']} kasus
- Anomali Dual Coding (INA-CBG vs iDRG): Ditemukan {dual_coding_mismatches} kasus mengalami ketidaksesuaian/diskrepansi kode.

Struktur Laporan yang Diharapkan:
1. PENDAHULUAN: Tujuan audit nasional dan konteks transisi sistem pembiayaan iDRG.
2. RINGKASAN EKSEKUTIF DATA: Narasikan secara natural metrik-metrik agregat di atas (jangan hanya berupa bullet points kaku, buat narasinya mengalir dan mudah dipahami pimpinan).
3. ANALISIS & IMPLIKASI: Apa arti dari tingginya/rendahnya temuan ini terhadap kesiapan implementasi iDRG secara nasional.
4. REKOMENDASI TINDAK LANJUT: Saran konkret bagi Pimpinan Pusbikes dan Itjen untuk penanganan RS yang masuk kategori On-Site Audit dan Sampling, serta strategi pembinaan.
5. KESIMPULAN.

Tulis Laporan dalam format Markdown yang rapi.
"""

    print(f"Mengumpulkan data dari {total_rs} Rumah Sakit...")
    print(f"Total Sampel: {total_sampel}")
    print("Menghasilkan Laporan Nasional menggunakan LLM Gemini...")
    
    response = call_gemini(prompt, temperature=0.6, max_tokens=4000)
    
    out_path = 'exports/Laporan_Akhir_Nasional_Agregat.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(response)
        
    print(f"Berhasil membuat laporan di {out_path}")

if __name__ == "__main__":
    main()
