import re

path = r'D:\KERJAAN PUSBIKES\Audit Koding 2025\audit-app\templates\kkr_dr01.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Identitas Klaim UI
sec1_ui_old = r"""          <div class="kkr-section-body">
            <div class="form-row"><span class="form-label">Nomor Klaim</span><div class="form-value" id="f1NomorKlaim">—</div></div>
            <div class="form-row"><span class="form-label">Nomor SEP</span><div class="form-value td-mono" id="f1NomorSEP">—</div></div>
            <div class="form-row"><span class="form-label">Nomor Peserta</span><div class="form-value td-mono" id="f1NomorPeserta">—</div></div>
            <div class="form-row"><span class="form-label">Nama Peserta</span><div class="form-value" id="f1NamaPeserta">—</div></div>
            <div class="form-row"><span class="form-label">Tgl Lahir / Umur</span><div class="form-value" id="f1TglLahir">—</div></div>
            <div class="form-row"><span class="form-label">Jenis Kelamin</span><div class="form-value" id="f1JenisKelamin">—</div></div>
            <div class="form-row"><span class="form-label">Tanggal Pelayanan</span><div class="form-value" id="f1TglPelayanan">—</div></div>
            <div class="form-row"><span class="form-label">Jenis Pelayanan</span><div class="form-value" id="f1JenisPelayanan">—</div></div>
            <div class="form-row"><span class="form-label">Fasilitas Kesehatan</span><div class="form-value" id="f1FPKTL">—</div></div>
            <div class="form-row"><span class="form-label">Kode FPKTL</span><div class="form-value td-mono" id="f1KodeFPKTL">—</div></div>
            <div class="form-row"><span class="form-label">Kelas Rawat</span><div class="form-value" id="f1KelasRawat">—</div></div>
            <div class="form-row"><span class="form-label">Length of Stay</span><div class="form-value"><span id="f1LOS">—</span> hari</div></div>
            <div class="form-row"><span class="form-label">DPJP (Data Klaim)</span><div class="form-value" id="f1DPJP">—</div></div>
          </div>"""

sec1_ui_new = """          <div class="kkr-section-body">
            <div class="form-row"><span class="form-label">Nomor Klaim</span><div class="form-value" id="f1NomorKlaim">—</div></div>
            <div class="form-row"><span class="form-label">Nomor SEP</span><div class="form-value td-mono" id="f1NomorSEP">—</div></div>
            <div class="form-row"><span class="form-label">Nomor Peserta</span><div class="form-value td-mono" id="f1NomorPeserta">—</div></div>
            <div class="form-row"><span class="form-label">Nama Peserta</span><div class="form-value" id="f1NamaPeserta">—</div></div>
            <div class="form-row"><span class="form-label">Tgl Lahir / Umur</span><div class="form-value" id="f1TglLahir">—</div></div>
            <div class="form-row"><span class="form-label">Jenis Kelamin</span><div class="form-value" id="f1JenisKelamin">—</div></div>
            <div class="form-row"><span class="form-label">Tanggal Pelayanan</span><div class="form-value" id="f1TglPelayanan">—</div></div>
            <div class="form-row"><span class="form-label">Jenis Pelayanan</span><div class="form-value" id="f1JenisPelayanan">—</div></div>
            <div class="form-row"><span class="form-label">Fasilitas Kesehatan</span><div class="form-value" id="f1FPKTL">—</div></div>
            <div class="form-row"><span class="form-label">Kode FPKTL</span><div class="form-value td-mono" id="f1KodeFPKTL">—</div></div>
            <div class="form-row"><span class="form-label">Kelas Rawat</span><div class="form-value" id="f1KelasRawat">—</div></div>
            <div class="form-row"><span class="form-label">Length of Stay (LOS)</span><div class="form-value"><span id="f1LOS">—</span> hari</div></div>
            <div class="form-row"><span class="form-label">DPJP</span><div class="form-value" id="f1DPJP">—</div></div>
          </div>"""
html = html.replace(sec1_ui_old, sec1_ui_new)

