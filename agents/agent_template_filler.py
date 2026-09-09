"""
agents/agent_template_filler.py
================================
MODE TEMPLATE — Hemat Token untuk 43 RS
========================================
Skip Agent 2/3/4 (LLM). Gunakan template narasi dari RS master (1275655)
dan ganti seluruh data dengan metadata Agent 1 RS target.

Pipeline:
  Agent 1 (Python) → JSON metadata
  Template Filler  → isi template dengan data RS target
  Agent 5 (Python) → QA check
  Generator        → DOCX + PNG
"""

import os
import sys
import re
import json
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'approved')
META_DIR     = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'data_review')
DRAFT_OUT    = os.path.join(BASE_DIR, 'exports', 'agent_outputs', 'final_md')
os.makedirs(DRAFT_OUT, exist_ok=True)

MASTER_RS_KODE = '1275655'
MASTER_RS_NAME = 'RSU H. ADAM MALIK'

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE NARASI MASTER — dibangun dari Python (tidak bergantung pada LLM)
# ─────────────────────────────────────────────────────────────────────────────

def build_template_md(meta: dict, kode_rs: str) -> str:
    """
    Bangun Markdown laporan lengkap dari metadata Agent 1.
    Narasi berbasis template — tidak perlu LLM.
    """
    rs_name   = meta.get('_meta', {}).get('rs_name', kode_rs)
    pop       = meta.get('population', {})
    samp      = meta.get('sample', {})
    knavp     = meta.get('knavp_validation', {})
    triase    = meta.get('triase', {})
    dc        = meta.get('dual_coding', {})
    summary   = meta.get('summary_stats', {})
    def fmt_num(val) -> str:
        if isinstance(val, float):
            return f"{val:,.1f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"{val:,}".replace(',', '.')

    total_pop = pop.get('total', 0)
    ri_pop    = pop.get('rawat_inap', 0)
    rj_pop    = pop.get('rawat_jalan', 0)
    total_samp= samp.get('total', 0)
    ri_samp   = samp.get('rawat_inap', 0)
    rj_samp   = samp.get('rawat_jalan', 0)

    total_alerts = knavp.get('total_alerts', 0)
    sev          = knavp.get('severity_breakdown', {})
    cat_breakdown= knavp.get('category_breakdown', [])
    dom_cat      = knavp.get('dominant_category', {})
    dom_title    = dom_cat.get('title', '-')
    dom_count    = dom_cat.get('count', 0)

    onsite   = triase.get('onsite',   triase.get('onsite_count', 0))
    sampling = triase.get('sampling', triase.get('sampling_count', 0))
    monitor  = triase.get('monitor',  triase.get('monitoring_count', 0))

    mismatch     = dc.get('mismatch_count', dc.get('cases_with_discrepancy', 0))
    mismatch_pct = dc.get('mismatch_pct',   dc.get('mismatch_percentage', 0))
    match_count  = dc.get('cases_matching', total_samp - mismatch)

    avg_skor     = summary.get('avg_knavp_skor', 0)
    alert_pct    = summary.get('alert_rate_pct', 0)

    # Top anomaly cases
    top_anomalies = meta.get('top_anomalies', [])
    top_sep = top_anomalies[0].get('sep', '-') if top_anomalies else '-'

    # Priority cases
    priority_cases = meta.get('priority_cases', [])
    high_risk = [c for c in priority_cases if str(c.get('tingkat_risiko', '')).lower() == 'tinggi']
    medium_risk = [c for c in priority_cases if str(c.get('tingkat_risiko', '')).lower() == 'sedang']

    # KNAVP category list
    cat_list = ', '.join(
        [f"{c.get('title', c.get('category', '-'))} ({c.get('count', 0)} kasus)"
         for c in cat_breakdown if c.get('count', 0) > 0]
    ) or 'Tidak terdapat temuan'

    # Chart data KNAVP
    knavp_labels  = [c.get('title', c.get('category', '-'))[:30] for c in cat_breakdown if c.get('count', 0) > 0]
    knavp_values  = [c.get('count', 0) for c in cat_breakdown if c.get('count', 0) > 0]
    knavp_lbl_str = '\n'.join([f'  - {l}' for l in knavp_labels]) or '  - Tidak ada'
    knavp_val_str = '\n'.join([f'  - {v}' for v in knavp_values]) or '  - 0'

    # Rekomendasi based on findings
    if onsite >= 5:
        rekom_onsite = f"pelaksanaan On-Site Audit segera terhadap {onsite} kasus yang dinilai memiliki risiko tinggi"
    elif onsite > 0:
        rekom_onsite = f"pelaksanaan On-Site Audit terhadap {onsite} kasus prioritas tinggi"
    else:
        rekom_onsite = "pemantauan berkala terhadap kasus-kasus yang menunjukkan indikasi penyimpangan"

    md = f"""<!-- TOC_START -->
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

# BAB I PENDAHULUAN

## A. Latar Belakang

Pelaksanaan audit koding terhadap data klaim pelayanan kesehatan di {rs_name} dengan Kode Rumah Sakit {kode_rs} untuk periode pelayanan Januari sampai dengan Desember 2025 dilaksanakan oleh Pusat Pembiayaan Kesehatan Kementerian Kesehatan Republik Indonesia dalam kerangka evaluasi tata kelola pembiayaan kesehatan nasional. Kegiatan ini ditempatkan dalam koridor penataan ulang dan transisi sistem pembiayaan berbasis kelompok diagnosis, yaitu dari sistem Indonesia Case Based Groups (INA-CBG) menuju sistem Indonesian Diagnosis Related Groups (iDRG). Proses penyesuaian arsitektur pengelompokan klaim ini menuntut tingkat akurasi koding diagnosis maupun prosedur tindakan medis yang tinggi agar mencerminkan kondisi klinis pasien secara tepat dan dapat dipertanggungjawabkan secara administratif dalam proses klaim pembayaran.

Konteks pelaksanaan audit koding ini tidak dapat dipisahkan dari kebijakan transformasi pembiayaan kesehatan nasional yang sedang berlangsung. Pusat Pembiayaan Kesehatan bertanggung jawab atas pengawasan kualitas data klaim yang diajukan oleh fasilitas pelayanan kesehatan mitra Jaminan Kesehatan Nasional (JKN). Kegiatan desk review merupakan tahapan pertama dalam hierarki pengawasan tersebut, berfungsi sebagai penyaring awal berbasis data elektronik sebelum dilakukan verifikasi lapangan. Dengan cakupan populasi klaim sebesar {fmt_num(total_pop)} kasus di {rs_name} selama tahun 2025, baik rawat inap maupun rawat jalan, diperlukan mekanisme penapisan sistematis yang mampu mengidentifikasi pola anomali secara efisien dan terukur.

Pelaksanaan desk review ini menggunakan instrumen Katalog Nasional Aturan Validasi Pengodean (KNAVP) sebagai standar acuan pengujian konsistensi koding. KNAVP merupakan kompilasi aturan teknis pengodean klinis yang mencakup berbagai dimensi validasi, antara lain kesesuaian diagnosis utama dan sekunder, validitas prosedur tindakan, konsistensi hubungan manifestasi-sebab, serta kepatuhan terhadap ketentuan unbundling dan pengelompokan biaya. Instrumen ini dioperasikan secara algoritmik untuk memproses seluruh kasus sampel yang telah ditentukan berdasarkan formula Cochran dengan mempertimbangkan volume populasi klaim masing-masing fasilitas pelayanan kesehatan. Penggunaan formula ini memastikan representativitas sampel secara statistik sekaligus menjamin efisiensi sumber daya pengawasan yang tersedia.

Laporan desk review ini disusun sebagai dokumentasi resmi hasil pelaksanaan audit koding tahap pertama dan menjadi dasar perencanaan tindak lanjut berupa audit sampling ataupun on-site audit bagi kasus-kasus yang menunjukkan indikasi ketidaksesuaian koding. Seluruh temuan dalam laporan ini berstatus indikasi administratif berdasarkan analisis data elektronik, sehingga belum merupakan penetapan final atas adanya pelanggaran koding. Verifikasi definitif akan dilaksanakan pada tahapan audit lanjutan dengan melibatkan pemeriksaan dokumen rekam medis fisik dan konfirmasi langsung kepada tenaga koding serta klinisi di fasilitas pelayanan kesehatan yang bersangkutan.

## B. Dasar Hukum dan Pelaksanaan

Pelaksanaan audit koding ini berlandaskan pada ketentuan peraturan perundang-undangan di bidang pembiayaan kesehatan dan penyelenggaraan jaminan kesehatan nasional. Kerangka hukum yang menjadi acuan pelaksanaan meliputi Undang-Undang Nomor 17 Tahun 2023 tentang Kesehatan yang menegaskan kewajiban pembiayaan kesehatan yang berkeadilan dan akuntabel, serta Peraturan Presiden yang mengatur penyelenggaraan JKN. Selain itu, pelaksanaan audit ini merujuk pada Peraturan Menteri Kesehatan yang mengatur standar koding klinis dan tata cara penagihan klaim pelayanan kesehatan kepada Badan Penyelenggara Jaminan Sosial Kesehatan.

Kewenangan Pusat Pembiayaan Kesehatan dalam melaksanakan fungsi pengawasan koding dan verifikasi klaim didasarkan pada tugas pokok dan fungsi yang ditetapkan melalui peraturan internal Kementerian Kesehatan. Dalam menjalankan fungsi ini, Pusat Pembiayaan Kesehatan berkoordinasi dengan Direktorat Jenderal Pelayanan Kesehatan, BPJS Kesehatan, dan fasilitas pelayanan kesehatan mitra untuk memastikan integritas data klaim yang menjadi dasar pembayaran. Audit koding yang dilaksanakan merupakan bagian dari siklus penjaminan mutu pembiayaan yang berlangsung secara periodik sesuai dengan kalender pengawasan yang telah ditetapkan dalam rencana kerja tahunan Pusat Pembiayaan Kesehatan.

## C. Tujuan

Pelaksanaan desk review audit koding terhadap data klaim {rs_name} bertujuan untuk menilai tingkat kepatuhan pengodean klinis terhadap kaidah Indonesian Coding Standard (ICS) dan aturan pengelompokan kasus iDRG. Secara khusus, audit ini diarahkan untuk mengidentifikasi pola ketidaksesuaian antara kode diagnosis dan prosedur yang tertera dalam klaim dengan kondisi klinis yang seharusnya terdokumentasi dalam rekam medis. Hasil identifikasi ini kemudian digunakan sebagai landasan pengambilan keputusan mengenai tindak lanjut audit yang diperlukan, baik berupa sampling klarifikasi maupun on-site audit secara menyeluruh.

## D. Ruang Lingkup

Ruang lingkup desk review mencakup seluruh kasus sampel yang dipilih secara acak dari populasi klaim {rs_name} periode Januari hingga Desember 2025. Dari total populasi {fmt_num(total_pop)} kasus yang terdiri atas {fmt_num(ri_pop)} kasus rawat inap dan {fmt_num(rj_pop)} kasus rawat jalan, diambil sampel sebanyak {fmt_num(total_samp)} kasus berdasarkan formula Cochran, terdiri atas {fmt_num(ri_samp)} kasus rawat inap dan {fmt_num(rj_samp)} kasus rawat jalan. Seluruh kasus sampel tersebut dievaluasi menggunakan instrumen KNAVP yang mencakup aspek validasi diagnosis, prosedur, kesesuaian koding dual system (INA-CBG dan iDRG), serta penilaian kelengkapan bukti medis pendukung.

## E. Metode

Metode yang digunakan dalam pelaksanaan desk review ini adalah kombinasi antara algoritma penapis otomatis (rule-based engine) dan penilaian pakar (expert review). Seluruh kasus sampel diproses melalui KNAVP Engine untuk menghasilkan skor anomali koding dan rekomendasi tindak lanjut awal. Kasus yang memperoleh skor KNAVP di atas ambang batas yang ditetapkan selanjutnya dikategorikan ke dalam kelompok risiko tinggi, sedang, atau rendah. Pengelompokan ini menjadi dasar penentuan prioritas tindak lanjut: kasus risiko tinggi direkomendasikan untuk on-site audit, kasus risiko sedang untuk audit sampling, dan kasus risiko rendah untuk monitoring berkala.

---

# BAB II HASIL DESK REVIEW

## A. Gambaran Data

Pelaksanaan desk review terhadap berkas klaim pelayanan kesehatan di {rs_name} (Kode RS: {kode_rs}) untuk periode Januari sampai dengan Desember 2025 dilakukan sebagai bagian dari pemantauan keterandalan data klaim program Jaminan Kesehatan Nasional. Tim auditor Pusat Pembiayaan Kesehatan Kementerian Kesehatan Republik Indonesia mengarahkan penelaahan ini untuk memetakan konsistensi antara pengodean tindakan, diagnosis, serta kelengkapan dokumen pendukung yang terekam secara digital dalam sistem informasi rumah sakit. Melalui evaluasi tingkat pertama ini, seluruh data administratif dan muatan variabel klaim diteliti guna mengidentifikasi adanya anomali atau ketidaksesuaian pola pengodean sebelum dilaksanakannya verifikasi faktual secara langsung di lapangan.

Total populasi klaim yang menjadi basis pengambilan sampel berjumlah {fmt_num(total_pop)} kasus, terdiri atas {fmt_num(ri_pop)} kasus rawat inap dan {fmt_num(rj_pop)} kasus rawat jalan. Berdasarkan formula Cochran yang diterapkan secara konsisten dalam siklus audit nasional ini, jumlah sampel yang ditentukan adalah sebanyak {fmt_num(total_samp)} kasus, dengan komposisi {fmt_num(ri_samp)} kasus rawat inap dan {fmt_num(rj_samp)} kasus rawat jalan. Distribusi sampel ini mencerminkan proporsi populasi klaim rawat inap dan rawat jalan yang sesungguhnya, sehingga hasil analisis dapat dianggap mewakili keseluruhan pola koding yang diterapkan di {rs_name} selama periode referensi. Ukuran sampel ini dipandang memadai secara statistik untuk mendeteksi penyimpangan sistemik dalam praktik pengodean klinis.

```chart
id: chart_{kode_rs}_004
type: bar
title: Populasi vs Sampel — {kode_rs}
labels:
  - Total Populasi
  - Rawat Inap
  - Rawat Jalan
  - Total Sampel
values:
  - {total_pop}
  - {ri_pop}
  - {rj_pop}
  - {total_samp}
```

Penelaahan awal terhadap seluruh kasus sampel difokuskan pada identifikasi pola anomali yang terdeteksi secara algoritmik melalui instrumen KNAVP. Dari {fmt_num(total_samp)} kasus yang dievaluasi, sistem berhasil mengidentifikasi {fmt_num(total_alerts)} kasus yang memiliki setidaknya satu indikasi ketidaksesuaian koding berdasarkan aturan validasi yang berlaku. Tingkat kejadian anomali sebesar {fmt_num(alert_pct)}% dari total sampel ini merupakan parameter awal yang akan diperdalam pada tahapan analisis selanjutnya. Distribusi temuan tersebut tersebar dalam beberapa kategori aturan KNAVP dengan dominasi pada kelompok {dom_title} sebanyak {fmt_num(dom_count)} kasus.

## B. Hasil Validasi KNAVP

Instrumen Katalog Nasional Aturan Validasi Pengodean (KNAVP) yang dioperasikan dalam kerangka desk review ini menghasilkan penilaian terhadap {fmt_num(total_samp)} kasus sampel di {rs_name}. Dari keseluruhan kasus tersebut, sistem validasi mendeteksi {fmt_num(total_alerts)} indikasi ketidaksesuaian koding yang terdistribusi dalam beberapa kategori aturan. Distribusi anomali per kategori KNAVP adalah sebagai berikut: {cat_list}. Tingkat keparahan temuan terbagi atas {fmt_num(sev.get('High', 0))} kasus dengan severity tinggi (High), {fmt_num(sev.get('Medium', 0))} kasus dengan severity sedang (Medium), dan {fmt_num(sev.get('Low', 0))} kasus dengan severity rendah (Low).

```chart
id: chart_{kode_rs}_002
type: bar
title: Distribusi Anomali KNAVP per Kategori — {kode_rs}
labels:
{knavp_lbl_str}
values:
{knavp_val_str}
```

Berdasarkan hasil penilaian KNAVP, seluruh kasus sampel dikategorikan ke dalam tiga kelompok tindak lanjut. Pertama, sejumlah {fmt_num(onsite)} kasus direkomendasikan untuk On-Site Audit karena memiliki skor risiko tinggi atau ditemukan anomali koding yang berdampak signifikan terhadap nilai klaim. Kedua, sebanyak {fmt_num(sampling)} kasus direkomendasikan untuk Audit Sampling guna melakukan klarifikasi atas indikasi yang ditemukan pada tahap desk review. Ketiga, sejumlah {fmt_num(monitor)} kasus dinyatakan dapat masuk dalam kategori Monitoring, yang berarti tidak ditemukan indikasi ketidaksesuaian koding yang memerlukan tindak lanjut segera. Rata-rata skor KNAVP dari seluruh kasus sampel adalah {fmt_num(avg_skor)}, mencerminkan tingkat risiko agregat pada periode ini.

```chart
id: chart_{kode_rs}_001
type: pie
title: Distribusi Hasil Triase — {kode_rs}
labels:
  - On-Site Audit
  - Audit Sampling
  - Monitoring/Lolos
values:
  - {onsite}
  - {sampling}
  - {monitor}
```

## C. Analisis Temuan

Analisis mendalam terhadap temuan KNAVP menunjukkan bahwa kategori {dom_title} menjadi kelompok anomali yang paling banyak teridentifikasi dengan {fmt_num(dom_count)} kasus pada periode ini. Kondisi ini mengindikasikan adanya pola tertentu dalam praktik pengodean di {rs_name} yang perlu mendapatkan perhatian dari manajemen koding dan klinisi terkait. Temuan pada kategori ini umumnya berkaitan dengan ketidaksesuaian antara bukti medis yang tersedia dalam data elektronik dengan pengodean tindakan atau diagnosis yang diajukan dalam klaim. Indikasi ini bersifat administratif dan memerlukan konfirmasi melalui pemeriksaan rekam medis fisik pada tahapan audit lanjutan.

Selain kategori dominan tersebut, distribusi temuan pada kategori lainnya juga memberikan gambaran mengenai pola pengodean secara keseluruhan di {rs_name}. Kehadiran temuan pada berbagai kategori KNAVP sekaligus mengindikasikan bahwa perlu dilakukan pembinaan menyeluruh terhadap tenaga koding, tidak hanya terfokus pada satu aspek saja. Variasi kategori temuan ini juga menunjukkan bahwa pengodean di fasilitas pelayanan kesehatan ini mencakup kasus-kasus klinis yang beragam dengan kompleksitas koding yang berbeda-beda. Sebagian temuan mungkin merupakan false positive yang dapat dibantah dengan bukti klinis yang memadai, sehingga proses validasi lanjutan mutlak diperlukan sebelum kesimpulan final dapat ditetapkan.

## D. Kasus Prioritas

Dari {len(priority_cases)} kasus yang memiliki indikasi ketidaksesuaian koding atau diskrepansi dual coding, terdapat {len(high_risk)} kasus yang dikategorikan sebagai prioritas tinggi dan {len(medium_risk)} kasus sebagai prioritas sedang. Kasus-kasus prioritas tinggi ini memerlukan perhatian segera karena berpotensi memiliki dampak finansial yang signifikan terhadap nilai klaim yang dibayarkan. Kasus dengan tingkat risiko tinggi umumnya memiliki kombinasi skor KNAVP yang tinggi sekaligus jumlah diskrepansi dual coding yang besar, menandakan adanya ketidaksesuaian sistemik antara pengodean INA-CBG dan iDRG. Seluruh kasus prioritas ini direkomendasikan untuk menjadi fokus utama pada tahapan audit sampling atau on-site audit yang dijadwalkan berikutnya.

## E. Kesesuaian Input INA-CBG dan iDRG

Evaluasi kesesuaian antara input koding INA-CBG dan iDRG merupakan komponen kritis dalam proses transisi sistem pembiayaan. Dari {fmt_num(total_samp)} kasus sampel yang dievaluasi, sebanyak {fmt_num(mismatch)} kasus atau {fmt_num(mismatch_pct)}% menunjukkan adanya diskrepansi antara koding INA-CBG dan iDRG. Sementara itu, {fmt_num(match_count)} kasus atau {fmt_num(100 - mismatch_pct)}% menunjukkan kesesuaian antara kedua sistem koding tersebut. Angka diskrepansi sebesar {fmt_num(mismatch_pct)}% ini perlu mendapat perhatian serius karena dapat berdampak pada akurasi pengelompokan kasus dan nilai klaim yang diajukan dalam sistem iDRG yang akan diberlakukan.

```chart
id: chart_{kode_rs}_003
type: pie
title: Kesesuaian Input INA-CBG vs iDRG — {kode_rs}
labels:
  - Sinkron
  - Mismatch
values:
  - {match_count}
  - {mismatch}
```

Tingginya angka diskrepansi dual coding ini mengindikasikan perlunya peningkatan kapasitas tenaga koding di {rs_name} dalam memahami perbedaan logika pengelompokan antara INA-CBG dan iDRG. Perbedaan mendasar antara kedua sistem ini mencakup struktur hierarki diagnosis, pembobotan tindakan, serta mekanisme penentuan tingkat keparahan kasus. Tanpa pemahaman yang memadai atas perbedaan tersebut, tenaga koding berpotensi menghasilkan klaim yang tidak konsisten antar sistem, yang pada gilirannya dapat menimbulkan permasalahan dalam proses verifikasi dan pembayaran klaim pada era iDRG.

---

# BAB III KESIMPULAN DAN REKOMENDASI

## A. Kesimpulan

Pelaksanaan desk review audit koding oleh Pusat Pembiayaan Kesehatan Kementerian Kesehatan Republik Indonesia terhadap {rs_name} (Kode RS: {kode_rs}) untuk periode Januari sampai dengan Desember 2025 telah menghasilkan gambaran komprehensif mengenai kualitas pengodean klinis di fasilitas pelayanan kesehatan ini. Dari {fmt_num(total_samp)} kasus sampel yang dievaluasi, sistem KNAVP berhasil mengidentifikasi {fmt_num(total_alerts)} indikasi ketidaksesuaian koding yang terdistribusi dalam beberapa kategori aturan validasi. Kategori {dom_title} menjadi kelompok temuan yang paling dominan dengan {fmt_num(dom_count)} kasus, diikuti oleh temuan pada kategori-kategori lainnya. Tingkat diskrepansi dual coding sebesar {fmt_num(mismatch_pct)}% dari total sampel menjadi perhatian utama mengingat pentingnya konsistensi koding dalam proses transisi dari INA-CBG ke iDRG.

Hasil penilaian risiko menunjukkan bahwa dari {fmt_num(total_samp)} kasus sampel, sebanyak {fmt_num(onsite)} kasus direkomendasikan untuk On-Site Audit, {fmt_num(sampling)} kasus untuk Audit Sampling, dan {fmt_num(monitor)} kasus dinyatakan dapat dimonitoring secara berkala. Komposisi ini mencerminkan profil risiko pengodean di {rs_name} yang memerlukan tindak lanjut terstruktur sesuai dengan tingkatan urgensi masing-masing kasus. Seluruh temuan dalam laporan desk review ini berstatus indikasi yang perlu dikonfirmasi melalui pemeriksaan rekam medis fisik pada tahapan audit lanjutan yang akan dijadwalkan oleh Pusat Pembiayaan Kesehatan Kementerian Kesehatan Republik Indonesia.

## B. Rekomendasi

Berdasarkan hasil analisis desk review terhadap data klaim {rs_name} periode Januari hingga Desember 2025, direkomendasikan langkah-langkah tindak lanjut sebagai berikut:

1. Tidak diperlukan tindak lanjut segera bagi {fmt_num(monitor)} kasus yang dinyatakan lolos validasi tanpa catatan risiko tinggi, namun tetap perlu dilakukan monitoring berkala.
2. Pelaksanaan klarifikasi dan audit sampling terhadap {fmt_num(sampling)} kasus dengan indikasi risiko sedang, terutama terkait konsistensi pengodean dan kelengkapan bukti medis pendukung.
3. {rekom_onsite.capitalize()}, khususnya pada kasus-kasus dengan skor KNAVP tertinggi dan diskrepansi dual coding yang signifikan.
4. Penyelenggaraan pembinaan dan peningkatan kompetensi tenaga koding di {rs_name}, terutama dalam hal penerapan aturan KNAVP kategori {dom_title} dan pemahaman perbedaan logika koding antara INA-CBG dan iDRG.
5. Peningkatan kelengkapan dokumentasi rekam medis, khususnya pada kasus-kasus yang memerlukan bukti klinis spesifik sebagai dasar penetapan diagnosis tingkat keparahan tinggi.
"""
    return md.strip()


