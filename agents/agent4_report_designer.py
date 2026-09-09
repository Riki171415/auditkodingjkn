"""
AGENT 4 — REPORT DESIGNER
===========================
Kementerian Kesehatan RI / Pusat Pembiayaan Kesehatan
AI Report Generation Framework V2

TUGAS:
- Menerima Draft laporan dari Agent 3
- Mengonversi ke Markdown terstruktur siap Python
- Tambahkan: heading hierarchy, tabel (id+caption+summary), chart blocks (id+type+data), gambar (id+caption+alt)
- Generate TOC block, Daftar Gambar, Daftar Tabel otomatis
- Output: Markdown siap diproses generate_from_md.py
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'final_md')
INPUT_DIR  = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'draft')
META_DIR   = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'data_review')
os.makedirs(OUTPUT_DIR, exist_ok=True)


from agents.shared.gemini_client import call_gemini, get_model_name, test_connection


SYSTEM_PROMPT_AGENT4 = """
Anda adalah Report Designer spesialis dokumen resmi pemerintah.

TUGAS:
Konversi laporan ke Markdown terstruktur yang siap diproses oleh Python generator.

ATURAN WAJIB:

1. HEADING HIERARCHY
   # BAB I ...
   ## A. ...
   ### 1. ...

2. TABEL — setiap tabel WAJIB mempunyai:
   <!-- table_id: tbl_001 -->
   <!-- caption: Judul Tabel -->
   <!-- summary: Deskripsi singkat isi tabel -->
   | ... | ... |

3. CHART BLOCKS — gunakan format ini persis:
   ```chart
   id: chart_001
   type: pie
   title: Judul Chart
   labels:
     - Label1
     - Label2
   values:
     - 45
     - 74
   ```

4. GAMBAR — setiap gambar WAJIB:
   <!-- img_id: fig_001 -->
   <!-- caption: Judul Gambar -->
   <!-- alt: Alt text -->
   <!-- summary: Deskripsi gambar -->
   ![caption](path/to/image)