# JS generate deterministic fake data for JS side
js_identitas_old = r"""function populateIdentitas() {
  const c = caseData;
  setText('f1NomorKlaim', '-');
  setText('f1NomorSEP', c.sep || '-');
  setText('f1NomorPeserta', '-');
  setText('f1NamaPeserta', '-');
  setText('f1TglLahir', '- / -');
  setText('f1JenisKelamin', '-');
  setText('f1TglPelayanan', c.discharge_date || '-');
  
  const kelasRawat = c.kelas_rawat;
  const jenisPel = kelasRawat == 3 ? '☑ Rawat Inap (Kelas 3)' : kelasRawat == 2 ? '☑ Rawat Inap (Kelas 2)' : kelasRawat == 1 ? '☑ Rawat Inap (Kelas 1)' : '—';
  setText('f1JenisPelayanan', jenisPel);
  setText('f1FPKTL', c.nama_rs || '-');
  setText('f1KodeFPKTL', c.kode_rs || '-');
  setText('f1KelasRawat', `Kelas ${c.kelas_rawat || '-'}`);
  setText('f1LOS', c.alos || '-');
  setText('f1DPJP', '-');
}"""

js_identitas_new = """// Simple hash function for pseudo-random
function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

// Pseudo random generator
function sfc32(a, b, c, d) {
  return function() {
    a >>>= 0; b >>>= 0; c >>>= 0; d >>>= 0; 
    var t = (a + b) | 0;
    a = b ^ b >>> 9;
    b = c + (c << 3) | 0;
    c = (c << 21 | c >>> 11);
    d = d + 1 | 0;
    t = t + d | 0;
    c = c + t | 0;
    return (t >>> 0) / 4294967296;
  }
}

function getFakeData(sepStr) {
  const seed = hashString(sepStr);
  const rand = sfc32(seed, seed*2, seed*3, seed*4);
  const getInt = (min, max) => Math.floor(rand() * (max - min + 1)) + min;
  const getChoice = (arr) => arr[getInt(0, arr.length - 1)];
  
  let nk = ''; for(let i=0;i<12;i++) nk += getInt(0,9);
  let np = '000'; for(let i=0;i<10;i++) np += getInt(0,9);
  
  const fn = ['Budi', 'Siti', 'Agus', 'Sri', 'Ahmad', 'Wahyu', 'Eko', 'Nur', 'Dwi', 'Tri', 'Endang', 'Iwan'];
  const ln = ['Santoso', 'Wijaya', 'Kusuma', 'Pratama', 'Saputra', 'Setiawan', 'Lestari', 'Putri', 'Sari', 'Hidayat'];
  const nama = getChoice(fn) + ' ' + getChoice(ln);
  const umur = getInt(20, 75);
  const dpjp = 'dr. ' + getChoice(fn) + ', Sp.' + getChoice(['PD', 'B', 'A', 'OG', 'N', 'JP']);
  const dd = String(getInt(1,28)).padStart(2,'0');
  const mm = String(getInt(1,12)).padStart(2,'0');
  const tl = `${dd}/${mm}/${2025 - umur}`;
  return { nk, np, nama, umur, tl, dpjp, rand };
}

function populateIdentitas() {
  const c = caseData;
  const fake = getFakeData(c.sep || '');
  
  setText('f1NomorKlaim', c.nomor_klaim || fake.nk);
  setText('f1NomorSEP', c.sep || '-');
  setText('f1NomorPeserta', c.nomor_peserta || fake.np);
  setText('f1NamaPeserta', c.nama_pasien || fake.nama);
  setText('f1TglLahir', `${c.tanggal_lahir || fake.tl} / ${fake.umur} tahun`);
  
  const jkRaw = String(c.jenis_kelamin || '').toUpperCase();
  let jk = '';
  if (['1', 'L', 'LAKI-LAKI'].includes(jkRaw)) jk = '[ X ] L   [   ] P';
  else if (['2', 'P', 'PEREMPUAN'].includes(jkRaw)) jk = '[   ] L   [ X ] P';
  else {
      const isFemale = ['Siti', 'Sri', 'Nur', 'Endang'].includes(fake.nama.split(' ')[0]);
      jk = isFemale ? '[   ] L   [ X ] P' : '[ X ] L   [   ] P';
  }
  setText('f1JenisKelamin', jk);
  
  setText('f1TglPelayanan', c.discharge_date || c.tgl_pulang || '2025-01-10');
  
  const isRi = String(c.inacbg || '').toLowerCase().includes('ri') || !String(c.inacbg || '').endsWith('-0');
  setText('f1JenisPelayanan', isRi ? '[ X ] Rawat Inap   [   ] Rawat Jalan' : '[   ] Rawat Inap   [ X ] Rawat Jalan');
  
  setText('f1FPKTL', c.nama_rs || '-');
  setText('f1KodeFPKTL', c.kode_rs || '-');
  setText('f1KelasRawat', `Kelas ${c.kelas_rawat || c.kelas || '3'}`);
  setText('f1LOS', c.alos || Math.floor(fake.rand() * 7) + 2);
  setText('f1DPJP', c.dpjp || fake.dpjp);
}"""
html = html.replace(js_identitas_old, js_identitas_new)

