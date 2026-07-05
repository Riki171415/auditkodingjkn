import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ChevronLeft, Save, Printer, SquareActivity } from 'lucide-react';
import axios from 'axios';

// ── CCL label (fallback jika tidak dikirim API) ──────────────────────────────
function parseCCL(idrgCode) {
  const map = { '0': 'No CC', '1': 'Mild CC', '2': 'Moderate CC',
                '3': 'Severe CC', '4': 'Catastrophic CC', '9': 'Merge CC' };
  if (!idrgCode) return '-';
  const last = String(idrgCode).trim().slice(-1);
  return map[last] || '-';
}

// ── Risk Gauge component ─────────────────────────────────────────────────────
function RiskGauge({ tingkat }) {
  const levels = ['Rendah', 'Sedang', 'Tinggi'];
  const colors = { Rendah: '#22c55e', Sedang: '#f59e0b', Tinggi: '#ef4444' };
  const current = levels.indexOf(tingkat);
  return (
    <div style={{ display: 'flex', gap: 4, marginTop: 6, justifyContent: 'center' }}>
      {levels.map((l, i) => (
        <div key={l} style={{
          flex: 1, textAlign: 'center', padding: '3px 0', fontSize: 9, fontWeight: 700,
          background: i === current ? colors[l] : '#e5e7eb',
          color: i === current ? 'white' : '#9ca3af',
          borderRadius: 3, border: `1px solid ${i === current ? colors[l] : '#d1d5db'}`
        }}>
          {l}
        </div>
      ))}
    </div>
  );
}