5. TOC — di awal dokumen, setelah metadata:
   <!-- TOC_START -->
   - [BAB I PENDAHULUAN](#bab-i-pendahuluan)
   ...
   <!-- TOC_END -->

6. DAFTAR TABEL — setelah TOC:
   <!-- TABLE_LIST_START -->
   - Tabel 1.1: [caption] — hal. X
   ...
   <!-- TABLE_LIST_END -->

7. DAFTAR GAMBAR:
   <!-- FIGURE_LIST_START -->
   - Gambar 1.1: [caption] — hal. X
   ...
   <!-- FIGURE_LIST_END -->

8. CHART BLOCKS WAJIB untuk:
   - Distribusi Triase (pie chart)
   - Distribusi KNAVP per kategori (bar chart)
   - Perbandingan Populasi vs Sampel (bar chart)
   - Diskrepansi Dual Coding (pie chart)

9. NUMBERING:
   - Tabel: tbl_[kode_rs]_001, tbl_[kode_rs]_002, ...
   - Chart: chart_[kode_rs]_001, ...
   - Gambar: fig_[kode_rs]_001, ...

JANGAN ubah isi narasi.
JANGAN tambah atau kurangi konten.
HANYA tambahkan elemen struktural Markdown.
"""


def build_charts_from_meta(meta: dict, kode_rs: str) -> str:
    """Hasilkan chart blocks dari metadata Agent 1."""
    knavp  = meta.get('knavp_validation', {})
    triase = meta.get('triase', {})
    dc     = meta.get('dual_coding', {})
    pop    = meta.get('population', {})
    samp   = meta.get('sample', {})

    cat_breakdown = knavp.get('category_breakdown', [])
    cat_labels    = [c.get('title', c.get('category', '-'))[:30] for c in cat_breakdown if c.get('count', 0) > 0]
    cat_values    = [c.get('count', 0) for c in cat_breakdown if c.get('count', 0) > 0]

    charts = []

    # Chart 1: Distribusi Triase
    triase_vals = [
        triase.get('onsite_count', 0),
        triase.get('sampling_count', 0),
        triase.get('monitoring_count', 0),
    ]
    if sum(triase_vals) > 0:
        charts.append(f"""```chart
id: chart_{kode_rs}_001
type: pie
title: Distribusi Hasil Triase — {kode_rs}
labels:
  - On-Site Audit
  - Audit Sampling
  - Monitoring/Lolos
values:
  - {triase_vals[0]}
  - {triase_vals[1]}
  - {triase_vals[2]}
```""")

    # Chart 2: KNAVP per kategori
    if cat_labels and cat_values:
        labels_yaml  = "\n  - ".join(cat_labels)
        values_yaml  = "\n  - ".join(str(v) for v in cat_values)
        charts.append(f"""```chart
id: chart_{kode_rs}_002
type: bar
title: Distribusi Anomali KNAVP per Kategori — {kode_rs}
labels:
  - {labels_yaml}
values:
  - {values_yaml}
```""")

    # Chart 3: Dual Coding Discrepancy
    dc_match    = dc.get('cases_matching', 0)
    dc_mismatch = dc.get('cases_with_discrepancy', 0)
    if dc_match + dc_mismatch > 0:
        charts.append(f"""```chart
id: chart_{kode_rs}_003
type: pie
title: Kesesuaian Input INA-CBG vs iDRG — {kode_rs}
labels:
  - Sinkron
  - Mismatch
values:
  - {dc_match}
  - {dc_mismatch}
```""")

    # Chart 4: Populasi vs Sampel
    charts.append(f"""```chart
id: chart_{kode_rs}_004
type: bar
title: Populasi vs Sampel — {kode_rs}
labels:
  - Total Populasi
  - Rawat Inap
  - Rawat Jalan
  - Total Sampel
values:
  - {pop.get('total', 0)}
  - {pop.get('rawat_inap', 0)}
  - {pop.get('rawat_jalan', 0)}
  - {samp.get('total', 0)}
```""")

    return "\n\n".join(charts)


def run(kode_rs: str, draft_text: str = None, metadata: dict = None, verbose: bool = True) -> str:
    """
    Eksekusi Agent 4 untuk satu RS.
    Return: string Final Markdown terstruktur.
    """
    if verbose:
        print(f"\n[AGENT 4] REPORT DESIGNER — RS: {kode_rs}")
        print("=" * 60)

    # Load draft dari file jika tidak diberikan
    if draft_text is None:
        draft_path = os.path.join(INPUT_DIR, f'draft_{kode_rs}.md')
        if not os.path.exists(draft_path):
            print(f"  [ERROR] Draft tidak ditemukan: {draft_path}")
            return ""
        with open(draft_path, 'r', encoding='utf-8') as f:
            draft_text = f.read()

    # Load metadata untuk chart data
    if metadata is None:
        meta_path = os.path.join(META_DIR, f'data_review_{kode_rs}.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}

    rs_name = metadata.get('_meta', {}).get('rs_name', kode_rs)

    # Generate chart blocks dari metadata (deterministik, tidak perlu LLM)
    chart_blocks = build_charts_from_meta(metadata, kode_rs)

    try:
        model_name = get_model_name()
        if verbose:
            print(f"  Model: {model_name}")

        user_prompt = f"""
Kode RS: {kode_rs}
Nama RS: {rs_name}

Berikut adalah Draft Laporan dari Agent 3:

---
{draft_text[:6000]}
---

Tambahkan elemen struktural Markdown (TOC, caption tabel, chart blocks, id gambar, Daftar Tabel, Daftar Gambar)
sesuai format yang ditetapkan.

Chart blocks yang sudah siap dari data (tambahkan di posisi yang relevan dalam laporan):

{chart_blocks}

PENTING: Output HARUS mencakup SELURUH narasi dari draft. JANGAN memotong atau meringkas teks.
Jangan hentikan output sebelum seluruh laporan selesai hingga BAB III Rekomendasi.
Gunakan kode_rs {kode_rs} untuk semua ID (tbl_{kode_rs}_001, chart_{kode_rs}_001, dst).
"""

        full_prompt = SYSTEM_PROMPT_AGENT4 + "\n\n" + user_prompt

        final_md = call_gemini(
            full_prompt,
            temperature=0.1,
            max_tokens=8192,
            max_retries=5,
            retry_delay=40,
            verbose=verbose
        )
        if not final_md:
            print(f"  Gemini tidak merespons -- pakai fallback struktural")
            final_md = _fallback_structure(draft_text, chart_blocks, metadata, kode_rs, rs_name)
        else:
            # Deteksi truncation di Agent 4
            last_char = final_md.rstrip()[-1] if final_md.rstrip() else ''
            word_count = len(final_md.split())
            is_truncated = last_char not in {'.', '!', '?', ':', ';', '\n'}
            if is_truncated and word_count >= 600:
                if verbose:
                    print(f"  [TRUNCATION A4] Output terpotong ({word_count} kata) -- pakai fallback struktural")
                # Fallback: tambahkan chart blocks langsung ke draft (lebih aman daripada MD terpotong)
                final_md = _fallback_structure(draft_text, chart_blocks, metadata, kode_rs, rs_name)

    except Exception as e:
        print(f"  [WARN] Exception: {e} -- pakai fallback")
        final_md = _fallback_structure(draft_text, chart_blocks, metadata, kode_rs, rs_name)

    # Final safety net
    if not final_md or not final_md.strip():
        final_md = _fallback_structure(draft_text, chart_blocks, metadata, kode_rs, rs_name)

    # Simpan final MD
    out_path = os.path.join(OUTPUT_DIR, f'final_md_{kode_rs}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_md)

    if verbose:
        print(f"  Final MD disimpan: {out_path}")
        print(f"  Panjang: {len(final_md)} karakter")

    return final_md


def _fallback_structure(draft: str, charts: str, meta: dict, kode_rs: str, rs_name: str) -> str:
    """Fallback: inject chart blocks dan TOC ke draft tanpa Gemini."""
    knavp  = meta.get('knavp_validation', {})
    triase = meta.get('triase', {})
    dc     = meta.get('dual_coding', {})
    pop    = meta.get('population', {})
    samp   = meta.get('sample', {})

    toc = f"""<!-- TOC_START -->
## DAFTAR ISI

- [BAB I PENDAHULUAN](#bab-i-pendahuluan)
  - [A. Latar Belakang](#a-latar-belakang)
  - [B. Dasar Hukum dan Pelaksanaan](#b-dasar-hukum-dan-pelaksanaan)
  - [C. Tujuan](#c-tujuan)
  - [D. Ruang Lingkup](#d-ruang-lingkup)
  - [E. Metode](#e-metode)
- [BAB II HASIL DESK REVIEW](#bab-ii-hasil-desk-review)
  - [A. Gambaran Data](#a-gambaran-data)
  - [B. Hasil Validasi KNAVP](#b-hasil-validasi-knavp)
  - [C. Analisis Temuan](#c-analisis-temuan)
  - [D. Kasus Prioritas](#d-kasus-prioritas)
  - [E. Kesesuaian Input INA-CBG dan iDRG](#e-kesesuaian-input-ina-cbg-dan-idrg)
- [BAB III KESIMPULAN DAN REKOMENDASI](#bab-iii-kesimpulan-dan-rekomendasi)
  - [A. Kesimpulan](#a-kesimpulan)
  - [B. Rekomendasi](#b-rekomendasi)
<!-- TOC_END -->

<!-- TABLE_LIST_START -->
## DAFTAR TABEL

- Tabel {kode_rs}.1: Populasi dan Sampel Klaim
- Tabel {kode_rs}.2: Ringkasan Validasi KNAVP
- Tabel {kode_rs}.3: Kasus Prioritas
<!-- TABLE_LIST_END -->

<!-- FIGURE_LIST_START -->
## DAFTAR GAMBAR

- Gambar {kode_rs}.1: Distribusi Triase
- Gambar {kode_rs}.2: Distribusi KNAVP per Kategori
- Gambar {kode_rs}.3: Kesesuaian INA-CBG vs iDRG
- Gambar {kode_rs}.4: Populasi vs Sampel
<!-- FIGURE_LIST_END -->

---
"""

    # Table: Populasi & Sampel
    pop_table = f"""<!-- table_id: tbl_{kode_rs}_001 -->
<!-- caption: Tabel {kode_rs}.1 — Populasi dan Sampel Klaim -->
<!-- summary: Rincian total populasi klaim dan jumlah sampel yang direview -->

| Uraian | Total Populasi | Sampel Direview |
|--------|---------------|-----------------|
| Total Kasus | {pop.get('total', 0):,} | {samp.get('total', 0)} |
| Rawat Inap | {pop.get('rawat_inap', 0):,} | {samp.get('rawat_inap', 0)} |
| Rawat Jalan | {pop.get('rawat_jalan', 0):,} | {samp.get('rawat_jalan', 0)} |
"""

    # Table: KNAVP Summary
    cat_breakdown = knavp.get('category_breakdown', [])
    knavp_rows = "\n".join(
        f"| {c.get('title', c.get('category', '-'))} | {c.get('count', 0)} |"
        for c in cat_breakdown if c.get('count', 0) > 0
    )
    knavp_table = f"""<!-- table_id: tbl_{kode_rs}_002 -->
<!-- caption: Tabel {kode_rs}.2 — Ringkasan Validasi KNAVP per Kategori -->
<!-- summary: Jumlah peringatan anomali per kategori aturan KNAVP -->

| Kategori KNAVP | Jumlah Temuan |
|----------------|--------------|
{knavp_rows}
| **TOTAL** | **{knavp.get('total_alerts', 0)}** |
"""

    # Table: Triase
    triase_table = f"""<!-- table_id: tbl_{kode_rs}_003 -->
<!-- caption: Tabel {kode_rs}.3 — Hasil Triase Kasus -->
<!-- summary: Distribusi keputusan triase berdasarkan tingkat risiko -->

| Kategori Triase | Jumlah Kasus | Persentase |
|-----------------|-------------|-----------|
| On-Site Audit | {triase.get('onsite_count', 0)} | {triase.get('onsite_percentage', 0)}% |
| Audit Sampling | {triase.get('sampling_count', 0)} | - |
| Monitoring/Lolos | {triase.get('monitoring_count', 0)} | - |
| **Total Sampel** | **{samp.get('total', 0)}** | **100%** |
"""

    # Insert everything into draft
    result = toc + "\n---\n\n" + draft + "\n\n---\n\n"
    result += "## Lampiran — Visualisasi Data\n\n"
    result += pop_table + "\n\n"
    result += knavp_table + "\n\n"
    result += triase_table + "\n\n"
    result += "### Chart Visualisasi\n\n"
    result += charts

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Agent 4 — Report Designer')
    parser.add_argument('--kode_rs', type=str, default='1275655', help='Kode RS')
    args = parser.parse_args()
    result = run(args.kode_rs)
    if result:
        print("\n[AGENT 4] DONE. Final Markdown tersimpan.")
