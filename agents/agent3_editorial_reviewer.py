"""
AGENT 3 — EDITORIAL REVIEWER
==============================
Kementerian Kesehatan RI / Pusat Pembiayaan Kesehatan
AI Report Generation Framework V2

TUGAS:
- Menerima Audit Outline dari Agent 2
- Mengembangkan menjadi laporan naratif penuh
- Pola wajib: Pendahuluan → Fakta → Analisis → Interpretasi → Implikasi → Kesimpulan → Transisi
- Min 180 kata per paragraf, min 4 paragraf per subbab
- Tidak ada AI-wording, tidak ada kalimat kosong
- Target: natural, administratif, profesional — seperti auditor senior Kemenkes
"""

import os
import sys
import json
import argparse
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'draft')
INPUT_DIR  = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'audit_outline')
META_DIR   = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'data_review')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import banned phrases checker
sys.path.insert(0, os.path.join(BASE_DIR, 'agents'))
from shared.banned_phrases import check_banned


from agents.shared.gemini_client import call_gemini, get_model_name, test_connection


SYSTEM_PROMPT_AGENT3 = """
Anda adalah Senior Editorial Reviewer dengan pengalaman 25 tahun menyusun laporan resmi Kementerian Kesehatan RI dan Pusat Pembiayaan Kesehatan.

ATURAN MUTLAK — WAJIB DIPATUHI:
1. Jangan mengubah fakta, angka, atau temuan dari Audit Outline.
2. Jangan menambahkan data yang tidak ada di Outline.
3. Setiap paragraf WAJIB minimum 180 kata.
4. Setiap subbab WAJIB minimum 4 paragraf.
5. Tidak ada kalimat pendek tanpa isi.
6. Tidak ada frasa AI generik (contoh: "dengan demikian", "sangat penting", "komprehensif", "signifikan", "membongkar").
7. Gaya bahasa: formal, administratif, presisi klinis, seperti auditor pemerintah senior.

POLA WAJIB SETIAP SUBBAB:
Paragraf 1 - Pendahuluan subbab (konteks & tujuan)
Paragraf 2 - Fakta (angka-angka dari data)
Paragraf 3 - Analisis dan Interpretasi (apa artinya angka itu)
Paragraf 4 - Implikasi dan transisi ke subbab berikutnya

KONTEKS PENTING:
Laporan ini adalah hasil DESK REVIEW oleh Pusat Pembiayaan Kesehatan, Kementerian Kesehatan RI.
Audit koding dilaksanakan dalam rangka transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG).
Auditor BELUM memeriksa rekam medis fisik.
Setiap temuan berstatus "indikasi" — bukan penetapan kesalahan.
Verifikasi definitif dilakukan pada On-Site Audit.

STRUKTUR LAPORAN YANG HARUS DIHASILKAN:

# BAB I PENDAHULUAN
## A. Latar Belakang
## B. Dasar Hukum dan Pelaksanaan
## C. Tujuan
## D. Ruang Lingkup
## E. Metode

# BAB II HASIL DESK REVIEW
## A. Gambaran Data
## B. Hasil Validasi KNAVP
## C. Analisis Temuan
## D. Kasus Prioritas
## E. Kesesuaian Input INA-CBG dan iDRG

# BAB III KESIMPULAN DAN REKOMENDASI
## A. Kesimpulan
## B. Rekomendasi

TUGAS:
Baca Audit Outline yang diberikan.
Kembangkan setiap bagian menjadi laporan naratif penuh sesuai struktur dan aturan di atas.
Gunakan HANYA fakta yang ada di Outline.
Jangan berasumsi.
Jangan bernarasi tanpa dasar data.
"""


def _build_section_prompt(bab_title: str, outline_text: str, rs_name: str, kode_rs: str) -> str:
    """Bangun prompt untuk satu BAB spesifik."""
    return f"""
Anda sedang menulis {bab_title} dari Laporan Hasil Desk Review untuk:
- Rumah Sakit  : {rs_name}
- Kode RS      : {kode_rs}
- Periode      : Januari - Desember 2025

Berikut adalah Audit Outline yang menjadi dasar penulisan:

---
{outline_text}
---

TUGAS: Tulis HANYA bagian {bab_title} secara lengkap dan penuh.

WAJIB DIPENUHI:
- Minimal 4 subbab
- Setiap subbab minimal 4 paragraf
- Setiap paragraf minimal 150 kata
- Semua angka dari Outline WAJIB tercantum
- Tidak ada frasa AI generik (komprehensif, signifikan, tidak dapat dipungkiri, dll)
- Bahasa: formal, administratif, seperti laporan resmi Kementerian Kesehatan
- KONTEKS DESK REVIEW: setiap temuan adalah indikasi, bukan penetapan
- Jangan tambah data yang tidak ada di Outline
- Jangan berhenti sebelum seluruh {bab_title} selesai ditulis

Mulai langsung dengan heading {bab_title}, jangan tambahkan penjelasan meta.
"""