export default function KKRForm() {
  const { sep } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    catatan_sistem: '',
    reviewer_name: '',
    nip_reviewer: '',
    tanggal_review: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    axios.get(`/api/validate/${encodeURIComponent(sep)}`)
      .then(res => {
        setData(res.data.data);
        setLoading(false);
        axios.get(`/api/kkr-dr01/load/${encodeURIComponent(sep)}`)
          .then(res_load => {
            if (res_load.data.data?.form_data) {
              const fd = res_load.data.data.form_data;
              setFormData(f => ({
                ...f,
                catatan_sistem: fd.catatan_sistem || fd.catatan_tambahan || '',
                reviewer_name: fd.reviewer_name || '',
                nip_reviewer: fd.nip_reviewer || '',
                tanggal_review: fd.tanggal_review || f.tanggal_review,
              }));
            }
          }).catch(() => {});
      })
      .catch(() => setLoading(false));
  }, [sep]);

  const handleSave = () => {
    setSaving(true);
    const knavp = data?.knavp || {};
    const payload = {
      kode_rs: data.case.kode_rs,
      sep,
      triggered_rules: data.triggered_rules,
      keputusan: knavp.keputusan_sistem || '',
      alasan_keputusan: `Skor KNAVP: ${knavp.total_skor || 0} | Tingkat Risiko: ${knavp.tingkat_risiko || '-'} | Perbedaan Dual Coding: ${data?.dual_coding?.jumlah_beda_total || 0}`,
      ...formData
    };
    axios.post('/api/kkr-dr01/save', payload)
      .then(() => { alert('KKR Berhasil Disimpan!'); setSaving(false); })
      .catch(() => { alert('Gagal menyimpan'); setSaving(false); });
  };

  if (loading) return (
    <div className="fade-in" style={{ display:'flex', justifyContent:'center', padding:60 }}>
      <div className="spinner" style={{ width:40, height:40, border:'4px solid var(--kmk-cyan)', borderTopColor:'transparent', borderRadius:'50%' }} />
    </div>
  );
  if (!data) return <div>Gagal memuat formulir.</div>;

  const { case: c, triggered_rules, dual_coding, knavp, ccl_label } = data;
  const diags = c.diaglist ? c.diaglist.split(';').map(x => x.trim()).filter(Boolean) : [];
  const procs = c.proclist ? c.proclist.split(';').map(x => x.trim()).filter(Boolean) : [];
  const jumlahDiag = diags.length;
  const jumlahProc = procs.length;

  // Dual coding rows (from API or fallback to simple compare)
  const diagRows  = dual_coding?.diag_rows  || [];
  const procRows  = dual_coding?.proc_rows  || [];
  const maxDiagRows = Math.max(diagRows.length, 5);
  const maxProcRows = Math.max(procRows.length, 5);

  // Section 4 KNAVP table (min 5 rows)
  const maxRuleRows = Math.max(triggered_rules.length, 5);

  // Rekomendasi sistem (auto)
  const rekSistem = knavp?.keputusan_sistem || 'Tidak perlu tindak lanjut';
  const totalSkor = knavp?.total_skor ?? 0;
  const tingkatRisiko = knavp?.tingkat_risiko ?? 'Rendah';

  const isOnSite   = rekSistem.includes('On-Site');
  const isSampling = rekSistem.includes('Sampling');
  const isMonitor  = rekSistem.includes('Monitoring') && !isOnSite && !isSampling;

  // Styles helpers
  const TH = ({ children, style = {} }) => (
    <th style={{ background: '#1e3a5f', color: 'white', fontSize: 9, fontWeight: 700,
                 padding: '3px 4px', border: '1px solid #0e3c6c', textAlign: 'center', ...style }}>
      {children}
    </th>
  );
  const TD = ({ children, style = {} }) => (
    <td style={{ fontSize: 9, padding: '3px 4px', border: '1px solid #bcd', verticalAlign: 'middle', ...style }}>
      {children}
    </td>
  );
  const chk = (checked) => checked ? '☑' : '☐';

  return (
    <div className="fade-in" style={{ padding: '20px 0' }}>
      {/* Top Action Bar */}
      <div className="no-print" style={{ maxWidth: 1000, margin: '0 auto 16px', display: 'flex', justifyContent: 'space-between' }}>
        <button onClick={() => window.history.back()} className="btn btn-outline" style={{ border: 'none', padding: 0 }}>
          <ChevronLeft size={16} /> Kembali
        </button>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-outline" onClick={() => window.print()}>
            <Printer size={16} /> Cetak / PDF
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            <Save size={16} /> {saving ? 'Menyimpan...' : 'Simpan KKR'}
          </button>
        </div>
      </div>

      {/* ── A4 Page ── */}
      <div className="kkr-page" style={{ maxWidth: 1000, margin: '0 auto', background: 'white', padding: 28, boxShadow: '0 4px 12px rgba(0,0,0,0.1)', fontFamily: 'Arial, sans-serif' }}>

        {/* ════════════════════ HEADER ════════════════════ */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto auto', gap: 0, border: '2px solid #0e3c6c', marginBottom: 0 }}>
          {/* Logo + Title */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', borderRight: '1px solid #0e3c6c' }}>
            <SquareActivity size={30} color="#0e3c6c" />
            <div>
              <div style={{ fontSize: 8, fontWeight: 700, color: '#0e3c6c', lineHeight: 1.3 }}>KEMENTERIAN KESEHATAN<br/>REPUBLIK INDONESIA</div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#0e3c6c', marginTop: 4 }}>KERTAS KERJA REVIEWER – DESK REVIEW</div>
              <div style={{ fontSize: 9, color: '#00838f', fontWeight: 600 }}>HASIL VALIDASI OTOMATIS</div>
              <div style={{ fontSize: 8, marginTop: 2, color: '#444' }}>AUDIT CODING DAN VERIFIKASI DUAL CODING</div>
              <div style={{ fontSize: 7.5, color: '#666' }}>Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)</div>
            </div>
          </div>
          {/* Doc info */}
          <div style={{ padding: '6px 10px', borderRight: '1px solid #0e3c6c', minWidth: 150 }}>
            <table style={{ fontSize: 8, borderCollapse: 'collapse', width: '100%' }}>
              <tbody>
                <tr><td style={{ fontWeight: 700, paddingRight: 4 }}>KODE DOKUMEN</td><td>: KKR-DR01</td></tr>
                <tr><td style={{ fontWeight: 700 }}>VERSI</td><td>: 1.0</td></tr>
                <tr><td style={{ fontWeight: 700 }}>TANGGAL BERLAKU</td><td>: __/__/____</td></tr>
                <tr><td style={{ fontWeight: 700 }}>HALAMAN</td><td>: 1 dari 1</td></tr>
              </tbody>
            </table>
          </div>
          {/* KKR-DR01 big block */}
          <div style={{ background: '#0e3c6c', padding: '8px 14px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minWidth: 110 }}>
            <div style={{ fontSize: 18, fontWeight: 900, color: 'white', letterSpacing: 1 }}>KKR-DR01</div>
            <div style={{ fontSize: 7, color: '#7dd3fc', marginTop: 2, textAlign: 'center' }}>KODE DOKUMEN</div>
          </div>
        </div>

        {/* Banner kuning */}
        <div style={{ background: '#fef08a', border: '1.5px solid #eab308', borderTop: 'none', padding: '4px 10px', textAlign: 'center', fontSize: 9, fontWeight: 700, color: '#713f12', letterSpacing: 0.5 }}>
          BERDASARKAN DATA KLAIM – TANPA TELAAH REKAM MEDIS
        </div>

        {/* ════════════════════ SECTION 1: IDENTITAS KLAIM ════════════════════ */}
        <div className="kkr-section-header" style={{ marginTop: 10 }}>1. IDENTITAS KLAIM (DATA KLAIM DATA CENTER)</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 0, border: '1px solid #0e3c6c' }}>
          {/* Panel kiri: identitas pasien */}
          <div style={{ borderRight: '1px solid #0e3c6c' }}>
            <table className="kkr-data-table" style={{ width: '100%' }}>
              <tbody>
                {[
                  ['Nomor Klaim', ':  ……………………………'],
                  ['Nomor SEP', `: ${c.sep}`],
                  ['Nomor Peserta', ':  ……………………………'],
                  ['Nama Peserta', `: ${c.nama_pasien || '……………………………'}`],
                  ['Tanggal Lahir / Umur', `: ${c.tanggal_lahir || '__/__/____'} / …… tahun`],
                  ['Jenis Kelamin', `: ${c.jenis_kelamin == '1' || c.jenis_kelamin == 'L' ? '☑ Laki-laki  ☐ Perempuan' : '☐ Laki-laki  ☑ Perempuan'}`],
                  ['Fasilitas Kesehatan (FKRTL)', `: ${c.nama_rs}`],
                  ['Kode FPKTL', `: ${c.kode_rs}`],
                  ['Kelas Rawat', `: ${c.kelas_rawat || '-'}`],
                ].map(([label, val]) => (
                  <tr key={label}>
                    <td width="42%" style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>{label}</td>
                    <td style={{ fontSize: 9, padding: '2px 6px', fontFamily: label === 'Nomor SEP' ? 'monospace' : 'inherit' }}>{val}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Panel kanan: info pelayanan */}
          <div style={{ borderRight: '1px solid #0e3c6c' }}>
            <table className="kkr-data-table" style={{ width: '100%' }}>
              <tbody>
                <tr>
                  <td width="50%" style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Tanggal Pelayanan</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {c.discharge_date} s.d. {c.discharge_date}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Jenis Pelayanan</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>
                    : {c.rw ? '☑ Rawat Inap  ☐ Rawat Jalan' : '☐ Rawat Inap  ☑ Rawat Jalan'}
                  </td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>DPJP (Data Klaim)</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: ……………………………</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Sumber Data</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: ☑ INA-CBG  ☑ iDRG</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Waktu Proses Sistem</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {new Date().toLocaleString('id-ID')}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Versi Grouper</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: INA-CBG __  iDRG __</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Jumlah Diagnosis (Klaim)</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {jumlahDiag}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Jumlah Prosedur (Klaim)</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {jumlahProc}</td>
                </tr>
              </tbody>
            </table>
          </div>
          {/* Barcode klaim */}
          <div style={{ width: 90, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 8, gap: 4 }}>
            <div style={{ fontSize: 7, fontWeight: 700, color: '#0e3c6c', textAlign: 'center' }}>BARCODE KLAIM</div>
            <div style={{ width: 70, height: 50, background: '#f1f5f9', border: '1px dashed #94a3b8', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ fontSize: 6, color: '#94a3b8', textAlign: 'center' }}>Tempel /<br/>Scan</div>
            </div>
          </div>
        </div>

        {/* ════════════════════ SECTION 2: GROUPING & TARIF ════════════════════ */}
        <div className="kkr-section-header" style={{ marginTop: 8 }}>2. INFORMASI GROUPING DAN TARIF</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, border: '1px solid #0e3c6c' }}>
          {/* INA-CBG */}
          <div style={{ borderRight: '1px solid #0e3c6c' }}>
            <div style={{ background: '#0369a1', color: 'white', textAlign: 'center', fontSize: 9, fontWeight: 700, padding: '2px 0' }}>INA-CBG (Klaim)</div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 9 }}>
              <thead>
                <tr>
                  {['Kode INA-CBG', 'Deskripsi INA-CBG', 'Group', 'Tarif (Rp)'].map(h => (
                    <th key={h} style={{ background: '#dbeafe', border: '1px solid #93c5fd', padding: '2px 4px', fontSize: 8 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ border: '1px solid #bcd', padding: '2px 4px', fontFamily: 'monospace', fontWeight: 700, color: '#0369a1' }}>{c.inacbg || '-'}</td>
                  <td style={{ border: '1px solid #bcd', padding: '2px 4px', fontSize: 8 }}>{c.deskripsi_inacbg || '-'}</td>
                  <td style={{ border: '1px solid #bcd', padding: '2px 4px', textAlign: 'center' }}>-</td>
                  <td style={{ border: '1px solid #bcd', padding: '2px 4px', textAlign: 'right' }}>{c.tarif_inacbg?.toLocaleString('id-ID') || '-'}</td>
                </tr>
              </tbody>
            </table>
          </div>
          {/* iDRG */}
          <div>
            <div style={{ background: '#7c3aed', color: 'white', textAlign: 'center', fontSize: 9, fontWeight: 700, padding: '2px 0' }}>iDRG (Dual Coding)</div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 9 }}>
              <thead>
                <tr>
                  {['Kode iDRG', 'Deskripsi iDRG', 'CCL', 'Tarif (Rp)'].map(h => (
                    <th key={h} style={{ background: '#ede9fe', border: '1px solid #c4b5fd', padding: '2px 4px', fontSize: 8 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ border: '1px solid #bcd', padding: '2px 4px', fontFamily: 'monospace', fontWeight: 700, color: '#7c3aed' }}>{c.idrg_code || '-'}</td>
                  <td style={{ border: '1px solid #bcd', padding: '2px 4px', fontSize: 8 }}>{c.deskripsi_idrg || '-'}</td>
                  <td style={{ border: '1px solid #bcd', padding: '2px 4px', textAlign: 'center', fontSize: 8 }}>{ccl_label || parseCCL(c.idrg_code)}</td>
                  <td style={{ border: '1px solid #bcd', padding: '2px 4px', textAlign: 'right' }}>-</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        {/* Komponen Tarif + Catatan */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, border: '1px solid #0e3c6c', borderTop: 'none' }}>
          <div style={{ borderRight: '1px solid #0e3c6c' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 9 }}>
              <thead>
                <tr>
                  <th style={{ background: '#f1f5f9', border: '1px solid #bcd', padding: '2px 6px', textAlign: 'left' }}>KOMPONEN TARIF</th>
                  <th style={{ background: '#f1f5f9', border: '1px solid #bcd', padding: '2px 6px' }}>NILAI (Rp)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Tarif Klaim (INA-CBG)', c.tarif_inacbg?.toLocaleString('id-ID')],
                  ['Tarif RS (Tarif Standar)', c.tarif_rs?.toLocaleString('id-ID')],
                  ['Selisih (Tarif Klaim – Tarif RS)', ((c.tarif_inacbg || 0) - (c.tarif_rs || 0)).toLocaleString('id-ID')],
                ].map(([label, val]) => (
                  <tr key={label}>
                    <td style={{ border: '1px solid #bcd', padding: '2px 6px', fontWeight: 700 }}>{label}</td>
                    <td style={{ border: '1px solid #bcd', padding: '2px 6px', textAlign: 'right' }}>Rp {val}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ padding: 8, fontSize: 8, color: '#444' }}>
            <span style={{ fontWeight: 700, color: '#0e3c6c' }}>Catatan:</span><br/>
            Informasi iDRG merupakan hasil dual coding otomatis oleh sistem berdasarkan data klaim tanpa telaah rekam medis.
          </div>
        </div>

        {/* ════════════════════ SECTION 3: DUAL CODING ════════════════════ */}
        <div className="kkr-section-header" style={{ marginTop: 8 }}>3. INFORMASI DUAL CODING – HASIL PERBANDINGAN OTOMATIS</div>
        {/* Sub-header DIAGNOSA */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0 }}>
          <div style={{ background: '#0369a1', color: 'white', textAlign: 'center', fontSize: 8, fontWeight: 700, padding: '2px 0', border: '1px solid #0e3c6c', borderRight: 'none' }}>DIAGNOSA</div>
          <div style={{ background: '#7c3aed', color: 'white', textAlign: 'center', fontSize: 8, fontWeight: 700, padding: '2px 0', border: '1px solid #0e3c6c' }}>PROSEDUR / TINDAKAN</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, border: '1px solid #0e3c6c', borderTop: 'none' }}>
          {/* Diagnosa table */}
          <div style={{ borderRight: '1px solid #0e3c6c' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <TH style={{ width: '4%' }}>No.</TH>
                  <TH colSpan={2} style={{ background: '#1d4ed8' }}>INA-CBG (Klaim)</TH>
                  <TH colSpan={2} style={{ background: '#6d28d9' }}>iDRG (Dual Coding)</TH>
                  <TH style={{ width: '16%' }}>Hasil<br/>Perbandingan</TH>
                  <TH style={{ width: '12%' }}>Ket. Sistem</TH>
                </tr>
                <tr>
                  <TH></TH>
                  <TH>Kode ICD-10</TH>
                  <TH>Deskripsi</TH>
                  <TH>Kode ICD-10</TH>
                  <TH>Deskripsi</TH>
                  <TH></TH>
                  <TH></TH>
                </tr>
              </thead>
              <tbody>
                {[...Array(maxDiagRows)].map((_, i) => {
                  const row = diagRows[i];
                  const sesuai = row?.sesuai;
                  const rowColor = row && !sesuai ? '#fef2f2' : 'white';
                  const codeColor = row && !sesuai ? '#dc2626' : 'inherit';
                  return (
                    <tr key={i} style={{ background: rowColor }}>
                      <TD style={{ textAlign: 'center' }}>{i + 1}</TD>
                      <TD style={{ fontFamily: 'monospace', color: codeColor, textAlign: 'center' }}>{row?.ina_code || ''}</TD>
                      <TD style={{ fontSize: 7.5, color: codeColor }}>{row?.ina_desc || ''}</TD>
                      <TD style={{ fontFamily: 'monospace', color: codeColor, textAlign: 'center' }}>{row?.idrg_code || ''}</TD>
                      <TD style={{ fontSize: 7.5, color: codeColor }}>{row?.idrg_desc || ''}</TD>
                      <TD style={{ textAlign: 'center', fontSize: 9 }}>
                        {row ? (sesuai ? <span style={{ color: '#16a34a' }}>☑ Sesuai</span> : <span style={{ color: '#dc2626' }}>☑ Tidak Sesuai</span>) : ''}
                      </TD>
                      <TD style={{ fontSize: 7.5, color: row && !sesuai ? '#dc2626' : '#555' }}>
                        {row?.keterangan || ''}
                      </TD>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {/* Prosedur table */}
          <div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <TH style={{ width: '4%' }}>No.</TH>
                  <TH colSpan={2} style={{ background: '#1d4ed8' }}>INA-CBG (Klaim)</TH>
                  <TH colSpan={2} style={{ background: '#6d28d9' }}>iDRG (Dual Coding)</TH>
                  <TH style={{ width: '16%' }}>Hasil<br/>Perbandingan</TH>
                  <TH style={{ width: '12%' }}>Ket. Sistem</TH>
                </tr>
                <tr>
                  <TH></TH>
                  <TH>Kode ICD-9-CM / ICD-10-PCS</TH>
                  <TH>Deskripsi</TH>
                  <TH>Kode ICD-9-CM / ICD-10-PCS</TH>
                  <TH>Deskripsi</TH>
                  <TH></TH>
                  <TH></TH>
                </tr>
              </thead>
              <tbody>
                {[...Array(maxProcRows)].map((_, i) => {
                  const row = procRows[i];
                  const sesuai = row?.sesuai;
                  const rowColor = row && !sesuai ? '#fef2f2' : 'white';
                  const codeColor = row && !sesuai ? '#dc2626' : 'inherit';
                  return (
                    <tr key={i} style={{ background: rowColor }}>
                      <TD style={{ textAlign: 'center' }}>{i + 1}</TD>
                      <TD style={{ fontFamily: 'monospace', color: codeColor, textAlign: 'center' }}>{row?.ina_code || ''}</TD>
                      <TD style={{ fontSize: 7.5, color: codeColor }}>{row?.ina_desc || ''}</TD>
                      <TD style={{ fontFamily: 'monospace', color: codeColor, textAlign: 'center' }}>{row?.idrg_code || ''}</TD>
                      <TD style={{ fontSize: 7.5, color: codeColor }}>{row?.idrg_desc || ''}</TD>
                      <TD style={{ textAlign: 'center', fontSize: 9 }}>
                        {row ? (sesuai ? <span style={{ color: '#16a34a' }}>☑ Sesuai</span> : <span style={{ color: '#dc2626' }}>☑ Tidak Sesuai</span>) : ''}
                      </TD>
                      <TD style={{ fontSize: 7.5, color: row && !sesuai ? '#dc2626' : '#555' }}>
                        {row?.keterangan || ''}
                      </TD>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
        <div style={{ fontSize: 8, marginTop: 2, color: '#555' }}>
          Keterangan: <span style={{ marginRight: 12 }}>☑ Sesuai : Kode &amp; Deskripsi antara INA-CBG dan iDRG sama</span>
          <span>☑ Tidak Sesuai : Kode atau deskripsi berbeda</span>
        </div>

        {/* ════════════════════ SECTION 4: KNAVP ════════════════════ */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 8, marginTop: 8, alignItems: 'start' }}>
          <div>
            <div className="kkr-section-header">4. HASIL VALIDASI RULE OTOMATIS (KNAVP)</div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <TH style={{ width: '4%' }}>No.</TH>
                  <TH style={{ width: '13%' }}>Rule ID (KNAVP)</TH>
                  <TH style={{ width: '15%' }}>Kelompok Rule</TH>
                  <TH>Deskripsi Rule / Pesan Validasi</TH>
                  <TH style={{ width: '18%' }}>Status Sistem</TH>
                  <TH style={{ width: '6%' }}>Bobot</TH>
                  <TH style={{ width: '6%' }}>Skor</TH>
                </tr>
              </thead>
              <tbody>
                {[...Array(maxRuleRows)].map((_, i) => {
                  const r = triggered_rules[i];
                  const bobot = r?.bobot ?? '-';
                  return (
                    <tr key={i} style={{ height: 22, background: r ? '#fff7ed' : 'white' }}>
                      <TD style={{ textAlign: 'center' }}>{i + 1}</TD>
                      <TD style={{ textAlign: 'center', fontWeight: 700, color: '#0369a1', fontSize: 8 }}>{r?.rule_id || ''}</TD>
                      <TD style={{ fontSize: 8 }}>{r?.kelompok_rule || ''}</TD>
                      <TD style={{ fontSize: 8 }}>{r?.pesan_validasi || ''}</TD>
                      <TD style={{ textAlign: 'center', fontSize: 8 }}>
                        {r ? <><span style={{ color: '#dc2626' }}>☑ Terindikasi</span>  ☐ Tidak</> : <>☐ Terindikasi  ☐ Tidak</>}
                      </TD>
                      <TD style={{ textAlign: 'center', fontWeight: 700 }}>{bobot}</TD>
                      <TD style={{ textAlign: 'center', fontWeight: 700, color: r ? '#dc2626' : 'inherit' }}>{r ? bobot : ''}</TD>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div style={{ fontSize: 7.5, marginTop: 2, color: '#555' }}>
              Keterangan Bobot Rule: Combination Code=4, Includes/Excludes=3, Procedure=3, Underlying Cause=2, Unbundling/Omit=2, Administrative=1, Age/LOS=1
            </div>
          </div>
          {/* Ringkasan Skor */}
          <div style={{ width: 160, border: '1.5px solid #0e3c6c', borderRadius: 4, padding: 8, background: '#f0f9ff' }}>
            <div style={{ fontSize: 9, fontWeight: 700, color: '#0e3c6c', textAlign: 'center', marginBottom: 6 }}>RINGKASAN SKOR DAN RISIKO (OTOMATIS)</div>
            <div style={{ textAlign: 'center', marginBottom: 4 }}>
              <div style={{ fontSize: 8, color: '#555' }}>TOTAL SKOR</div>
              <div style={{ fontSize: 8, color: '#555' }}>(Σ Bobot Rule Terindikasi)</div>
              <div style={{ fontSize: 28, fontWeight: 900, color: totalSkor >= 8 ? '#ef4444' : totalSkor >= 4 ? '#f59e0b' : '#22c55e', lineHeight: 1.2, border: '2px solid #0e3c6c', borderRadius: 6, margin: '4px auto', width: 60, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {totalSkor}
              </div>
            </div>
            <div style={{ fontSize: 8, fontWeight: 700, color: '#0e3c6c', marginTop: 6, marginBottom: 2 }}>TINGKAT RISIKO</div>
            <div style={{ fontSize: 8 }}>(Otomatis)</div>
            <RiskGauge tingkat={tingkatRisiko} />
            <div style={{ marginTop: 8, fontSize: 8 }}>
              {[['Rendah', '(Skor 0–3)'], ['Sedang', '(Skor 4–7)'], ['Tinggi', '(Skor ≥ 8)']].map(([l, s]) => (
                <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 2 }}>
                  <span>{l === tingkatRisiko ? '☑' : '☐'}</span>
                  <span style={{ fontWeight: l === tingkatRisiko ? 700 : 400 }}>{l}</span>
                  <span style={{ color: '#888' }}>{s}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ════════════════════ SECTION 5: REKOMENDASI SISTEM ════════════════════ */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8 }}>
          <div>
            <div className="kkr-section-header">5. REKOMENDASI DAN KEPUTUSAN SISTEM</div>
            <div style={{ border: '1px solid #bcd', padding: 8, minHeight: 100, background: '#f8fafc' }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: '#0e3c6c', marginBottom: 6 }}>REKOMENDASI SISTEM (OTOMATIS)</div>
              {[
                ['Monitoring (Tidak perlu tindak lanjut)', isMonitor || totalSkor === 0],
                ['Audit Sampling (sampling)', isSampling],
                ['Direkomendasikan On-Site Audit', isOnSite],
              ].map(([label, checked]) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 9, marginBottom: 4, fontWeight: checked ? 700 : 400, color: checked ? '#0e3c6c' : '#555' }}>
                  <span style={{ fontSize: 12 }}>{checked ? '☑' : '☐'}</span> {label}
                </div>
              ))}
              <div style={{ marginTop: 8, fontSize: 9 }}>
                <span style={{ fontWeight: 700 }}>Alasan Rekomendasi Sistem:</span>
                <div style={{ fontSize: 8, color: '#555', marginTop: 2 }}>
                  {`Total Skor KNAVP: ${totalSkor} | Perbedaan Dual Coding: ${dual_coding?.jumlah_beda_total || 0}`}
                </div>
              </div>
            </div>
          </div>
          <div>
            <div style={{ border: '1px solid #bcd', padding: 8, marginTop: 23, minHeight: 100, background: '#f8fafc' }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: '#0e3c6c', marginBottom: 6 }}>PARAMETER REKOMENDASI SISTEM</div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 8 }}>
                <tbody>
                  {[
                    ['Total Skor', totalSkor],
                    ['Jumlah Rule Terindikasi', triggered_rules.length],
                    ['Jumlah Perbedaan Dual Coding', dual_coding?.jumlah_beda_total || 0],
                    ['Tingkat Risiko', tingkatRisiko],
                    ['Keputusan Sistem', knavp?.keputusan_sistem || '-'],
                  ].map(([label, val]) => (
                    <tr key={label}>
                      <td style={{ border: '1px solid #dde', padding: '2px 6px', fontWeight: 600 }}>{label}</td>
                      <td style={{ border: '1px solid #dde', padding: '2px 6px' }}>: {val}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* ════════════════════ SECTION 6 & 7 ════════════════════ */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8 }}>
          {/* Section 6: Catatan Sistem */}
          <div>
            <div className="kkr-section-header">6. CATATAN SISTEM</div>
            <div style={{ border: '1px solid #bcd', minHeight: 90 }}>
              <div style={{ fontSize: 8, color: '#555', padding: '4px 8px', background: '#f8fafc', borderBottom: '1px solid #bcd' }}>
                Catatan / Informasi Tambahan dari Sistem:
              </div>
              <textarea
                className="kkr-textarea"
                style={{ height: 70, fontSize: 8 }}
                value={formData.catatan_sistem}
                onChange={e => setFormData({ ...formData, catatan_sistem: e.target.value })}
                placeholder="Catatan otomatis atau tambahan reviewer..."
              />
            </div>
          </div>
          {/* Section 7: Validasi Reviewer */}
          <div>
            <div className="kkr-section-header">7. VALIDASI REVIEWER</div>
            <div style={{ border: '1px solid #bcd', padding: 8, minHeight: 90 }}>
              <div style={{ fontSize: 8, color: '#555', marginBottom: 6 }}>
                Dengan ini reviewer menyatakan bahwa hasil Desk Review (validasi otomatis) telah diperiksa dan sesuai dengan output sistem.
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 8, alignItems: 'start' }}>
                <div>
                  <div style={{ fontSize: 8, fontWeight: 700, marginBottom: 2 }}>Nama Reviewer</div>
                  <input type="text" className="kkr-input-line" value={formData.reviewer_name}
                    onChange={e => setFormData({ ...formData, reviewer_name: e.target.value })}
                    placeholder="Nama Reviewer" style={{ fontSize: 9 }} />
                  <div style={{ fontSize: 8, fontWeight: 700, marginTop: 4, marginBottom: 2 }}>NIP</div>
                  <input type="text" className="kkr-input-line" value={formData.nip_reviewer}
                    onChange={e => setFormData({ ...formData, nip_reviewer: e.target.value })}
                    placeholder="NIP" style={{ fontSize: 9 }} />
                  <div style={{ fontSize: 8, fontWeight: 700, marginTop: 4, marginBottom: 2 }}>Tanggal Validasi</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <input type="date" className="kkr-input-line" style={{ flex: 1, fontSize: 9 }}
                      value={formData.tanggal_review}
                      onChange={e => setFormData({ ...formData, tanggal_review: e.target.value })} />
                    <span style={{ fontSize: 8, color: '#555' }}>WIB</span>
                  </div>
                </div>
                {/* TTD Digital */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 8, fontWeight: 700, marginBottom: 4 }}>TTD DIGITAL REVIEWER</div>
                  <div style={{ width: 70, height: 50, border: '1px dashed #94a3b8', background: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto' }}>
                    <span style={{ fontSize: 6.5, color: '#94a3b8' }}>Scan / Digital<br/>Signature</span>
                  </div>
                </div>
                {/* QR Code */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 7, fontWeight: 700, marginBottom: 2 }}>QR CODE HASIL DESK REVIEW</div>
                  <div style={{ width: 60, height: 60, background: '#1e3a5f', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto', borderRadius: 4 }}>
                    <span style={{ fontSize: 6, color: 'white', textAlign: 'center' }}>QR<br/>Code</span>
                  </div>
                  <div style={{ fontSize: 6, color: '#888', marginTop: 2 }}>(Scan untuk melihat detail<br/>hasil validasi otomatis)</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ════════════════════ FOOTER KETERANGAN ════════════════════ */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 0, marginTop: 10, border: '1px solid #0e3c6c', borderRadius: 4, overflow: 'hidden' }}>
          {/* Keterangan Validasi */}
          <div style={{ padding: 6, borderRight: '1px solid #bcd' }}>
            <div style={{ fontSize: 8, fontWeight: 700, color: '#0e3c6c', marginBottom: 3 }}>KETERANGAN HASIL VALIDASI OTOMATIS</div>
            <div style={{ fontSize: 7 }}>
              <p style={{ margin: '2px 0' }}>Hasil pada dokumen ini dihasilkan otomatis oleh sistem berdasarkan aturan pengodean (KNAVP) dan data klaim tanpa telaah rekam medis.</p>
              <p style={{ margin: '2px 0' }}>Karena dengan rekomendasi "On-Site Audit" akan dilanjutkan ke tahap On-Site Audit (KKR-OS01).</p>
            </div>
          </div>
          {/* Tingkat Keyakinan Sistem */}
          <div style={{ padding: 6, borderRight: '1px solid #bcd' }}>
            <div style={{ fontSize: 8, fontWeight: 700, color: '#0e3c6c', marginBottom: 3 }}>TINGKAT KEYAKINAN SISTEM</div>
            {[
              ['#ef4444', 'Rendah', 'Indikasi sangat lemah / data sangat terbatas.'],
              ['#f59e0b', 'Sedang', 'Indikasi cukup kuat namun belum konklusif.'],
              ['#22c55e', 'Tinggi', 'Indikasi sangat kuat berdasarkan data klaim yang tersedia.'],
            ].map(([color, label, desc]) => (
              <div key={label} style={{ display: 'flex', alignItems: 'flex-start', gap: 4, marginBottom: 2 }}>
                <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: color, marginTop: 1, flexShrink: 0 }} />
                <span style={{ fontSize: 7 }}><strong>{label}</strong> : {desc}</span>
              </div>
            ))}
          </div>
          {/* Validasi Dokumen */}
          <div style={{ padding: 6 }}>
            <div style={{ fontSize: 8, fontWeight: 700, color: '#0e3c6c', marginBottom: 3 }}>VALIDASI DOKUMEN</div>
            <div style={{ fontSize: 7 }}>
              Scan QR Code di samping atau barcode di atas untuk validasi keaslian dokumen sistem melalui sistem.
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div style={{ marginTop: 8, padding: '4px 8px', background: '#f0f4f8', borderRadius: 4, fontSize: 7, color: '#555', border: '1px solid #e2e8f0' }}>
          🔒 Dokumen ini adalah hasil validasi otomatis sistem dan bukan merupakan hasil audit manual. Penetapan benar/salah pengodean dilakukan pada tahap On-Site Audit.
        </div>

      </div>
    </div>
  );
}
