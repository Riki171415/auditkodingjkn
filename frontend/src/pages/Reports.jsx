import { useState, useEffect } from 'react';
import { FileText, Download, CheckCircle, AlertTriangle, FileSpreadsheet } from 'lucide-react';
import axios from 'axios';

export default function Reports() {
  const [activeTab, setActiveTab] = useState('desk-review');
  const [drData, setDrData] = useState([]);
  const [osData, setOsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedHospital, setSelectedHospital] = useState('ALL');

  useEffect(() => {
    Promise.all([
      axios.get('/api/reports/recap-dr'),
      axios.get('/api/reports/recap-os')
    ]).then(([resDr, resOs]) => {
      setDrData(resDr.data.data);
      setOsData(resOs.data.data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  const exportCSV = (data, filename, type) => {
    let filteredData = data;
    if (selectedHospital !== 'ALL') {
      filteredData = data.filter(d => d.kode_rs === selectedHospital);
    }

    if (!filteredData || filteredData.length === 0) {
      alert('Tidak ada data untuk diekspor');
      return;
    }

    let actualFilename = filename;
    if (selectedHospital !== 'ALL') {
      const rsName = filteredData[0].nama_rs.replace(/[^a-zA-Z0-9]/g, '_');
      actualFilename = `${filename}_RS_${rsName}`;
    }

    let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
    
    // Define headers based on report type
    let headers = [];
    if (type === 'dr') {
      headers = ['Nomor SEP', 'Kode RS', 'Nama RS', 'Kelas', 'Reviewer', 'Tanggal KKR', 'Kode INA-CBG', 'Tarif INA-CBG', 'Tarif RS', 'Selisih Tarif', 'Keputusan', 'Rekomendasi Lanjut'];
    } else if (type === 'os') {
      headers = ['Nomor SEP', 'Kode RS', 'Nama RS', 'Reviewer', 'Tanggal KKR', 'Kode INA-CBG', 'Tarif INA-CBG', 'Tarif RS', 'Selisih Tarif', 'Kesimpulan'];
    }
    csvContent += headers.join(";") + "\r\n";
    
    filteredData.forEach(row => {
      let csvRow = [];
      if (type === 'dr') {
        const selisih = (row.tarif_inacbg || 0) - (row.tarif_rs || 0);
        csvRow = [
          row.sep, row.kode_rs, `"${row.nama_rs}"`, row.kelas || '-', 
          `"${row.reviewer_name}"`, row.tanggal, row.inacbg, 
          row.tarif_inacbg, row.tarif_rs, selisih, 
          `"${row.keputusan}"`, `"${row.rekomendasi_lanjut}"`
        ];
      } else if (type === 'os') {
        const selisih = (row.tarif_inacbg || 0) - (row.tarif_rs || 0);
        csvRow = [
          row.sep, row.kode_rs, `"${row.nama_rs}"`, 
          `"${row.reviewer_name}"`, row.tanggal, row.inacbg, 
          row.tarif_inacbg, row.tarif_rs, selisih, 
          `"${row.kesimpulan}"`
        ];
      }
      csvContent += csvRow.join(";") + "\r\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${actualFilename}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) return <div className="fade-in"><div className="spinner" style={{margin:'100px auto'}}></div></div>;

  // Extract unique hospitals for dropdown
  const getUniqueHospitals = (data) => {
    const map = new Map();
    data.forEach(item => {
      if (!map.has(item.kode_rs)) {
        map.set(item.kode_rs, item.nama_rs);
      }
    });
    return Array.from(map.entries()).map(([kode_rs, nama_rs]) => ({ kode_rs, nama_rs }));
  };

  const drHospitals = getUniqueHospitals(drData);
  const osHospitals = getUniqueHospitals(osData);

  const displayedDrData = selectedHospital === 'ALL' ? drData : drData.filter(d => d.kode_rs === selectedHospital);
  const displayedOsData = selectedHospital === 'ALL' ? osData : osData.filter(d => d.kode_rs === selectedHospital);

  const renderDeskReview = () => (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h3 style={{ margin: 0, color: 'var(--kmk-navy)' }}>Rekapitulasi KKR Desk Review (KKR-DR01)</h3>
          <p style={{ margin: 0, fontSize: 13, color: 'var(--text-muted)' }}>Total KKR Ditampilkan: {displayedDrData.length}</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <select 
            className="form-control" 
            style={{ width: 250, padding: '6px 12px', fontSize: 13 }}
            value={selectedHospital}
            onChange={(e) => setSelectedHospital(e.target.value)}
          >
            <option value="ALL">Semua Rumah Sakit</option>
            {drHospitals.map(rs => (
              <option key={rs.kode_rs} value={rs.kode_rs}>{rs.nama_rs} ({rs.kode_rs})</option>
            ))}
          </select>
          {selectedHospital !== 'ALL' && (
            <a 
              className="btn btn-secondary" 
              href={`/api/reports/export-word/${selectedHospital}`}
              target="_blank"
              rel="noreferrer"
            >
              <FileSpreadsheet size={16} /> Cetak LHA (Word)
            </a>
          )}
          <button className="btn btn-primary" onClick={() => exportCSV(drData, 'Rekap_DeskReview_KKR-DR01', 'dr')}>
            <Download size={16} /> Export CSV (Excel)
          </button>
        </div>
      </div>
      
      <div className="glass-panel" style={{ overflowX: 'auto', padding: 16 }}>
        <table className="bi-table">
          <thead>
            <tr>
              <th>No</th>
              <th>Nomor SEP</th>
              <th>Rumah Sakit</th>
              <th>Reviewer</th>
              <th>Tarif INA-CBG</th>
              <th>Keputusan</th>
            </tr>
          </thead>
          <tbody>
            {displayedDrData.length === 0 ? (
              <tr><td colSpan="6" style={{textAlign:'center', padding:24}} className="text-muted">Belum ada KKR Desk Review yang diselesaikan.</td></tr>
            ) : (
              displayedDrData.map((row, i) => (
                <tr key={row.sep}>
                  <td>{i+1}</td>
                  <td style={{fontFamily:'monospace', fontSize:12, fontWeight:600}}>{row.sep}</td>
                  <td>
                    <div style={{fontWeight:600}}>{row.nama_rs}</div>
                    <div style={{fontSize:11, color:'var(--text-muted)'}}>{row.kode_rs}</div>
                  </td>
                  <td>{row.reviewer_name || '-'}</td>
                  <td>Rp {(row.tarif_inacbg || 0).toLocaleString('id-ID')}</td>
                  <td>
                    <span className={`badge ${row.keputusan.includes('On-Site') ? 'badge-danger' : row.keputusan.includes('Monitoring') ? 'badge-warning' : 'badge-success'}`}>
                      {row.keputusan || 'Belum Diisi'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderOnSite = () => (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h3 style={{ margin: 0, color: 'var(--kmk-navy)' }}>Rekapitulasi KKR On-Site Audit (KKR-OS01)</h3>
          <p style={{ margin: 0, fontSize: 13, color: 'var(--text-muted)' }}>Total KKR Ditampilkan: {displayedOsData.length}</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <select 
            className="form-control" 
            style={{ width: 250, padding: '6px 12px', fontSize: 13 }}
            value={selectedHospital}
            onChange={(e) => setSelectedHospital(e.target.value)}
          >
            <option value="ALL">Semua Rumah Sakit</option>
            {osHospitals.map(rs => (
              <option key={rs.kode_rs} value={rs.kode_rs}>{rs.nama_rs} ({rs.kode_rs})</option>
            ))}
          </select>
          <button className="btn btn-primary" onClick={() => exportCSV(osData, 'Rekap_OnSiteAudit_KKR-OS01', 'os')}>
            <Download size={16} /> Export CSV (Excel)
          </button>
        </div>
      </div>
      
      <div className="glass-panel" style={{ overflowX: 'auto', padding: 16 }}>
        <table className="bi-table">
          <thead>
            <tr>
              <th>No</th>
              <th>Nomor SEP</th>
              <th>Rumah Sakit</th>
              <th>Reviewer</th>
              <th>Tarif INA-CBG</th>
              <th>Kesimpulan Lapangan</th>
            </tr>
          </thead>
          <tbody>
            {displayedOsData.length === 0 ? (
              <tr><td colSpan="6" style={{textAlign:'center', padding:24}} className="text-muted">Belum ada KKR On-Site Audit yang diselesaikan.</td></tr>
            ) : (
              displayedOsData.map((row, i) => (
                <tr key={row.sep}>
                  <td>{i+1}</td>
                  <td style={{fontFamily:'monospace', fontSize:12, fontWeight:600}}>{row.sep}</td>
                  <td>
                    <div style={{fontWeight:600}}>{row.nama_rs}</div>
                    <div style={{fontSize:11, color:'var(--text-muted)'}}>{row.kode_rs}</div>
                  </td>
                  <td>{row.reviewer_name || '-'}</td>
                  <td>Rp {(row.tarif_inacbg || 0).toLocaleString('id-ID')}</td>
                  <td>
                    <span className={`badge ${row.kesimpulan.includes('Tidak Sesuai') ? 'badge-danger' : 'badge-success'}`}>
                      {row.kesimpulan || 'Belum Diisi'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderLaporanAkhir = () => (
    <div className="fade-in" style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:40, textAlign:'center' }}>
      <FileSpreadsheet size={64} color="var(--kmk-cyan)" style={{ marginBottom: 16, opacity: 0.5 }} />
      <h2 style={{ color: 'var(--kmk-navy)', margin: '0 0 8px 0' }}>Laporan Rekonsiliasi Akhir</h2>
      <p className="text-muted" style={{ maxWidth: 500, margin: '0 auto' }}>
        Modul ini akan menggabungkan hasil Desk Review dan On-Site Audit secara komprehensif, mengkalkulasi total penghematan/selisih tarif nasional, dan mengekspor dokumen resmi laporan akhir.
      </p>
      <div className="badge badge-warning" style={{ marginTop: 24, fontSize: 14, padding: '8px 16px' }}>
        Status: Dalam Tahap Pengembangan (Coming Soon)
      </div>
    </div>
  );

  return (
    <div className="fade-in" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
            <FileText className="text-primary" size={28} />
            Tahap 5: Rekonsiliasi & Laporan
          </h1>
          <p className="text-muted" style={{ margin: '8px 0 0 0' }}>
            Rekapitulasi seluruh Kertas Kerja Reviewer dan ekspor laporan.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 24, borderBottom: '1px solid var(--border-color)', paddingBottom: 16 }}>
        <button 
          className={`btn ${activeTab === 'desk-review' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => { setActiveTab('desk-review'); setSelectedHospital('ALL'); }}
          style={{ padding: '8px 24px', border: activeTab !== 'desk-review' ? 'none' : undefined, background: activeTab !== 'desk-review' ? 'transparent' : undefined }}
        >
          <CheckCircle size={16} /> 1. Laporan Desk Review
        </button>
        <button 
          className={`btn ${activeTab === 'onsite' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => { setActiveTab('onsite'); setSelectedHospital('ALL'); }}
          style={{ padding: '8px 24px', border: activeTab !== 'onsite' ? 'none' : undefined, background: activeTab !== 'onsite' ? 'transparent' : undefined }}
        >
          <AlertTriangle size={16} /> 2. Laporan On-Site Audit
        </button>
        <button 
          className={`btn ${activeTab === 'akhir' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => { setActiveTab('akhir'); setSelectedHospital('ALL'); }}
          style={{ padding: '8px 24px', border: activeTab !== 'akhir' ? 'none' : undefined, background: activeTab !== 'akhir' ? 'transparent' : undefined }}
        >
          <FileSpreadsheet size={16} /> 3. Laporan Akhir (Rekonsiliasi)
        </button>
      </div>

      <div>
        {activeTab === 'desk-review' && renderDeskReview()}
        {activeTab === 'onsite' && renderOnSite()}
        {activeTab === 'akhir' && renderLaporanAkhir()}
      </div>

    </div>
  );
}
