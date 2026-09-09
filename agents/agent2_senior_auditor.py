"""
AGENT 2 — SENIOR AUDITOR
=========================
Kementerian Kesehatan RI / Pusat Pembiayaan Kesehatan
AI Report Generation Framework V2

TUGAS:
- Menerima JSON metadata dari Agent 1
- Mengeksekusi Reasoning Framework 8 Langkah
- Menghasilkan Audit Outline terstruktur (.md)
- TIDAK berasumsi. TIDAK membuat opini. Hanya fakta yang bisa dibuktikan dari JSON.

Menggunakan Gemini LLM untuk reasoning & outline generation.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'audit_outline')
INPUT_DIR  = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'data_review')
os.makedirs(OUTPUT_DIR, exist_ok=True)


from agents.shared.gemini_client import call_gemini, get_model_name, test_connection


SYSTEM_PROMPT_AGENT2 = """
Anda adalah Ketua Tim Review Audit Koding, Kementerian Kesehatan Republik Indonesia.
Anda memiliki pengalaman 25 tahun dalam audit pembiayaan JKN, INA-CBG, dan transisi iDRG.

ATURAN MUTLAK:
- Jangan berasumsi.
- Jangan membuat opini.
- Jangan menggunakan bahasa AI.
- Setiap pernyataan HARUS dapat dibuktikan dari data JSON yang diberikan.
- Apabila tidak ada bukti → jangan tulis.

TUGAS ANDA:
Baca JSON metadata dari Agent 1.
Lakukan proses reasoning 8 langkah:

Langkah 1: Baca seluruh data. Jangan menulis.
Langkah 2: Identifikasi seluruh fakta dengan referensi ke field JSON.
Langkah 3: Kelompokkan fakta (populasi / validasi KNAVP / dual coding / risiko / triase).
Langkah 4: Cari hubungan antar fakta (korelasi, anomali berulang).
Langkah 5: Cari hubungan dengan konteks desk review (keterbatasan tanpa rekam medis fisik).
Langkah 6: Tentukan implikasi administratif per kelompok temuan.
Langkah 7: Tentukan implikasi audit per kelompok temuan.
Langkah 8: Tulis Audit Outline.

FORMAT OUTPUT WAJIB (Markdown):

# AUDIT OUTLINE
## Rumah Sakit: [nama_rs] — Kode: [kode_rs]
## Tanggal Analisis: [tanggal]

---

## A. IDENTITAS DATA

(Tabel: RS, periode, populasi, sampel)

---

## B. FAKTA UTAMA

### B.1 Populasi dan Sampel
- [Fakta dengan angka dari JSON]

### B.2 Hasil Validasi KNAVP
- [Fakta alert: total, per kategori, severity]

### B.3 Diskrepansi Dual Coding
- [Fakta mismatch INA-CBG vs iDRG]

### B.4 Triase Kasus
- [Angka onsite / sampling / monitoring]

### B.5 Kasus Prioritas Teratas
- [Top 5 kasus dengan detail rule]

---

## C. HUBUNGAN ANTAR FAKTA

(Korelasi dan pola yang teridentifikasi dari data)

---

## D. IMPLIKASI ADMINISTRATIF

(Per kelompok temuan — apa artinya bagi administrasi klaim)

---

## E. IMPLIKASI AUDIT

(Per kelompok temuan — apa yang harus diverifikasi di On-Site Audit)

---

## F. RISIKO

(Estimasi risiko keuangan JKN berdasarkan data, bukan asumsi)

---

## G. REKOMENDASI

(Berbasis fakta — bukan normatif)

---

## H. TINDAK LANJUT

(Langkah konkret: siapa, apa, kapan)

---

PENTING:
- Setiap poin HARUS menyebut angka spesifik dari JSON.
- Tidak ada kalimat tanpa angka atau referensi data.
- Tidak ada narasi deskriptif umum.
- Outline ini bukan laporan — hanya kerangka fakta + implikasi.
"""


def build_user_prompt(metadata: dict) -> str:
    """Bangun prompt untuk Agent 2 dari JSON metadata Agent 1."""
    return f"""
Berikut adalah JSON Metadata dari Agent 1 — Data Reviewer:

```json
{json.dumps(metadata, ensure_ascii=False, indent=2)[:8000]}
```