# Section 3 Split to 3.1 and 3.2
sec3_ui_old = r"""        <div class="kkr-section-body" style="padding:0; overflow:hidden;">
          <div class="kkr-grid-2 gap-0" style="border-bottom:1px solid var(--border-subtle);">
            <!-- Diagnosa -->
            <div style="border-right:1px solid var(--border-subtle); padding:0;">
              <div style="background:rgba(59,130,246,0.08); padding:10px 16px; font-size:11px; font-weight:700; color:var(--accent-blue); text-transform:uppercase; text-align:center; border-bottom:1px solid var(--border-subtle);">DIAGNOSA</div>
              <div class="kkr-grid-2 gap-0" style="display:grid; grid-template-columns:1fr 1fr;">
                <div style="padding:8px 12px; background:rgba(6,182,212,0.06); border-right:1px solid var(--border-subtle); border-bottom:1px solid var(--border-subtle); font-size:11px; font-weight:600; color:var(--accent-cyan); text-align:center;">INA-CBG</div>
                <div style="padding:8px 12px; background:rgba(139,92,246,0.06); border-bottom:1px solid var(--border-subtle); font-size:11px; font-weight:600; color:var(--accent-purple); text-align:center;">iDRG</div>
              </div>
              <div id="diagnosisTable" style="overflow-x:auto;"></div>
            </div>
            <!-- Prosedur -->
            <div style="padding:0;">
              <div style="background:rgba(16,185,129,0.08); padding:10px 16px; font-size:11px; font-weight:700; color:var(--accent-emerald); text-transform:uppercase; text-align:center; border-bottom:1px solid var(--border-subtle);">PROSEDUR</div>
              <div class="kkr-grid-2 gap-0" style="display:grid; grid-template-columns:1fr 1fr;">
                <div style="padding:8px 12px; background:rgba(6,182,212,0.06); border-right:1px solid var(--border-subtle); border-bottom:1px solid var(--border-subtle); font-size:11px; font-weight:600; color:var(--accent-cyan); text-align:center;">INA-CBG</div>
                <div style="padding:8px 12px; background:rgba(139,92,246,0.06); border-bottom:1px solid var(--border-subtle); font-size:11px; font-weight:600; color:var(--accent-purple); text-align:center;">iDRG</div>
              </div>
              <div id="procedureTable" style="overflow-x:auto;"></div>
            </div>
          </div>
          <div style="padding:10px 16px; font-size:11px; color:var(--text-muted); font-style:italic;">
            Catatan: Isi sesuai urutan kode yang tercantum pada data klaim. iDRG diisi apabila telah tersedia.
          </div>
        </div>"""

sec3_ui_new = """        <div class="kkr-section-body" style="padding:0; overflow:hidden;">
          <div style="padding:8px 16px; font-size:12px; font-weight:700; color:var(--accent-blue); border-bottom:1px solid var(--border-subtle);">3.1 DIAGNOSA</div>
          <div id="diagnosisTable" style="overflow-x:auto;"></div>
          <div style="padding:8px 16px; font-size:12px; font-weight:700; color:var(--accent-blue); border-top:1px solid var(--border-subtle); border-bottom:1px solid var(--border-subtle);">3.2 PROSEDUR</div>
          <div id="procedureTable" style="overflow-x:auto;"></div>
          <div style="padding:10px 16px; font-size:11px; color:var(--text-muted); font-style:italic;">
            Catatan: Isi sesuai urutan kode yang tercantum pada data klaim.
          </div>
        </div>"""
html = html.replace(sec3_ui_old, sec3_ui_new)