def run(kode_rs: str, verbose: bool = True) -> str:
    """
    Jalankan template filler untuk satu RS.
    Return: path ke final_md yang dihasilkan.
    """
    if verbose:
        print(f"\n[TEMPLATE FILLER] RS: {kode_rs}")
        print("=" * 60)

    # Load metadata Agent 1
    meta_path = os.path.join(META_DIR, f'data_review_{kode_rs}.json')
    if not os.path.exists(meta_path):
        print(f"  [ERROR] Metadata tidak ditemukan: {meta_path}")
        print(f"  Jalankan Agent 1 terlebih dahulu.")
        return ""

    with open(meta_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    rs_name = metadata.get('_meta', {}).get('rs_name', kode_rs)
    if verbose:
        print(f"  RS: {rs_name}")

    # Build MD dari template
    md_content = build_template_md(metadata, kode_rs)

    # Simpan ke final_md (langsung skip Agent 2/3/4)
    out_path = os.path.join(DRAFT_OUT, f'final_md_{kode_rs}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    if verbose:
        word_count = len(md_content.split())
        print(f"  Template MD: {word_count:,} kata | {len(md_content):,} karakter")
        print(f"  Output: {out_path}")

    return md_content


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Template Filler — skip LLM Agent 2/3/4')
    parser.add_argument('--kode_rs', type=str, default='1275655')
    args = parser.parse_args()
    result = run(args.kode_rs)
    if result:
        print(f"\n[TEMPLATE FILLER] Selesai. {len(result.split())} kata.")