Lakukan reasoning 8 langkah dan hasilkan Audit Outline sesuai format yang telah ditentukan.
Gunakan HANYA data yang ada di JSON di atas.
Jangan menambahkan data dari luar.
Jangan berasumsi.
"""


def run(kode_rs: str, metadata: dict = None, verbose: bool = True) -> str:
    """
    Eksekusi Agent 2 untuk satu RS.
    Return: string konten Audit Outline Markdown.
    """
    if verbose:
        print(f"\n[AGENT 2] SENIOR AUDITOR — RS: {kode_rs}")
        print("=" * 60)

    # Load metadata dari file jika tidak diberikan langsung
    if metadata is None:
        json_path = os.path.join(INPUT_DIR, f'data_review_{kode_rs}.json')
        if not os.path.exists(json_path):
            print(f"  [ERROR] File tidak ditemukan: {json_path}")
            print(f"  Jalankan Agent 1 terlebih dahulu.")
            return ""
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

    try:
        model_name = get_model_name()
        if verbose:
            print(f"  Model: {model_name}")

        user_prompt = build_user_prompt(metadata)
        full_prompt = SYSTEM_PROMPT_AGENT2 + "\n\n" + user_prompt

        outline_text = call_gemini(
            full_prompt,
            temperature=0.2,
            max_tokens=4096,
            max_retries=5,
            retry_delay=40,
            verbose=verbose
        )
        if not outline_text:
            if verbose:
                print(f"  Gemini tidak merespons — pakai fallback Python")
            outline_text = _fallback_outline(metadata, kode_rs)

    except Exception as e:
        print(f"  [ERROR] Gemini API gagal: {e}")
        # Fallback: buat outline dari template Python
        outline_text = _fallback_outline(metadata, kode_rs)

    # Simpan output
    out_path = os.path.join(OUTPUT_DIR, f'audit_outline_{kode_rs}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(outline_text)

    if verbose:
        print(f"  Outline disimpan: {out_path}")
        print(f"  Panjang: {len(outline_text)} karakter")

    return outline_text


def _fallback_outline(meta: dict, kode_rs: str) -> str:
    """Fallback Python template jika Gemini API tidak tersedia."""
    rs_name  = meta.get('_meta', {}).get('rs_name', kode_rs)
    pop      = meta.get('population', {})
    samp     = meta.get('sample', {})
    knavp    = meta.get('knavp_validation', {})
    triase   = meta.get('triase', {})
    dc       = meta.get('dual_coding', {})
    dom      = knavp.get('dominant_category', {})
    prio     = meta.get('priority_cases', [])[:5]
    stats    = meta.get('summary_stats', {})

    lines = [
        f"# AUDIT OUTLINE",
        f"## Rumah Sakit: {rs_name} — Kode: {kode_rs}",
        f"## Tanggal Analisis: {datetime.now().strftime('%d %B %Y')}",
        "",
        "---",
        "",
        "## A. IDENTITAS DATA",
        "",
        f"| Parameter | Nilai |",
        f"|-----------|-------|",
        f"| Nama RS | {rs_name} |",
        f"| Kode RS | {kode_rs} |",
        f"| Periode | Januari – Desember 2025 |",
        f"| Total Populasi | {pop.get('total', 0):,} kasus |",
        f"| Sampel Direview | {samp.get('total', 0)} kasus |",
        "",
        "---",
        "",
        "## B. FAKTA UTAMA",
        "",
        "### B.1 Populasi dan Sampel",
        f"- Populasi klaim: {pop.get('total', 0):,} kasus (Rawat Inap: {pop.get('rawat_inap', 0):,} | Rawat Jalan: {pop.get('rawat_jalan', 0):,})",
        f"- Sampel Cochran: {samp.get('total', 0)} kasus (RI: {samp.get('rawat_inap', 0)} | RJ: {samp.get('rawat_jalan', 0)})",
        "",
        "### B.2 Hasil Validasi KNAVP",
        f"- Total alerts: {knavp.get('total_alerts', 0)}",
        f"- Kategori dominan: {dom.get('title', '-')} — {dom.get('count', 0)} kejadian ({dom.get('percentage', 0)}%)",
        f"- Kasus dengan alerts: {stats.get('cases_with_alerts', 0)} dari {samp.get('total', 0)} ({stats.get('alert_rate_pct', 0)}%)",
    ]

    cat_breakdown = knavp.get('category_breakdown', [])
    for cat in cat_breakdown:
        lines.append(f"  - {cat.get('title', cat.get('category', '-'))}: {cat.get('count', 0)} temuan")

    lines += [
        "",
        "### B.3 Diskrepansi Dual Coding",
        f"- Kasus mismatch INA-CBG vs iDRG: {dc.get('cases_with_discrepancy', 0)} kasus ({dc.get('mismatch_percentage', 0)}%)",
        f"- Total perbedaan kode: {dc.get('total_discrepancy', 0)}",
        f"- Kasus sinkron: {dc.get('cases_matching', 0)} ({dc.get('match_percentage', 0)}%)",
        "",
        "### B.4 Triase Kasus",
        f"- Rekomendasi On-Site Audit: {triase.get('onsite_count', 0)} kasus ({triase.get('onsite_percentage', 0)}%)",
        f"- Rekomendasi Audit Sampling: {triase.get('sampling_count', 0)} kasus",
        f"- Monitoring/Lolos: {triase.get('monitoring_count', 0)} kasus",
        "",
        "### B.5 Kasus Prioritas Teratas",
    ]

    for i, c in enumerate(prio, 1):
        lines.append(f"- [{i}] SEP {c.get('sep', '-')} | Skor KNAVP: {c.get('knavp_skor', 0)} | Risiko: {c.get('tingkat_risiko', '-')} | Rules: {c.get('triggered_rules_count', 0)}")

    lines += [
        "",
        "---",
        "",
        "## C. HUBUNGAN ANTAR FAKTA",
        "",
        f"- Tingginya frekuensi anomali {dom.get('title', '-')} berkorelasi dengan potensi pergeseran tingkat keparahan (PCCL).",
        f"- {dc.get('mismatch_percentage', 0)}% kasus mismatch dual coding mengindikasikan ketidakselarasan input diagnosis/prosedur antara sistem INA-CBG dan iDRG.",
        f"- {triase.get('onsite_percentage', 0)}% kasus masuk kategori risiko tinggi yang memerlukan verifikasi fisik.",
        "",
        "---",
        "",
        "## D. IMPLIKASI ADMINISTRATIF",
        "",
        f"- Anomali {dom.get('title', '-')} mensyaratkan koreksi administrasi klaim oleh tim PMIK sebelum proses lanjut.",
        f"- Diskrepansi dual coding berimplikasi pada potensi pembayaran tarif yang tidak akurat.",
        "",
        "---",
        "",
        "## E. IMPLIKASI AUDIT",
        "",
        f"- {triase.get('onsite_count', 0)} kasus wajib diverifikasi fisik rekam medis (On-Site Audit).",
        "- Pembuktian medical evidence (lab, radiologi, laporan operasi) menjadi syarat mutlak.",
        "- Desk Review tidak dapat menyimpulkan kesalahan definitif — hanya indikasi.",
        "",
        "---",
        "",
        "## F. RISIKO",
        "",
        f"- Risiko up-coding akibat anomali {dom.get('title', '-')} yang tidak dikoreksi.",
        f"- Risiko pembayaran klaim tidak tepat pada {dc.get('cases_with_discrepancy', 0)} kasus mismatch.",
        "",
        "---",
        "",
        "## G. REKOMENDASI",
        "",
        f"- Lakukan On-Site Audit terhadap {triase.get('onsite_count', 0)} kasus prioritas.",
        f"- Klarifikasi administratif terhadap {triase.get('sampling_count', 0)} kasus sampling.",
        "- Pembinaan koder RS terkait penerapan ICS dan aturan KNAVP.",
        "",
        "---",
        "",
        "## H. TINDAK LANJUT",
        "",
        "- Tim Reviewer: Susun jadwal On-Site Audit berbasis daftar prioritas.",
        f"- PMIK {rs_name}: Siapkan dokumen rekam medis untuk {triase.get('onsite_count', 0)} kasus prioritas.",
        "- Pusbikes: Terbitkan Surat Pemberitahuan Audit kepada manajemen RS.",
    ]

    return "\n".join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Agent 2 — Senior Auditor')
    parser.add_argument('--kode_rs', type=str, default='1275655', help='Kode RS')
    args = parser.parse_args()
    result = run(args.kode_rs)
    if result:
        print("\n[AGENT 2] DONE. Audit Outline tersimpan.")