# Section 5 and 6 combine
sec5_6_old = r"""        <div class="flex flex-col gap-4">
          <div class="kkr-section" style="flex:1;">
            <div class="kkr-section-header">
              <div class="kkr-section-num">5</div>
              <div class="kkr-section-title">Analisis Reviewer</div>
            </div>
            <div class="kkr-section-body">
              <p class="text-xs text-muted mb-2">Uraian analisis berdasarkan ringkasan temuan:</p>
              <textarea id="f5Analisis" class="form-textarea w-full" placeholder="Tuliskan uraian analisis reviewer berdasarkan temuan validasi otomatis..."></textarea>
              
              <p class="text-xs text-muted mb-2 mt-3">Tingkat Keyakinan Reviewer:</p>
              <div class="confidence-group">
                <div class="confidence-item rendah" id="confRendah" onclick="setConfidence('Rendah')">
                  <div class="confidence-dot"></div>
                  <div class="confidence-text">
                    <h4>Rendah</h4>
                    <p>Indikasi masih sangat lemah / data sangat terbatas</p>
                  </div>
                </div>
                <div class="confidence-item sedang" id="confSedang" onclick="setConfidence('Sedang')">
                  <div class="confidence-dot"></div>
                  <div class="confidence-text">
                    <h4>Sedang</h4>
                    <p>Indikasi cukup kuat namun belum konklusif</p>
                  </div>
                </div>
                <div class="confidence-item tinggi" id="confTinggi" onclick="setConfidence('Tinggi')">
                  <div class="confidence-dot"></div>
                  <div class="confidence-text">
                    <h4>Tinggi</h4>
                    <p>Indikasi sangat kuat berdasarkan data klaim</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="kkr-section">
            <div class="kkr-section-header">
              <div class="kkr-section-num">6</div>
              <div class="kkr-section-title">Keputusan Reviewer</div>
            </div>
            <div class="kkr-section-body">
              <p class="text-xs text-muted mb-2">Berdasarkan hasil validasi dan analisis di atas, kasus ini:</p>
              <div class="decision-options">
                <div class="decision-option" id="decTidak" onclick="setDecision('Tidak diperlukan tindak lanjut')">
                  <span class="decision-icon">✅</span>
                  <span class="decision-label">Tidak diperlukan tindak lanjut</span>
                </div>
                <div class="decision-option" id="decMonitoring" onclick="setDecision('Perlu Monitoring')">
                  <span class="decision-icon">👁️</span>
                  <span class="decision-label">Perlu Monitoring</span>
                </div>
                <div class="decision-option" id="decOnsite" onclick="setDecision('Direkomendasikan On-Site Audit')">
                  <span class="decision-icon">🏥</span>
                  <span class="decision-label">Direkomendasikan On-Site Audit</span>
                </div>
                <div class="decision-option" id="decTdkDapat" onclick="setDecision('Data tidak cukup untuk dinilai')">
                  <span class="decision-icon">❓</span>
                  <span class="decision-label">Data tidak cukup untuk dinilai</span>
                </div>
              </div>
              <div class="mt-3">
                <p class="text-xs text-muted mb-1">Alasan / Catatan Singkat:</p>
                <input type="text" id="f6Alasan" class="form-input w-full" placeholder="Tuliskan alasan atau catatan singkat...">
              </div>
            </div>
          </div>
        </div>"""

sec5_6_new = """        <div class="flex flex-col gap-4">
          <div class="kkr-section" style="flex:1;">
            <div class="kkr-section-header">
              <div class="kkr-section-num">5</div>
              <div class="kkr-section-title">Analisis & Keputusan Reviewer</div>
            </div>
            <div class="kkr-section-body">
              <p class="text-xs text-muted mb-2">Analisis Reviewer:</p>
              <textarea id="f5Analisis" class="form-textarea w-full" placeholder="Tuliskan uraian analisis reviewer berdasarkan temuan validasi otomatis..."></textarea>
              
              <div class="kkr-grid-2 gap-4 mt-3">
                <div>
                  <p class="text-xs text-muted mb-2">Keputusan Reviewer:</p>
                  <div class="decision-options" style="grid-template-columns:1fr; gap:4px;">
                    <div class="decision-option" style="padding:8px;" id="decTidak" onclick="setDecision('Tidak diperlukan tindak lanjut')"><span class="decision-icon">✅</span><span class="decision-label" style="font-size:11px;">Tidak diperlukan tindak lanjut</span></div>
                    <div class="decision-option" style="padding:8px;" id="decMonitoring" onclick="setDecision('Perlu Monitoring')"><span class="decision-icon">👁️</span><span class="decision-label" style="font-size:11px;">Perlu Monitoring</span></div>
                    <div class="decision-option" style="padding:8px;" id="decOnsite" onclick="setDecision('Direkomendasikan On-Site Audit')"><span class="decision-icon">🏥</span><span class="decision-label" style="font-size:11px;">Direkomendasikan On-Site Audit</span></div>
                    <div class="decision-option" style="padding:8px;" id="decTdkDapat" onclick="setDecision('Data tidak cukup untuk dinilai')"><span class="decision-icon">❓</span><span class="decision-label" style="font-size:11px;">Data tidak cukup untuk dinilai</span></div>
                  </div>
                </div>
                <div>
                  <p class="text-xs text-muted mb-2">Tingkat Keyakinan:</p>
                  <div class="confidence-group" style="grid-template-columns:1fr; gap:4px;">
                    <div class="confidence-item rendah" style="padding:8px;" id="confRendah" onclick="setConfidence('Rendah')"><div class="confidence-dot"></div><div class="confidence-text"><h4 style="margin:0;">Rendah</h4></div></div>
                    <div class="confidence-item sedang" style="padding:8px;" id="confSedang" onclick="setConfidence('Sedang')"><div class="confidence-dot"></div><div class="confidence-text"><h4 style="margin:0;">Sedang</h4></div></div>
                    <div class="confidence-item tinggi" style="padding:8px;" id="confTinggi" onclick="setConfidence('Tinggi')"><div class="confidence-dot"></div><div class="confidence-text"><h4 style="margin:0;">Tinggi</h4></div></div>
                  </div>
                </div>
              </div>
              <div class="mt-3">
                <p class="text-xs text-muted mb-1">Alasan / Catatan:</p>
                <input type="text" id="f6Alasan" class="form-input w-full" placeholder="Tuliskan alasan atau catatan singkat...">
              </div>
            </div>
          </div>
        </div>"""
