import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ChevronLeft, Save, Printer, SquareActivity } from 'lucide-react';
import axios from 'axios';

export default function KKRForm() {
  const { sep } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    analisis_reviewer: '',
    keputusan: '',
    alasan_keputusan: '',
    catatan_tambahan: '',
    reviewer_name: '',
    tanggal_review: new Date().toISOString().split('T')[0],
    ketua_tim_name: ''
  });

  useEffect(() => {
    axios.get(`/api/validate/${encodeURIComponent(sep)}`)
      .then(res => {
        setData(res.data.data);
        setLoading(false);
        axios.get(`/api/kkr-dr01/load/${encodeURIComponent(sep)}`)
          .then(res_load => {
            if (res_load.data.data && res_load.data.data.form_data) {
              const fd = res_load.data.data.form_data;
              setFormData(f => ({
                ...f,
                analisis_reviewer: fd.analisis_reviewer || '',
                keputusan: fd.keputusan || '',
                alasan_keputusan: fd.alasan_keputusan || '',
                catatan_tambahan: fd.catatan_tambahan || '',
                reviewer_name: fd.reviewer_name || '',
                tanggal_review: fd.tanggal_review || f.tanggal_review,
                ketua_tim_name: fd.ketua_tim_name || ''
              }));
            }
          });
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [sep]);

  const handleSave = () => {
    setSaving(true);
    const payload = {
      kode_rs: data.case.kode_rs,
      sep: sep,
      triggered_rules: data.triggered_rules,
      ...formData
    };
    
    axios.post('/api/kkr-dr01/save', payload)
      .then(res => {
        alert('KKR Berhasil Disimpan!');
        setSaving(false);
      })
      .catch(err => {
        alert('Gagal menyimpan');
        setSaving(false);
      });
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) return <div className="fade-in"><div className="spinner" style={{margin:'auto', width:40,height:40,border:'4px solid var(--kmk-cyan)',borderTopColor:'transparent',borderRadius:'50%'}}></div></div>;
  if (!data) return <div>Gagal memuat formulir.</div>;

  const diags = data.case.diaglist ? data.case.diaglist.split(';') : [];
  const procs = data.case.proclist ? data.case.proclist.split(';') : [];
  
  // Extract severity level from INA-CBG code if possible (usually last char like I, II, III)
  const inacbgParts = data.case.inacbg ? data.case.inacbg.split('-') : [];
  const severityLevel = inacbgParts.length > 0 ? inacbgParts[inacbgParts.length - 1] : '-';

  return (
    <div className="fade-in" style={{ padding: '20px 0' }}>
      {/* Top Action Bar */}
      <div className="no-print" style={{ maxWidth: 1000, margin: '0 auto 16px auto', display: 'flex', justifyContent: 'space-between' }}>
        <button onClick={() => window.history.back()} className="btn btn-outline" style={{ border: 'none', padding: 0 }}>
          <ChevronLeft size={16} /> Kembali
        </button>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-outline" onClick={handlePrint}>
            <Printer size={16} /> Cetak / PDF
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            <Save size={16} /> {saving ? 'Menyimpan...' : 'Simpan KKR'}
          </button>
        </div>
      </div>

      {/* Official A4 Page Container */}
      <div className="kkr-page" style={{ maxWidth: 1000, margin: '0 auto', background: 'white', padding: 30, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        
        {/* HEADER */}
        <div className="kkr-header-container">
          <div className="kkr-logo-box">
             <div style={{ display:'flex', alignItems:'center', gap: 8 }}>
               <SquareActivity size={32} color="#0e3c6c" />
               <div style={{ fontSize: 11, fontWeight: 700, color: '#0e3c6c', lineHeight: 1.2 }}>
                 KEMENTERIAN KESEHATAN<br/>REPUBLIK INDONESIA
               </div>
             </div>
          </div>
          <div className="kkr-title-box">
             <h2 style={{ fontSize: 18, margin: 0, color: '#0e3c6c' }}>KERTAS KERJA REVIEWER &ndash; DESK REVIEW</h2>
             <h3 style={{ fontSize: 16, margin: '4px 0', color: '#00838f' }}>(KKR-DR01)</h3>
             <h4 style={{ fontSize: 12, margin: '8px 0 2px 0', color: '#0e3c6c' }}>AUDIT CODING DAN VERIFIKASI DUAL CODING</h4>
             <div style={{ fontSize: 11 }}>Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)</div>
          </div>
          <div className="kkr-doc-info">
             <table className="kkr-doc-table">
               <tbody>
                 <tr><td width="55%">KODE DOKUMEN</td><td>: KKR-DR01</td></tr>
                 <tr><td>VERSI</td><td>: 1.0</td></tr>
                 <tr><td>TANGGAL BERLAKU</td><td>: ____/____/________</td></tr>
                 <tr><td>HALAMAN</td><td>: 1 dari 1</td></tr>
               </tbody>
             </table>
          </div>
        </div>

        {/* SECTION 1 & 2 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 16 }}>
          
          {/* SECTION 1 */}
          <div>
             <div className="kkr-section-header">1. IDENTITAS KLAIM (DATA KLAIM DATA CENTER)</div>
             <table className="kkr-data-table kkr-full-border">
               <tbody>
                 <tr><td width="35%" className="kkr-fw-bold">Nomor Klaim</td><td>: ....................................................</td></tr>
                 <tr><td className="kkr-fw-bold">Nomor SEP</td><td>: <span style={{fontFamily:'monospace'}}>{data.case.sep}</span></td></tr>
                 <tr><td className="kkr-fw-bold">Nomor Peserta</td><td>: ....................................................</td></tr>
                 <tr><td className="kkr-fw-bold">Nama Peserta</td><td>: ....................................................</td></tr>
                 <tr><td className="kkr-fw-bold">Tanggal Lahir / Umur</td><td>: ...... / ...... / ............ / ........... tahun</td></tr>
                 <tr><td className="kkr-fw-bold">Jenis Kelamin</td><td>: [ &nbsp; ] L &nbsp;&nbsp;&nbsp; [ &nbsp; ] P</td></tr>
                 <tr><td className="kkr-fw-bold">Tanggal Pelayanan</td><td>: {data.case.discharge_date}</td></tr>
                 <tr><td className="kkr-fw-bold">Jenis Pelayanan</td><td>: {data.case.rw ? '[ X ] Rawat Inap' : '[   ] Rawat Inap'} &nbsp; {data.case.rw ? '[   ] Rawat Jalan' : '[ X ] Rawat Jalan'}</td></tr>
                 <tr><td className="kkr-fw-bold">Fasilitas Kesehatan</td><td>: {data.case.nama_rs}</td></tr>
                 <tr><td className="kkr-fw-bold">Kode FPKTL</td><td>: {data.case.kode_rs}</td></tr>
                 <tr><td className="kkr-fw-bold">Kelas Rawat</td><td>: {data.case.kelas_rawat || '-'}</td></tr>
                 <tr><td className="kkr-fw-bold">Length of Stay (LOS)</td><td>: {data.case.alos || '-'} hari</td></tr>
                 <tr><td className="kkr-fw-bold">DPJP</td><td>: ....................................................</td></tr>
               </tbody>
             </table>
          </div>

          {/* SECTION 2 */}
          <div>
             <div className="kkr-section-header">2. INFORMASI GROUPING DAN TARIF</div>
             <table className="kkr-data-table kkr-full-border" style={{ borderBottom: 'none' }}>
               <thead>
                 <tr>
                   <th width="50%" className="kkr-th-blue">INA-CBG</th>
                   <th width="50%" className="kkr-th-blue">iDRG</th>
                 </tr>
               </thead>
               <tbody>
                 <tr>
                   <td style={{ padding: 0, verticalAlign: 'top' }}>
                     <table className="kkr-inner-table">
                       <tbody>
                         <tr><td width="40%" className="kkr-fw-bold">Kode INA-CBG</td><td>: {data.case.inacbg}</td></tr>
                         <tr><td className="kkr-fw-bold">Deskripsi INA-CBG</td><td>: <span style={{fontSize:9}}>{data.case.deskripsi_inacbg}</span></td></tr>
                         <tr><td className="kkr-fw-bold">Severity Level</td><td>: {severityLevel}</td></tr>
                       </tbody>
                     </table>
                   </td>
                   <td style={{ padding: 0, verticalAlign: 'top', borderLeft: '1px solid #0e3c6c' }}>
                     <table className="kkr-inner-table">
                       <tbody>
                         <tr><td width="40%" className="kkr-fw-bold">Kode iDRG</td><td>: {data.case.idrg_code || '-'}</td></tr>
                         <tr><td className="kkr-fw-bold">Deskripsi iDRG</td><td>: <span style={{fontSize:9}}>{data.case.deskripsi_idrg || '-'}</span></td></tr>
                         <tr><td className="kkr-fw-bold">Complexity Level</td><td>: -</td></tr>
                       </tbody>
                     </table>
                   </td>
                 </tr>
               </tbody>
             </table>
             <table className="kkr-data-table kkr-full-border" style={{ borderTop: 'none' }}>
               <thead>
                 <tr>
                   <th width="50%" className="kkr-th-light">KOMPONEN TARIF</th>
                   <th width="50%" className="kkr-th-light">NILAI (Rp)</th>
                 </tr>
               </thead>
               <tbody>
                 <tr><td className="kkr-fw-bold">Tarif Klaim (INA-CBG)</td><td>Rp {data.case.tarif_inacbg?.toLocaleString('id-ID')}</td></tr>
                 <tr><td className="kkr-fw-bold">Tarif RS (Standar)</td><td>Rp {data.case.tarif_rs?.toLocaleString('id-ID')}</td></tr>
                 <tr><td className="kkr-fw-bold">Selisih</td><td>Rp {(data.case.tarif_inacbg - data.case.tarif_rs)?.toLocaleString('id-ID')}</td></tr>
               </tbody>
             </table>
          </div>
        </div>

        {/* SECTION 3 */}
        <div className="kkr-section-header" style={{ marginTop: 12 }}>3. INPUT DATA KLAIM (BERDASARKAN DATA KLAIM DATA CENTER)</div>
        <table className="kkr-data-table kkr-full-border kkr-grid-table">
          <thead>
            <tr>
              <th rowSpan="2" width="4%" className="kkr-th-light">No.</th>
              <th colSpan="2" width="48%" className="kkr-th-light">DIAGNOSA</th>
              <th colSpan="2" width="48%" className="kkr-th-light">PROSEDUR</th>
            </tr>
            <tr>
              <th className="kkr-th-light" width="15%">INA-CBG / iDRG<br/>Kode ICD</th>
              <th className="kkr-th-light">Deskripsi</th>
              <th className="kkr-th-light" width="15%">INA-CBG / iDRG<br/>Kode ICD-9-CM</th>
              <th className="kkr-th-light">Deskripsi</th>
            </tr>
          </thead>
          <tbody>
            {[...Array(10)].map((_, i) => (
              <tr key={`diagproc-${i}`}>
                <td style={{ textAlign: 'center' }}>{i + 1}</td>
                <td style={{ textAlign: 'center', fontFamily: 'monospace' }}>{diags[i] || ''}</td>
                <td style={{ fontSize: 9 }}>-</td>
                <td style={{ textAlign: 'center', fontFamily: 'monospace' }}>{procs[i] || ''}</td>
                <td style={{ fontSize: 9 }}>-</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ fontSize: 9, marginTop: 2 }}>Catatan: Isi sesuai urutan yang tercantum pada data klaim. (Deskripsi individual ICD belum ditarik pada sampel dataset ini)</div>

        {/* SECTION 4 */}
        <div className="kkr-section-header" style={{ marginTop: 12 }}>4. RINGKASAN TEMUAN (HASIL VALIDASI OTOMATIS BERDASARKAN RULE)</div>
        <table className="kkr-data-table kkr-full-border kkr-grid-table">
          <thead>
            <tr>
              <th width="4%" className="kkr-th-light">No.</th>
              <th width="10%" className="kkr-th-light">Rule ID</th>
              <th width="40%" className="kkr-th-light">Nama Rule</th>
              <th width="13%" className="kkr-th-light">Hasil Validasi<br/>(Otomatis)</th>
              <th width="13%" className="kkr-th-light">Tingkat Keyakinan<br/>Reviewer</th>
              <th width="20%" className="kkr-th-light">Potensi Dampak</th>
            </tr>
          </thead>
          <tbody>
            {data.triggered_rules.length === 0 ? (
              <tr><td colSpan="6" style={{ textAlign: 'center', padding: '12px' }}>Tidak ditemukan indikasi pelanggaran aturan pengodean.</td></tr>
            ) : (
              [...Array(maxRows(data.triggered_rules.length, 5))].map((_, i) => {
                const r = data.triggered_rules[i];
                return (
                  <tr key={`rule-${i}`} style={{ height: 24 }}>
                    <td style={{ textAlign: 'center' }}>{i + 1}</td>
                    <td style={{ textAlign: 'center' }}>{r?.rule_id || ''}</td>
                    <td style={{ fontSize: 10 }}>{r?.nama_aturan || ''}</td>
                    <td style={{ textAlign: 'center' }}>{r ? 'Terindikasi' : ''}</td>
                    <td style={{ textAlign: 'center' }}>{r?.severity || ''}</td>
                    <td style={{ fontSize: 10, textAlign:'center' }}>{r ? 'Grouping/Tarif' : ''}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
        <div style={{ fontSize: 9, marginTop: 2 }}>Catatan: Ringkasan temuan dihasilkan otomatis oleh sistem berdasarkan aturan pengodean.</div>

        {/* SECTION 5 & 6 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
          <div>
            <div className="kkr-section-header">5. ANALISIS REVIEWER</div>
            <div className="kkr-box-border" style={{ height: 180, display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: 10, marginBottom: 4 }}>Uraian analisis berdasarkan ringkasan temuan:</div>
              <textarea 
                className="kkr-textarea"
                value={formData.analisis_reviewer}
                onChange={e => setFormData({...formData, analisis_reviewer: e.target.value})}
              />
            </div>
          </div>
          <div>
            <div className="kkr-section-header">6. KEPUTUSAN REVIEWER</div>
            <div className="kkr-box-border" style={{ height: 180, display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: 10, marginBottom: 6 }}>Berdasarkan hasil validasi dan analisis di atas, kasus ini:</div>
              {['Tidak diperlukan tindak lanjut', 'Perlu Monitoring', 'Direkomendasikan On-Site Audit', 'Data tidak cukup untuk dinilai'].map(opt => (
                <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 10, marginBottom: 4, cursor: 'pointer' }}>
                  <input 
                    type="checkbox" 
                    checked={formData.keputusan === opt} 
                    onChange={() => setFormData({...formData, keputusan: opt})} 
                    style={{ margin: 0 }}
                  />
                  {opt}
                </label>
              ))}
              <div style={{ fontSize: 10, marginTop: 12, marginBottom: 4 }}>Alasan / Catatan Singkat:</div>
              <textarea 
                className="kkr-textarea"
                style={{ flex: 1 }}
                value={formData.alasan_keputusan}
                onChange={e => setFormData({...formData, alasan_keputusan: e.target.value})}
              />
            </div>
          </div>
        </div>

        {/* SECTION 7 & 8 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
          <div>
            <div className="kkr-section-header">7. CATATAN TAMBAHAN REVIEWER</div>
            <div className="kkr-box-border" style={{ height: 120 }}>
              <textarea 
                className="kkr-textarea"
                value={formData.catatan_tambahan}
                onChange={e => setFormData({...formData, catatan_tambahan: e.target.value})}
              />
            </div>
          </div>
          <div>
            <div className="kkr-section-header">8. PARAF REVIEWER</div>
            <div className="kkr-box-border" style={{ height: 120, display: 'flex', justifyContent: 'space-between', padding: '12px 24px' }}>
              <div style={{ width: '45%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: 10, fontWeight: 700 }}>Reviewer,</div>
                <div style={{ width: '100%' }}>
                  <input type="text" className="kkr-input-line" placeholder="(..........................................)" value={formData.reviewer_name} onChange={e => setFormData({...formData, reviewer_name: e.target.value})} style={{ textAlign: 'center' }} />
                </div>
                <div style={{ fontSize: 10, display: 'flex', width: '100%', alignItems: 'center' }}>
                  Tanggal: <input type="date" className="kkr-input-line" style={{ flex: 1, marginLeft: 4 }} value={formData.tanggal_review} onChange={e => setFormData({...formData, tanggal_review: e.target.value})} />
                </div>
              </div>
              <div style={{ width: '45%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: 10, fontWeight: 700 }}>Ketua Tim Reviewer,</div>
                <div style={{ width: '100%' }}>
                  <input type="text" className="kkr-input-line" placeholder="(..........................................)" value={formData.ketua_tim_name} onChange={e => setFormData({...formData, ketua_tim_name: e.target.value})} style={{ textAlign: 'center' }} />
                </div>
                <div style={{ fontSize: 10, display: 'flex', width: '100%' }}>
                  Tanggal: <span style={{ flex: 1, borderBottom: '1px dotted #888', marginLeft: 4 }}>&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FOOTER PANDUAN */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginTop: 16, border: '1px solid #0e3c6c', borderRadius: 4, padding: 8 }}>
          <div>
             <div style={{ fontSize: 9, fontWeight: 700, color: '#0e3c6c', marginBottom: 4 }}>KETERANGAN HASIL VALIDASI (OTOMATIS)</div>
             <table style={{ fontSize: 8 }}>
               <tbody>
                 <tr><td width="30%" className="kkr-fw-bold" style={{verticalAlign:'top'}}>Sesuai Rule</td><td style={{verticalAlign:'top'}}>: Tidak ditemukan indikasi pelanggaran aturan pengodean.</td></tr>
                 <tr><td className="kkr-fw-bold" style={{verticalAlign:'top'}}>Terindikasi</td><td style={{verticalAlign:'top'}}>: Ditemukan indikasi ketidaksesuaian terhadap aturan pengodean.</td></tr>
                 <tr><td className="kkr-fw-bold" style={{verticalAlign:'top'}}>Tidak Dapat Dinilai</td><td style={{verticalAlign:'top'}}>: Rule tidak dapat diterapkan pada kasus ini berdasarkan data klaim.</td></tr>
               </tbody>
             </table>
          </div>
          <div>
             <div style={{ fontSize: 9, fontWeight: 700, color: '#0e3c6c', marginBottom: 4 }}>TINGKAT KEYAKINAN REVIEWER</div>
             <table style={{ fontSize: 8 }}>
               <tbody>
                 <tr><td width="25%" className="kkr-fw-bold" style={{verticalAlign:'top'}}>Rendah</td><td style={{verticalAlign:'top'}}>: Indikasi masih sangat lemah / data sangat terbatas.</td></tr>
                 <tr><td className="kkr-fw-bold" style={{verticalAlign:'top'}}>Sedang</td><td style={{verticalAlign:'top'}}>: Indikasi cukup kuat namun belum konklusif.</td></tr>
                 <tr><td className="kkr-fw-bold" style={{verticalAlign:'top'}}>Tinggi</td><td style={{verticalAlign:'top'}}>: Indikasi sangat kuat berdasarkan data klaim yang tersedia.</td></tr>
               </tbody>
             </table>
          </div>
          <div>
             <div style={{ fontSize: 9, fontWeight: 700, color: '#0e3c6c', marginBottom: 4 }}>CATATAN PENTING</div>
             <ol style={{ fontSize: 8, margin: 0, paddingLeft: 12 }}>
               <li>Formulir ini digunakan untuk <strong>Desk Review</strong> berdasarkan data klaim pada <strong>Data Center</strong>.</li>
               <li>Penilaian ini bukan penetapan benar/salah pengodean.</li>
               <li>Verifikasi definitif dilakukan pada <strong>On-Site Audit</strong>.</li>
             </ol>
          </div>
        </div>

      </div>
    </div>
  );
}

function maxRows(actualLen, minLen) {
  return Math.max(actualLen, minLen);
}