def run(kode_rs: str, outline_text: str = None, metadata: dict = None, verbose: bool = True) -> str:
    """
    Eksekusi Agent 3 untuk satu RS.
    Return: string Draft laporan Markdown penuh.
    """
    if verbose:
        print(f"\n[AGENT 3] EDITORIAL REVIEWER — RS: {kode_rs}")
        print("=" * 60)

    # Load outline dari file jika tidak diberikan
    if outline_text is None:
        outline_path = os.path.join(INPUT_DIR, f'audit_outline_{kode_rs}.md')
        if not os.path.exists(outline_path):
            print(f"  [ERROR] Outline tidak ditemukan: {outline_path}")
            return ""
        with open(outline_path, 'r', encoding='utf-8') as f:
            outline_text = f.read()

    # Load metadata untuk konteks angka
    if metadata is None:
        meta_path = os.path.join(META_DIR, f'data_review_{kode_rs}.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}

    rs_name = metadata.get('_meta', {}).get('rs_name', kode_rs)

    try:
        model_name = get_model_name()
        if verbose:
            print(f"  Model: {model_name}")

        user_prompt = f"""
Berikut adalah Audit Outline dari Agent 2 — Senior Auditor:

---
{outline_text}
---

Kembangkan seluruh Outline di atas menjadi laporan naratif penuh menggunakan pola dan aturan yang telah ditetapkan.

Pastikan:
- Setiap subbab minimal 4 paragraf
- Setiap paragraf minimal 180 kata
- Semua angka dari Outline tercantum di laporan
- Tidak ada frasa AI generik
- Bahasa formal, administratif, dan profesional
- Konteks Desk Review selalu dipertahankan (bukan audit definitif)
- Nama RS: {rs_name}
- Kode RS: {kode_rs}
- Periode: Januari – Desember 2025
"""

        full_prompt = SYSTEM_PROMPT_AGENT3 + "\n\n" + user_prompt

        # === Strategi: panggil Gemini per BAB agar tidak terpotong ===
        sections = {
            "BAB I": _build_section_prompt("BAB I PENDAHULUAN", outline_text, rs_name, kode_rs),
            "BAB II": _build_section_prompt("BAB II HASIL DESK REVIEW", outline_text, rs_name, kode_rs),
            "BAB III": _build_section_prompt("BAB III KESIMPULAN DAN REKOMENDASI", outline_text, rs_name, kode_rs),
        }

        parts = []
        for bab_name, bab_prompt in sections.items():
            if verbose:
                print(f"  Generating {bab_name}...")
            text = call_gemini(
                SYSTEM_PROMPT_AGENT3 + "\n\n" + bab_prompt,
                temperature=0.3,
                max_tokens=8192,
                verbose=verbose
            )

            # Deteksi truncation: output terpotong di tengah kalimat
            if text and len(text) > 100:
                last_char = text.rstrip()[-1] if text.rstrip() else ''
                is_truncated = last_char not in {'.', '!', '?', ':', ';', '»', '"', "'"}
                word_count   = len(text.split())
                # Jika terpotong DAN output sangat panjang (mendekati limit)
                if is_truncated and word_count >= 700:
                    if verbose:
                        print(f"  [TRUNCATION DETECTED] {bab_name} terpotong di {word_count} kata — lanjutkan...")
                    continuation = call_gemini(
                        SYSTEM_PROMPT_AGENT3 + "\n\nLanjutkan PERSIS dari kalimat yang terpotong berikut ini tanpa mengulang yang sudah ditulis:\n\n"
                        + text[-500:],  # 500 karakter terakhir sebagai konteks
                        temperature=0.3,
                        max_tokens=4096,
                        verbose=verbose
                    )
                    if continuation:
                        # Sambungkan tanpa duplikasi
                        text = text.rstrip() + ' ' + continuation.lstrip()
                        if verbose:
                            total_words = len(text.split())
                            print(f"  [CONTINUATION] {bab_name} sekarang {total_words} kata")

            if text:
                parts.append(text)
            else:
                # Fallback untuk section ini
                parts.append(f"# {bab_name}\n\n[Konten {bab_name} menggunakan fallback]\n")

        draft_text = "\n\n---\n\n".join(parts) if parts else ""

        # Jika semua bagian gagal, pakai fallback penuh
        if not draft_text.strip():
            draft_text = _fallback_draft(outline_text, metadata, kode_rs, rs_name)

    except Exception as e:
        print(f"  [WARN] Exception: {e} -- pakai fallback")
        draft_text = _fallback_draft(outline_text, metadata, kode_rs, rs_name)

    # Final safety net
    if not draft_text or not draft_text.strip():
        draft_text = _fallback_draft(outline_text, metadata, kode_rs, rs_name)

    # QC: Deteksi banned phrases
    violations = check_banned(draft_text)
    if violations:
        if verbose:
            print(f"  [QC WARNING] {len(violations)} frasa terlarang terdeteksi:")
            for v in violations[:5]:
                print(f"    - '{v}'")

    # Simpan draft
    out_path = os.path.join(OUTPUT_DIR, f'draft_{kode_rs}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(draft_text)

    if verbose:
        print(f"  Draft disimpan: {out_path}")
        print(f"  Panjang: {len(draft_text)} karakter | Kata: {len(draft_text.split()):,}")
        if violations:
            print(f"  [!] {len(violations)} frasa perlu direvisi Agent 5")

    return draft_text


def _fallback_draft(outline: str, meta: dict, kode_rs: str, rs_name: str) -> str:
    """Fallback — kembalikan outline dengan header laporan jika Gemini tidak tersedia."""
    pop   = meta.get('population', {})
    samp  = meta.get('sample', {})
    knavp = meta.get('knavp_validation', {})
    triase= meta.get('triase', {})
    dc    = meta.get('dual_coding', {})
    dom   = knavp.get('dominant_category', {})
    stats = meta.get('summary_stats', {})

    header = f"""# LAPORAN HASIL DESK REVIEW AUDIT CODING
## Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)

| Parameter | Keterangan |
|-----------|------------|
| Rumah Sakit | {rs_name} |
| Kode RS | {kode_rs} |
| Periode Data | Januari – Desember 2025 |
| Tanggal Laporan | {datetime.now().strftime('%d %B %Y')} |
| Nomor Laporan | LHR-DR/2026/{kode_rs} |
| Disusun oleh | Tim Reviewer Koding — Pusat Pembiayaan Kesehatan |

---

# BAB I PENDAHULUAN

## A. Latar Belakang

Transformasi sistem pembiayaan kesehatan nasional dari INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)
menuntut akurasi dan konsistensi pengodean medis yang lebih tinggi dari fasilitas kesehatan. Sistem iDRG dirancang
untuk lebih sensitif dalam menangkap kompleksitas morbiditas pasien, sehingga setiap kode diagnosis sekunder dan
prosedur yang dicantumkan memiliki probabilitas langsung untuk menggeser tingkat keparahan klinis (PCCL) dan
besaran tarif kompensasi yang diterima rumah sakit.

Dalam fase transisi ini, kualitas pengodean medis yang tercatat pada pangkalan data fasilitas kesehatan menjadi
parameter fundamental. Kementerian Kesehatan RI melalui Pusat Pembiayaan Kesehatan memiliki mandat untuk memetakan
integritas data klaim secara dini melalui mekanisme Audit Koding berbasis Desk Review. Laporan ini merupakan hasil
evaluasi terhadap data klaim elektronik {rs_name} (Kode RS: {kode_rs}), yang mencakup populasi sebesar
{pop.get('total', 0):,} kasus selama periode Januari hingga Desember 2025.

Desk Review sebagai instrumen penyaringan awal menganalisis data secara elektronik tanpa melibatkan pemeriksaan
dokumen fisik rekam medis. Oleh karena itu, seluruh temuan dalam laporan ini berstatus sebagai indikasi yang
memerlukan klarifikasi dan verifikasi lanjutan. Penetapan definitif atas setiap temuan hanya dapat dilakukan
setelah pelaksanaan On-Site Audit dengan pemeriksaan dokumen rekam medis fisik di fasilitas kesehatan.

## D. Ruang Lingkup

Objek penelaahan dalam laporan ini dibatasi pada pangkalan data klaim JKN elektronik yang diterbitkan oleh
{rs_name} (Kode RS: {kode_rs}) selama periode layanan 1 Januari hingga 31 Desember 2025.
Total populasi klaim adalah {pop.get('rawat_inap', 0):,} kasus Rawat Inap dan {pop.get('rawat_jalan', 0):,}
kasus Rawat Jalan. Sampel Cochran yang ditarik untuk desk review berjumlah {samp.get('total', 0)} kasus
(RI: {samp.get('rawat_inap', 0)} | RJ: {samp.get('rawat_jalan', 0)}).

---

# BAB II HASIL DESK REVIEW

## A. Gambaran Data

Populasi klaim elektronik {rs_name} pada periode Januari–Desember 2025 tercatat sebesar {pop.get('total', 0):,} kasus,
terdiri dari {pop.get('rawat_inap', 0):,} kasus Rawat Inap dan {pop.get('rawat_jalan', 0):,} kasus Rawat Jalan.
Dari populasi tersebut, ditarik sampel Cochran sebesar {samp.get('total', 0)} kasus menggunakan instrumen KKR-DR01
sebagai basis evaluasi pada tahap Desk Review ini.

Distribusi triase hasil validasi menempatkan {triase.get('onsite_count', 0)} kasus pada kategori rekomendasi
On-Site Audit, {triase.get('sampling_count', 0)} kasus pada Audit Sampling, dan {triase.get('monitoring_count', 0)}
kasus pada klaster Lolos/Monitoring.

## B. Hasil Validasi KNAVP

Eksekusi algoritma KNAVP pada {samp.get('total', 0)} kasus sampel menghasilkan total {knavp.get('total_alerts', 0)}
peringatan anomali koding. Klaster temuan tertinggi terdapat pada kelompok {dom.get('title', '-')}
dengan {dom.get('count', 0)} kejadian ({dom.get('percentage', 0)}% dari total alerts).

Sebaran peringatan ini mencakup {stats.get('cases_with_alerts', 0)} kasus atau {stats.get('alert_rate_pct', 0)}%
dari total sampel yang divalidasi.

## E. Kesesuaian Input INA-CBG dan iDRG

Komparasi input antara sistem INA-CBG dan iDRG menemukan diskrepansi kode pada {dc.get('cases_with_discrepancy', 0)}
berkas klaim atau {dc.get('mismatch_percentage', 0)}% dari populasi sampel. Total selisih kode yang teridentifikasi
mencapai {dc.get('total_discrepancy', 0)} perbedaan. Sebaliknya, {dc.get('cases_matching', 0)} berkas klaim
({dc.get('match_percentage', 0)}%) terverifikasi sinkron antara kedua sistem.

---

# BAB III KESIMPULAN DAN REKOMENDASI

## A. Kesimpulan

Analisis elektronik atas {samp.get('total', 0)} sampel klaim {rs_name} mengonfirmasi keberadaan
{knavp.get('total_alerts', 0)} anomali koding dengan pusat deviasi pada kelompok {dom.get('title', '-')}.
Sebagai implikasi manajerial, {triase.get('onsite_count', 0)} kasus berisiko tinggi wajib ditindaklanjuti
secara faktual melalui On-Site Audit guna mencegah pembayaran klaim yang tidak tepat sasaran.

## B. Rekomendasi

Berdasarkan hasil analisis reviewer atas keseluruhan temuan Desk Review, direkomendasikan:
- Pelaksanaan On-Site Audit terhadap {triase.get('onsite_count', 0)} kasus prioritas.
- Klarifikasi administratif terhadap {triase.get('sampling_count', 0)} kasus sampling.
- Pembinaan pengodean ICS dan KNAVP bagi tenaga koding rumah sakit.

---

*Laporan ini merupakan hasil Desk Review — bukan penetapan kesalahan. Verifikasi definitif dilakukan pada On-Site Audit.*
"""
    return header


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Agent 3 — Editorial Reviewer')
    parser.add_argument('--kode_rs', type=str, default='1275655', help='Kode RS')
    args = parser.parse_args()
    result = run(args.kode_rs)
    if result:
        print("\n[AGENT 3] DONE. Draft laporan tersimpan.")