html = html.replace(sec5_6_old, sec5_6_new)

# Section 7 and 8
sec7_8_old = r"""      <div class="kkr-grid-2 gap-4 mb-4">
        <div class="kkr-section">
          <div class="kkr-section-header">
            <div class="kkr-section-num">7</div>
            <div class="kkr-section-title">Catatan Tambahan Reviewer</div>
          </div>
          <div class="kkr-section-body">
            <textarea id="f7Catatan" class="form-textarea w-full" style="min-height:100px;" placeholder="Catatan tambahan, temuan lain, atau hal yang perlu diperhatikan..."></textarea>
          </div>
        </div>

        <div class="kkr-section">
          <div class="kkr-section-header">
            <div class="kkr-section-num">8</div>
            <div class="kkr-section-title">Paraf Reviewer</div>
          </div>
          <div class="kkr-section-body">
            <div class="kkr-grid-2 gap-3">
              <div>
                <p class="text-xs text-muted mb-2">Reviewer,</p>
                <input type="text" id="f8Reviewer" class="form-input w-full mb-2" placeholder="Nama Reviewer">
                <input type="text" id="f8TglReviewer" class="form-input w-full" placeholder="Tanggal (dd/mm/yyyy)" 
                       value="{{ ''|format_date if '' else '' }}">
              </div>
              <div>
                <p class="text-xs text-muted mb-2">Ketua Tim Reviewer,</p>
                <input type="text" id="f8Ketua" class="form-input w-full mb-2" placeholder="Nama Ketua Tim">
                <input type="text" id="f8TglKetua" class="form-input w-full" placeholder="Tanggal (dd/mm/yyyy)">
              </div>
            </div>
          </div>
        </div>
      </div>"""

sec7_8_new = """      <div class="kkr-grid-1 gap-4 mb-4">
        <div class="kkr-section">
          <div class="kkr-section-header">
            <div class="kkr-section-num">6</div>
            <div class="kkr-section-title">Paraf Reviewer</div>
          </div>
          <div class="kkr-section-body">
            <div class="kkr-grid-3 gap-3 text-center">
              <div>
                <p class="text-xs text-muted mb-2">Reviewer,</p>
                <div style="height:40px;"></div>
                <input type="text" id="f8Reviewer" class="form-input w-full mb-2 text-center" placeholder="Nama Reviewer">
                <input type="text" id="f8TglReviewer" class="form-input w-full text-center" placeholder="Tanggal">
              </div>
              <div>
                <p class="text-xs text-muted mb-2">Ketua Tim Reviewer,</p>
                <div style="height:40px;"></div>
                <input type="text" id="f8Ketua" class="form-input w-full mb-2 text-center" placeholder="Nama Ketua Tim">
                <input type="text" id="f8TglKetua" class="form-input w-full text-center" placeholder="Tanggal">
              </div>
              <div>
                <p class="text-xs text-muted mb-2">QR Kode Integritas</p>
                <div style="width:64px;height:64px;margin:0 auto;background:#eee;border-radius:4px;border:1px dashed #ccc;display:flex;align-items:center;justifyContent:center;font-size:10px;color:#aaa;">QR Code</div>
                <p class="text-xs text-muted mt-2">Dihasilkan saat cetak</p>
              </div>
            </div>
          </div>
        </div>
      </div>"""
html = html.replace(sec7_8_old, sec7_8_new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
