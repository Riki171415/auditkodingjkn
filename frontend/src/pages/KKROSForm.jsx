import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ChevronLeft, Save, Printer, SquareActivity } from 'lucide-react';
import axios from 'axios';

export default function KKROSForm() {
  const { sep } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    review_dokumen: {},
    diagnosa: {
      utama: { klaim_kode: '', klaim_desc: '', rev_kode: '', rev_desc: '', sesuai: '', catatan: '' },
      sekunder: Array(5).fill({ klaim_kode: '', klaim_desc: '', rev_kode: '', rev_desc: '', sesuai: '', catatan: '' })
    },
    prosedur: Array(5).fill({ klaim_kode: '', klaim_desc: '', rev_kode: '', rev_desc: '', sesuai: '', catatan: '' }),
    verifikasi_dual: {
      principal_diagnosis: { ina: '', idrg: '', konsisten: '', catatan: '' },
      secondary_diagnosis: { ina: '', idrg: '', konsisten: '', catatan: '' },
      prosedur: { ina: '', idrg: '', konsisten: '', catatan: '' },
      grouping: { ina: '', idrg: '', konsisten: '', catatan: '' },
      severity: { ina: '', idrg: '', konsisten: '', catatan: '' },
      tarif: { ina: '', idrg: '', konsisten: '', catatan: '' }
    },
    ringkasan_temuan: Array(5).fill({ jenis: '', deskripsi: '', kategori: '', dampak: '' }),
    analisis_reviewer: '',
    penyebab_utama: {},
    rekomendasi: {},
    catatan_tambahan: '',
    kesimpulan: '',
    penjelasan_singkat: '',
    reviewer_name: '',
    tanggal_review: new Date().toISOString().split('T')[0],
    ketua_tim_name: '',
    perwakilan_rs_name: ''
  });

  useEffect(() => {
    axios.get(`/api/validate/${encodeURIComponent(sep)}`)
      .then(res => {
        const cData = res.data.data;
        setData(cData);
        
        axios.get(`/api/kkr-os01/load/${encodeURIComponent(sep)}`)
          .then(res_load => {
            if (res_load.data.data && res_load.data.data.form_data && Object.keys(res_load.data.data.form_data).length > 0) {
              setFormData(f => ({ ...f, ...res_load.data.data.form_data }));
            } else {
              // Pre-fill diagnoses and procedures from claim if empty (User requested automation)
              const diags = cData.case.diaglist ? cData.case.diaglist.split(';') : [];
              const procs = cData.case.proclist ? cData.case.proclist.split(';') : [];
              
              const utamaKode = diags[0] || '';
              const utamaDesc = utamaKode ? (cData.case.icd_desc_map?.[utamaKode] || '-') : '';
              
              const sekunderInit = Array(5).fill({ klaim_kode: '', klaim_desc: '', rev_kode: '', rev_desc: '', sesuai: '', catatan: '' }).map((_, i) => {
                const kode = diags[i+1] || '';
                const desc = kode ? (cData.case.icd_desc_map?.[kode] || '-') : '';
                return { klaim_kode: kode, klaim_desc: desc, rev_kode: kode, rev_desc: desc, sesuai: '', catatan: '' }; // Pre-fill rev == klaim
              });
              
              const procInit = Array(5).fill({ klaim_kode: '', klaim_desc: '', rev_kode: '', rev_desc: '', sesuai: '', catatan: '' }).map((_, i) => {
                const kode = procs[i] || '';
                const desc = kode ? (cData.case.icd_desc_map?.[kode] || '-') : '';
                return { klaim_kode: kode, klaim_desc: desc, rev_kode: kode, rev_desc: desc, sesuai: '', catatan: '' };
              });
              
              setFormData(f => ({
                ...f,
                diagnosa: {
                  utama: { klaim_kode: utamaKode, klaim_desc: utamaDesc, rev_kode: utamaKode, rev_desc: utamaDesc, sesuai: '', catatan: '' },
                  sekunder: sekunderInit
                },
                prosedur: procInit
              }));
            }
            setLoading(false);
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
      form_data: formData
    };
    
    axios.post('/api/kkr-os01/save', payload)
      .then(res => {
        alert('KKR On-Site Berhasil Disimpan!');
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
  
  // Helpers to update nested state
  const updateNested = (category, field, value) => {
    setFormData(f => ({ ...f, [category]: { ...f[category], [field]: value } }));
  };
  const updateArray = (category, index, field, value) => {
    setFormData(f => {
      const arr = [...f[category]];
      arr[index] = { ...arr[index], [field]: value };
      return { ...f, [category]: arr };
    });
  };
  const updateDiagSekunder = (index, field, value) => {
    setFormData(f => {
      const sekunder = [...f.diagnosa.sekunder];
      sekunder[index] = { ...sekunder[index], [field]: value };
      return { ...f, diagnosa: { ...f.diagnosa, sekunder } };
    });
  };

  if (loading) return <div className="fade-in"><div className="spinner" style={{margin:'auto', width:40,height:40,border:'4px solid var(--kmk-cyan)',borderTopColor:'transparent',borderRadius:'50%'}}></div></div>;
  if (!data) return <div>Gagal memuat formulir.</div>;

  const severityLevel = data.case.inacbg ? data.case.inacbg.split('-').pop() : '-';

  return (
    <div className="fade-in" style={{ padding: '20px 0' }}>
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

      <div className="kkr-page" style={{ maxWidth: 1000, margin: '0 auto', background: 'white', padding: 24, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        
        {/* HEADER */}
        <div className="kkr-header-container">
          <div className="kkr-logo-box">
             <div style={{ display:'flex', alignItems:'center', gap: 8 }}>
               <SquareActivity size={32} color="#00838f" />
               <div style={{ fontSize: 11, fontWeight: 700, color: '#0e3c6c', lineHeight: 1.2 }}>
                 KEMENTERIAN KESEHATAN<br/>REPUBLIK INDONESIA
               </div>
             </div>
          </div>
          <div className="kkr-title-box">
             <h2 style={{ fontSize: 18, margin: 0, color: '#0e3c6c' }}>KERTAS KERJA REVIEWER &ndash; ON SITE AUDIT</h2>
             <h3 style={{ fontSize: 16, margin: '4px 0', color: '#00838f' }}>(KKR-OS01)</h3>
             <h4 style={{ fontSize: 11, margin: '8px 0 2px 0', color: '#0e3c6c' }}>AUDIT CODING DAN VERIFIKASI DUAL CODING</h4>
             <div style={{ fontSize: 10 }}>Transisi INA-CBG menuju Indonesian Diagnosis Related Groups (iDRG)</div>
          </div>
          <div className="kkr-doc-info">
             <table className="kkr-doc-table">
               <tbody>
                 <tr><td width="55%">KODE DOKUMEN</td><td>: KKR-OS01</td></tr>
                 <tr><td>VERSI</td><td>: 1.0</td></tr>
                 <tr><td>TANGGAL BERLAKU</td><td>: ____/____/________</td></tr>
                 <tr><td>HALAMAN</td><td>: 1 dari 1</td></tr>
               </tbody>
             </table>
          </div>
        </div>

        {/* SECTION 1 & 2 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
          <div>
             <div className="kkr-section-header" style={{backgroundColor: '#00695c'}}>1. IDENTITAS KLAIM</div>
             <table className="kkr-data-table kkr-full-border">
               <tbody>
                 <tr><td width="35%" className="kkr-fw-bold">Nomor Klaim</td><td>: ....................................................</td></tr>
                 <tr><td className="kkr-fw-bold">Nomor SEP</td><td>: <span style={{fontFamily:'monospace'}}>{data.case.sep}</span></td></tr>
                 <tr><td className="kkr-fw-bold">Nomor Peserta</td><td>: ....................................................</td></tr>
                 <tr><td className="kkr-fw-bold">Nama Peserta</td><td>: ....................................................</td></tr>
                 <tr><td className="kkr-fw-bold">Tgl Lahir / Umur</td><td>: ...... / ...... / ............ / ........... tahun</td></tr>
                 <tr><td className="kkr-fw-bold">Jenis Kelamin</td><td>: [ &nbsp; ] L &nbsp;&nbsp;&nbsp; [ &nbsp; ] P</td></tr>
                 <tr><td className="kkr-fw-bold">Tanggal Pelayanan</td><td>: {data.case.discharge_date}</td></tr>
                 <tr><td className="kkr-fw-bold">Jenis Pelayanan</td><td>: {data.case.rw ? '[ X ] Rawat Inap' : '[   ] Rawat Inap'} &nbsp; {data.case.rw ? '[   ] Rawat Jalan' : '[ X ] Rawat Jalan'}</td></tr>
                 <tr><td className="kkr-fw-bold">Fasilitas Kesehatan</td><td>: {data.case.nama_rs}</td></tr>
                 <tr><td className="kkr-fw-bold">Kode FPKTL</td><td>: {data.case.kode_rs}</td></tr>
                 <tr><td className="kkr-fw-bold">Kelas Rawat</td><td>: {data.case.kelas_rawat || '-'}</td></tr>
                 <tr><td className="kkr-fw-bold">Length of Stay (LOS)</td><td>: {data.case.alos || '-'} hari</td></tr>
                 <tr><td className="kkr-fw-bold">DPJP (Data Klaim)</td><td>: ....................................................</td></tr>
               </tbody>
             </table>
          </div>
          <div>
             <div className="kkr-section-header" style={{backgroundColor: '#00695c'}}>2. INFORMASI GROUPING DAN TARIF</div>
             <table className="kkr-data-table kkr-full-border" style={{ borderBottom: 'none' }}>
               <thead>
                 <tr>
                   <th width="50%" className="kkr-th-green">INA-CBG</th>
                   <th width="50%" className="kkr-th-green">iDRG</th>
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
                   <td style={{ padding: 0, verticalAlign: 'top', borderLeft: '1px solid #ccc' }}>
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
                   <th width="50%" className="kkr-th-light-green">KOMPONEN TARIF</th>
                   <th width="50%" className="kkr-th-light-green">NILAI (Rp)</th>
                 </tr>
               </thead>
               <tbody>
                 <tr><td className="kkr-fw-bold">Tarif Klaim (INA-CBG)</td><td>Rp {data.case.tarif_inacbg?.toLocaleString('id-ID')}</td></tr>
                 <tr><td className="kkr-fw-bold">Tarif RS (Tarif Standar)</td><td>Rp {data.case.tarif_rs?.toLocaleString('id-ID')}</td></tr>
                 <tr><td className="kkr-fw-bold">Selisih (Klaim - RS)</td><td>Rp {(data.case.tarif_inacbg - data.case.tarif_rs)?.toLocaleString('id-ID')}</td></tr>
               </tbody>
             </table>
          </div>
        </div>

        {/* SECTION 3 */}
        <div className="kkr-section-header" style={{backgroundColor: '#00695c', marginTop: 12}}>3. REVIEW DOKUMEN KLINIS (BUKTI YANG DITELAAH)</div>
        <div className="kkr-box-border" style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr 1fr', gap:8, fontSize:10}}>
          {['Resume Medis', 'CPPT / Catatan Perkembangan', 'Laporan Operasi / Tindakan', 'Hasil Laboratorium', 'Hasil Radiologi', 'Dokumen Penunjang Lain', 'Surat Eligibilitas Peserta (SEP)'].map(doc => (
            <label key={doc} style={{display:'flex', alignItems:'center', gap:4, cursor:'pointer'}}>
              <input type="checkbox" checked={formData.review_dokumen[doc] || false} onChange={e => updateNested('review_dokumen', doc, e.target.checked)} /> {doc}
            </label>
          ))}
          <label style={{display:'flex', alignItems:'center', gap:4}}>
            <input type="checkbox" checked={formData.review_dokumen['Lainnya'] || false} onChange={e => updateNested('review_dokumen', 'Lainnya', e.target.checked)} /> Lainnya:
            <input type="text" className="kkr-input-line" style={{flex:1}} value={formData.review_dokumen['lainnya_text'] || ''} onChange={e => updateNested('review_dokumen', 'lainnya_text', e.target.value)} />
          </label>
        </div>

        {/* SECTION 4 */}
        <div className="kkr-section-header" style={{backgroundColor: '#00695c', marginTop: 12}}>4. REVIEW DIAGNOSA (BERDASARKAN DOKUMENTASI KLINIS)</div>
        <table className="kkr-data-table kkr-full-border kkr-grid-table">
          <thead>
            <tr>
              <th rowSpan="2" width="3%" className="kkr-th-light-green">No.</th>
              <th colSpan="2" width="33%" className="kkr-th-light-green">DIAGNOSA KLAIM (DATA KLAIM)</th>
              <th colSpan="2" width="33%" className="kkr-th-light-green">DIAGNOSA REVIEWER (BERDASARKAN RM)</th>
              <th colSpan="2" width="8%" className="kkr-th-light-green">SESUAI?</th>
              <th rowSpan="2" width="23%" className="kkr-th-light-green">CATATAN / ALASAN KETIDAKSESUAIAN</th>
            </tr>
            <tr>
              <th className="kkr-th-light-green">Kode ICD</th>
              <th className="kkr-th-light-green">Deskripsi</th>
              <th className="kkr-th-light-green">Kode ICD</th>
              <th className="kkr-th-light-green">Deskripsi</th>
              <th className="kkr-th-light-green">Ya</th>
              <th className="kkr-th-light-green">Tidak</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colSpan="8" style={{fontSize:9, fontWeight:'bold', background:'#eee', padding:'2px 4px'}}>A. Diagnosis Utama (Principal Diagnosis)</td></tr>
            <tr>
              <td style={{textAlign:'center'}}>1</td>
              <td style={{textAlign:'center'}}>{formData.diagnosa.utama.klaim_kode}</td>
              <td style={{fontSize:9}}>{formData.diagnosa.utama.klaim_desc}</td>
              <td><input className="kkr-input-line" style={{textAlign:'center'}} value={formData.diagnosa.utama.rev_kode} onChange={e => updateNested('diagnosa', 'utama', {...formData.diagnosa.utama, rev_kode: e.target.value})} /></td>
              <td><input className="kkr-input-line" style={{fontSize:9}} value={formData.diagnosa.utama.rev_desc} onChange={e => updateNested('diagnosa', 'utama', {...formData.diagnosa.utama, rev_desc: e.target.value})} /></td>
              <td style={{textAlign:'center'}}><input type="radio" checked={formData.diagnosa.utama.sesuai === 'Y'} onChange={() => updateNested('diagnosa', 'utama', {...formData.diagnosa.utama, sesuai: 'Y'})}/></td>
              <td style={{textAlign:'center'}}><input type="radio" checked={formData.diagnosa.utama.sesuai === 'N'} onChange={() => updateNested('diagnosa', 'utama', {...formData.diagnosa.utama, sesuai: 'N'})}/></td>
              <td><input className="kkr-input-line" value={formData.diagnosa.utama.catatan} onChange={e => updateNested('diagnosa', 'utama', {...formData.diagnosa.utama, catatan: e.target.value})} /></td>
            </tr>
            <tr><td colSpan="8" style={{fontSize:9, fontWeight:'bold', background:'#eee', padding:'2px 4px'}}>B. Diagnosis Sekunder (Secondary Diagnosis)</td></tr>
            {formData.diagnosa.sekunder.map((row, i) => (
              <tr key={`sec-${i}`}>
                <td style={{textAlign:'center'}}>{i+1}</td>
                <td style={{textAlign:'center'}}>{row.klaim_kode}</td>
                <td style={{fontSize:9}}>{row.klaim_desc}</td>
                <td><input className="kkr-input-line" style={{textAlign:'center'}} value={row.rev_kode} onChange={e => updateDiagSekunder(i, 'rev_kode', e.target.value)} /></td>
                <td><input className="kkr-input-line" style={{fontSize:9}} value={row.rev_desc} onChange={e => updateDiagSekunder(i, 'rev_desc', e.target.value)} /></td>
                <td style={{textAlign:'center'}}><input type="radio" checked={row.sesuai === 'Y'} onChange={() => updateDiagSekunder(i, 'sesuai', 'Y')}/></td>
                <td style={{textAlign:'center'}}><input type="radio" checked={row.sesuai === 'N'} onChange={() => updateDiagSekunder(i, 'sesuai', 'N')}/></td>
                <td><input className="kkr-input-line" value={row.catatan} onChange={e => updateDiagSekunder(i, 'catatan', e.target.value)} /></td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* SECTION 5 */}
        <div className="kkr-section-header" style={{backgroundColor: '#00695c', marginTop: 12}}>5. REVIEW PROSEDUR / TINDAKAN (BERDASARKAN DOKUMENTASI KLINIS)</div>
        <table className="kkr-data-table kkr-full-border kkr-grid-table">
          <thead>
            <tr>
              <th rowSpan="2" width="3%" className="kkr-th-light-green">No.</th>
              <th colSpan="2" width="33%" className="kkr-th-light-green">PROSEDUR KLAIM (DATA KLAIM)</th>
              <th colSpan="2" width="33%" className="kkr-th-light-green">PROSEDUR REVIEWER (BERDASARKAN RM)</th>
              <th colSpan="2" width="8%" className="kkr-th-light-green">SESUAI?</th>
              <th rowSpan="2" width="23%" className="kkr-th-light-green">CATATAN / ALASAN KETIDAKSESUAIAN</th>
            </tr>
            <tr>
              <th className="kkr-th-light-green">Kode ICD-9-CM</th>
              <th className="kkr-th-light-green">Deskripsi</th>
              <th className="kkr-th-light-green">Kode ICD-9-CM</th>
              <th className="kkr-th-light-green">Deskripsi</th>
              <th className="kkr-th-light-green">Ya</th>
              <th className="kkr-th-light-green">Tidak</th>
            </tr>
          </thead>
          <tbody>
            {formData.prosedur.map((row, i) => (
              <tr key={`proc-${i}`}>
                <td style={{textAlign:'center'}}>{i+1}</td>
                <td style={{textAlign:'center'}}>{row.klaim_kode}</td>
                <td style={{fontSize:9}}>{row.klaim_desc}</td>
                <td><input className="kkr-input-line" style={{textAlign:'center'}} value={row.rev_kode} onChange={e => updateArray('prosedur', i, 'rev_kode', e.target.value)} /></td>
                <td><input className="kkr-input-line" style={{fontSize:9}} value={row.rev_desc} onChange={e => updateArray('prosedur', i, 'rev_desc', e.target.value)} /></td>
                <td style={{textAlign:'center'}}><input type="radio" checked={row.sesuai === 'Y'} onChange={() => updateArray('prosedur', i, 'sesuai', 'Y')}/></td>
                <td style={{textAlign:'center'}}><input type="radio" checked={row.sesuai === 'N'} onChange={() => updateArray('prosedur', i, 'sesuai', 'N')}/></td>
                <td><input className="kkr-input-line" value={row.catatan} onChange={e => updateArray('prosedur', i, 'catatan', e.target.value)} /></td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* SECTION 6 & 7 */}
        <div style={{ display: 'grid', gridTemplateColumns: '40% 59%', gap: '1%', marginTop: 12 }}>
          {/* SECTION 6 */}
          <div>
            <div className="kkr-section-header" style={{backgroundColor: '#00695c'}}>6. VERIFIKASI DUAL CODING</div>
            <table className="kkr-data-table kkr-full-border kkr-grid-table">
              <thead>
                <tr>
                  <th rowSpan="2" className="kkr-th-light-green">Komponen</th>
                  <th rowSpan="2" className="kkr-th-light-green">INA-CBG</th>
                  <th rowSpan="2" className="kkr-th-light-green">iDRG</th>
                  <th colSpan="2" className="kkr-th-light-green">Konsisten?</th>
                  <th rowSpan="2" className="kkr-th-light-green">Catatan</th>
                </tr>
                <tr>
                  <th className="kkr-th-light-green">Ya</th>
                  <th className="kkr-th-light-green">Tidak</th>
                </tr>
              </thead>
              <tbody>
                {['principal_diagnosis', 'secondary_diagnosis', 'prosedur', 'grouping', 'severity', 'tarif'].map(comp => (
                  <tr key={comp}>
                    <td style={{fontSize:9}}>{comp.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                    <td><input className="kkr-input-line" value={formData.verifikasi_dual[comp].ina} onChange={e => updateNested('verifikasi_dual', comp, {...formData.verifikasi_dual[comp], ina: e.target.value})} /></td>
                    <td><input className="kkr-input-line" value={formData.verifikasi_dual[comp].idrg} onChange={e => updateNested('verifikasi_dual', comp, {...formData.verifikasi_dual[comp], idrg: e.target.value})} /></td>
                    <td style={{textAlign:'center'}}><input type="radio" checked={formData.verifikasi_dual[comp].konsisten === 'Y'} onChange={() => updateNested('verifikasi_dual', comp, {...formData.verifikasi_dual[comp], konsisten: 'Y'})}/></td>
                    <td style={{textAlign:'center'}}><input type="radio" checked={formData.verifikasi_dual[comp].konsisten === 'N'} onChange={() => updateNested('verifikasi_dual', comp, {...formData.verifikasi_dual[comp], konsisten: 'N'})}/></td>
                    <td><input className="kkr-input-line" value={formData.verifikasi_dual[comp].catatan} onChange={e => updateNested('verifikasi_dual', comp, {...formData.verifikasi_dual[comp], catatan: e.target.value})} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* SECTION 7 */}
          <div>
            <div className="kkr-section-header" style={{backgroundColor: '#00695c'}}>7. RINGKASAN TEMUAN (HASIL REVIEW ON SITE)</div>
            <table className="kkr-data-table kkr-full-border kkr-grid-table">
              <thead>
                <tr>
                  <th width="5%" className="kkr-th-light-green">No.</th>
                  <th width="25%" className="kkr-th-light-green">Jenis Temuan</th>
                  <th width="35%" className="kkr-th-light-green">Deskripsi Temuan</th>
                  <th width="20%" className="kkr-th-light-green">Kategori</th>
                  <th width="15%" className="kkr-th-light-green">Dampak</th>
                </tr>
              </thead>
              <tbody>
                {formData.ringkasan_temuan.map((row, i) => (
                  <tr key={`temuan-${i}`}>
                    <td style={{textAlign:'center'}}>{i+1}</td>
                    <td><input className="kkr-input-line" value={row.jenis} onChange={e => updateArray('ringkasan_temuan', i, 'jenis', e.target.value)} /></td>
                    <td><input className="kkr-input-line" style={{fontSize:9}} value={row.deskripsi} onChange={e => updateArray('ringkasan_temuan', i, 'deskripsi', e.target.value)} /></td>
                    <td>
                      <select className="kkr-input-line" style={{fontSize:9}} value={row.kategori} onChange={e => updateArray('ringkasan_temuan', i, 'kategori', e.target.value)}>
                        <option value=""></option>
                        <option value="Minor">Minor</option>
                        <option value="Moderate">Moderate</option>
                        <option value="Major">Major</option>
                        <option value="Critical">Critical</option>
                      </select>
                    </td>
                    <td>
                      <select className="kkr-input-line" style={{fontSize:9}} value={row.dampak} onChange={e => updateArray('ringkasan_temuan', i, 'dampak', e.target.value)}>
                        <option value=""></option>
                        <option value="Grouping">Grouping</option>
                        <option value="Tarif">Tarif</option>
                        <option value="CL">CL</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* SECTION 8 & 9 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
          {/* SECTION 8 */}
          <div>
            <div className="kkr-section-header" style={{backgroundColor: '#00695c'}}>8. ANALISIS & PENYEBAB KETIDAKSESUAIAN (ROOT CAUSE)</div>
            <div className="kkr-box-border" style={{ display: 'flex', flexDirection: 'column', padding: 8 }}>
              <div style={{ fontSize: 10, fontWeight:'bold', marginBottom: 2 }}>Analisis Reviewer:</div>
              <textarea 
                className="kkr-textarea"
                style={{ height: 60, borderBottom:'1px dotted #ccc', marginBottom: 8 }}
                value={formData.analisis_reviewer}
                onChange={e => setFormData({...formData, analisis_reviewer: e.target.value})}
              />
              <div style={{ fontSize: 10, fontWeight:'bold', marginBottom: 4 }}>Penyebab Utama (Root Cause) – Pilih yang sesuai:</div>
              <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', fontSize:9, gap:4}}>
                {['Pemilihan Diagnosis Utama', 'Pemilihan Diagnosis Sekunder', 'Pemilihan Prosedur / Tindakan', 'Aturan Kombinasi Kode', 'Sequencing', 'Dokumentasi Klinis Tidak Lengkap', 'Pemahaman Aturan Koding'].map(rc => (
                  <label key={rc} style={{display:'flex', alignItems:'center', gap:4}}>
                    <input type="checkbox" checked={formData.penyebab_utama[rc] || false} onChange={e => updateNested('penyebab_utama', rc, e.target.checked)} /> {rc}
                  </label>
                ))}
                <label style={{display:'flex', alignItems:'center', gap:4}}>
                  <input type="checkbox" checked={formData.penyebab_utama['Lainnya'] || false} onChange={e => updateNested('penyebab_utama', 'Lainnya', e.target.checked)} /> Lainnya:
                  <input type="text" className="kkr-input-line" value={formData.penyebab_utama['lainnya_text'] || ''} onChange={e => updateNested('penyebab_utama', 'lainnya_text', e.target.value)} />
                </label>
              </div>
            </div>
          </div>
          {/* SECTION 9 */}
          <div>
            <div className="kkr-section-header" style={{backgroundColor: '#00695c'}}>9. REKOMENDASI</div>
            <div className="kkr-box-border" style={{ display: 'flex', flexDirection: 'column', padding: 8 }}>
              <div style={{ fontSize: 10, fontWeight:'bold', marginBottom: 4 }}>Rekomendasi Reviewer:</div>
              <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', fontSize:9, gap:4, marginBottom: 8}}>
                {['Edukasi / Pelatihan Koding', 'Perbaikan Dokumentasi Klinis', 'Perbaikan Proses Koding', 'Audit Ulang', 'On Site Re-Audit'].map(rek => (
                  <label key={rek} style={{display:'flex', alignItems:'center', gap:4}}>
                    <input type="checkbox" checked={formData.rekomendasi[rek] || false} onChange={e => updateNested('rekomendasi', rek, e.target.checked)} /> {rek}
                  </label>
                ))}
                <label style={{display:'flex', alignItems:'center', gap:4, gridColumn:'1 / -1'}}>
                  <input type="checkbox" checked={formData.rekomendasi['Lainnya'] || false} onChange={e => updateNested('rekomendasi', 'Lainnya', e.target.checked)} /> Lainnya:
                  <input type="text" className="kkr-input-line" value={formData.rekomendasi['lainnya_text'] || ''} onChange={e => updateNested('rekomendasi', 'lainnya_text', e.target.value)} />
                </label>
              </div>
              <div style={{ fontSize: 10, fontWeight:'bold', marginBottom: 2 }}>Catatan Tambahan:</div>
              <textarea 
                className="kkr-textarea"
                style={{ height: 40 }}
                value={formData.catatan_tambahan}
                onChange={e => setFormData({...formData, catatan_tambahan: e.target.value})}
              />
            </div>
          </div>
        </div>

        {/* SECTION 10 & 11 */}
        <div style={{ display: 'grid', gridTemplateColumns: '40% 59%', gap: '1%', marginTop: 12 }}>
          {/* SECTION 10 */}
          <div>
            <div className="kkr-section-header" style={{backgroundColor: '#00695c'}}>10. KESIMPULAN REVIEWER</div>
            <div className="kkr-box-border" style={{ display: 'flex', flexDirection: 'column', padding: 8 }}>
              <div style={{ fontSize: 10, fontWeight:'bold', marginBottom: 4 }}>Kesimpulan:</div>
              <div style={{display:'flex', flexDirection:'column', fontSize:10, gap:4, marginBottom:8}}>
                <label style={{display:'flex', alignItems:'center', gap:4}}>
                  <input type="radio" name="kesimpulan_os" checked={formData.kesimpulan === 'Sesuai'} onChange={() => setFormData({...formData, kesimpulan: 'Sesuai'})} /> Sesuai (Tidak ditemukan ketidaksesuaian signifikan)
                </label>
                <div style={{display:'flex', gap:12}}>
                  <label style={{display:'flex', alignItems:'center', gap:4}}>
                    <input type="radio" name="kesimpulan_os" checked={formData.kesimpulan === 'Tidak Sesuai'} onChange={() => setFormData({...formData, kesimpulan: 'Tidak Sesuai'})} /> Tidak Sesuai (Ditemukan)
                  </label>
                  <label style={{display:'flex', alignItems:'center', gap:4}}>
                    <input type="radio" name="kesimpulan_os" checked={formData.kesimpulan === 'Perlu Klarifikasi'} onChange={() => setFormData({...formData, kesimpulan: 'Perlu Klarifikasi'})} /> Perlu Klarifikasi Tambahan
                  </label>
                </div>
              </div>
              <div style={{ fontSize: 10, fontWeight:'bold', marginBottom: 2 }}>Penjelasan Singkat:</div>
              <textarea 
                className="kkr-textarea"
                style={{ height: 40, borderBottom:'1px dotted #ccc' }}
                value={formData.penjelasan_singkat}
                onChange={e => setFormData({...formData, penjelasan_singkat: e.target.value})}
              />
            </div>
          </div>
          {/* SECTION 11 */}
          <div>
            <div className="kkr-section-header" style={{backgroundColor: '#00695c'}}>11. PARAF / PENGESAHAN</div>
            <div className="kkr-box-border" style={{ height: 'calc(100% - 21px)', display: 'flex', justifyContent: 'space-between', padding: '12px 24px' }}>
              {[
                { title: 'Reviewer,', key: 'reviewer_name', dateKey: 'tanggal_review' },
                { title: 'Ketua Tim Reviewer,', key: 'ketua_tim_name' },
                { title: 'Perwakilan FPKTL (Opsional)', key: 'perwakilan_rs_name' }
              ].map(paraf => (
                <div key={paraf.title} style={{ width: '30%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: 10, fontWeight: 700 }}>{paraf.title}</div>
                  <div style={{ width: '100%' }}>
                    <input type="text" className="kkr-input-line" placeholder="(..........................................)" value={formData[paraf.key]} onChange={e => setFormData({...formData, [paraf.key]: e.target.value})} style={{ textAlign: 'center' }} />
                  </div>
                  <div style={{ fontSize: 10, display: 'flex', width: '100%', alignItems: 'center' }}>
                    Tanggal: {paraf.dateKey ? (
                      <input type="date" className="kkr-input-line" style={{ flex: 1, marginLeft: 4 }} value={formData[paraf.dateKey]} onChange={e => setFormData({...formData, [paraf.dateKey]: e.target.value})} />
                    ) : (
                      <span style={{ flex: 1, borderBottom: '1px dotted #888', marginLeft: 4 }}>&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* FOOTER PANDUAN */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginTop: 12, border: '1px solid #ccc', borderRadius: 4, padding: 8 }}>
          <div>
             <div style={{ fontSize: 9, fontWeight: 700, color: '#00695c', marginBottom: 4 }}>KATEGORI TEMUAN</div>
             <table style={{ fontSize: 8 }}>
               <tbody>
                 <tr><td width="20%" className="kkr-fw-bold" style={{verticalAlign:'top'}}>Minor</td><td style={{verticalAlign:'top'}}>: Perbedaan tidak berdampak signifikan pada grouping/nominal</td></tr>
                 <tr><td className="kkr-fw-bold" style={{verticalAlign:'top'}}>Moderate</td><td style={{verticalAlign:'top'}}>: Perbedaan berdampak pada severity/complexity level atau tarif kecil</td></tr>
                 <tr><td className="kkr-fw-bold" style={{verticalAlign:'top'}}>Major</td><td style={{verticalAlign:'top'}}>: Perbedaan berdampak pada grouping atau tarif signifikan</td></tr>
                 <tr><td className="kkr-fw-bold" style={{verticalAlign:'top'}}>Critical</td><td style={{verticalAlign:'top'}}>: Perbedaan signifikan, potensi fraud atau pelanggaran serius</td></tr>
               </tbody>
             </table>
          </div>
          <div>
             <div style={{ fontSize: 9, fontWeight: 700, color: '#00695c', marginBottom: 4 }}>DAMPAK (PILIH SALAH SATU)</div>
             <div style={{ fontSize: 8, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
               <div>[ &nbsp; ] Tidak Ada Dampak</div>
               <div>[ &nbsp; ] Grouping Berubah</div>
               <div>[ &nbsp; ] Tarif Berubah</div>
               <div>[ &nbsp; ] Complexity Level Berubah</div>
             </div>
          </div>
          <div>
             <div style={{ fontSize: 9, fontWeight: 700, color: '#00695c', marginBottom: 4 }}>CATATAN PENTING</div>
             <ol style={{ fontSize: 8, margin: 0, paddingLeft: 12 }}>
               <li>Formulir ini digunakan untuk On Site Audit berdasarkan bukti dokumen klinis.</li>
               <li>Penilaian harus objektif, berbasis bukti, dan sesuai aturan pengodean.</li>
               <li>Semua temuan harus didukung oleh dokumentasi klinis yang ditelaah.</li>
               <li>Hasil review menjadi dasar rekomendasi perbaikan dan monitoring.</li>
             </ol>
          </div>
        </div>

      </div>
    </div>
  );
}
