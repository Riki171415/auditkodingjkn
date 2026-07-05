import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ChevronLeft, Filter, FileCheck2, ClipboardList, Hospital } from 'lucide-react';
import axios from 'axios';

export default function DeskReview() {
  const { kode_rs } = useParams();
  const navigate = useNavigate();
  
  const [info, setInfo] = useState(null);
  const [data, setData] = useState({ cases: [], total: 0, cochran_info: null, page: 1, total_pages: 1 });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [batchResults, setBatchResults] = useState(null);
  const [validating, setValidating] = useState(false);

  useEffect(() => {
    // Load RS Info
    axios.get(`/api/hospitals/${kode_rs}`)
      .then(res => setInfo(res.data.data))
      .catch(console.error);
  }, [kode_rs]);

  useEffect(() => {
    // Load Cases
    setLoading(true);
    axios.get(`/api/cases/${kode_rs}?page=${page}&per_page=50&search=${search}`)
      .then(res => {
        setData(res.data.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [kode_rs, page, search]);

  const handleValidateBatch = () => {
    setValidating(true);
    axios.get(`/api/validate-batch/${kode_rs}`)
      .then(res => {
        setBatchResults(res.data.data);
        setValidating(false);
      })
      .catch(err => {
        console.error(err);
        setValidating(false);
      });
  };

  const getStatusBadge = (sep) => {
    if (!batchResults) return <span className="badge badge-info" style={{background: '#eee', color: '#666'}}>Belum Divalidasi</span>;
    const res = batchResults.results.find(r => r.sep === sep);
    if (!res) return <span className="badge badge-info" style={{background: '#eee', color: '#666'}}>Belum Divalidasi</span>;
    
    if (res.triggered_count === 0) return <span className="badge badge-success">Sesuai Aturan</span>;
    return <span className="badge badge-danger">{res.triggered_count} Temuan</span>;
  };

  return (
    <div className="fade-in">
      <div style={{ marginBottom: 16 }}>
        <button onClick={() => navigate('/hospitals')} className="btn btn-outline" style={{ border: 'none', padding: 0 }}>
          <ChevronLeft size={16} /> Kembali ke Daftar RS
        </button>
      </div>

      <div className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 className="text-gradient" style={{ fontSize: '24px', display: 'flex', alignItems: 'center', gap: 12 }}>
              <Hospital size={24} color="var(--kmk-navy)" /> {info?.nama_rs || 'Memuat...'}
            </h1>
            <p style={{ color: 'var(--text-muted)', marginTop: 4 }}>Kode RS: <strong>{kode_rs}</strong> | Kelas: {info?.kelas || '-'} | Regional: {info?.regional || '-'}</p>
          </div>
          
          <div style={{ textAlign: 'right' }}>
            <button 
              className="btn btn-primary" 
              onClick={handleValidateBatch}
              disabled={validating}
            >
              <FileCheck2 size={16} />
              {validating ? 'Memvalidasi...' : 'Validasi Semua Sampel'}
            </button>
          </div>
        </div>

        {data.cochran_info && (
          <div style={{ marginTop: 24, padding: 16, background: 'var(--kmk-cyan-light)', borderRadius: 'var(--radius-md)', display: 'inline-flex', alignItems: 'center', gap: 12 }}>
            <div style={{ padding: 8, background: 'var(--kmk-cyan)', color: 'white', borderRadius: 8 }}>
              📊 
            </div>
            <div>
              <div style={{ fontSize: 12, color: 'var(--kmk-cyan-dark)', fontWeight: 600 }}>METODE SAMPLING COCHRAN</div>
              <div style={{ fontSize: 14, color: 'var(--kmk-navy)' }}>
                <strong>{data.cochran_info.n_sample}</strong> sampel ditarik dari total <strong>{data.cochran_info.N}</strong> populasi kasus ({data.cochran_info.percentage}%)
              </div>
            </div>
          </div>
        )}
      </div>

      {batchResults && (
        <div className="grid-cards fade-in" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
          <div className="glass-panel" style={{ padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Total Sampel</div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--kmk-navy)' }}>{batchResults.summary.total_kasus}</div>
          </div>
          <div className="glass-panel" style={{ padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Memiliki Temuan</div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--kmk-red)' }}>{batchResults.summary.kasus_dengan_temuan}</div>
          </div>
          <div className="glass-panel" style={{ padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Rekomendasi On-Site</div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#D4AC0D' }}>{batchResults.summary.rekomendasi_onsite}</div>
          </div>
          <div className="glass-panel" style={{ padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Kasus Aman</div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--kmk-green)' }}>{batchResults.summary.kasus_aman}</div>
          </div>
        </div>
      )}

      <div className="table-container glass-panel">
        <div style={{ padding: 16, borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontSize: 16 }}>Daftar Kasus Sampel</h3>
          <input 
            type="text" 
            placeholder="Cari SEP / INA-CBG..." 
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc', outline: 'none' }}
          />
        </div>
        <table className="bi-table">
          <thead>
            <tr>
              <th>No</th>
              <th>Nomor SEP</th>
              <th>INA-CBG</th>
              <th>iDRG (Kemenkes)</th>
              <th>Diagnosa</th>
              <th>Tarif RS</th>
              <th>Tarif INA-CBG</th>
              <th>Validasi Sistem</th>
              <th>Aksi KKR</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="9" style={{ textAlign: 'center', padding: '40px 0' }}>Memuat data...</td></tr>
            ) : data.cases.length === 0 ? (
              <tr><td colSpan="9" style={{ textAlign: 'center', padding: '40px 0' }}>Data tidak ditemukan</td></tr>
            ) : (
              data.cases.map((c, i) => (
                <tr key={c.sep}>
                  <td style={{ color: 'var(--text-muted)' }}>{(page-1)*50 + i + 1}</td>
                  <td style={{ fontFamily: 'monospace', fontWeight: 600, color: 'var(--kmk-cyan-dark)' }}>{c.sep}</td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{c.inacbg}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {c.deskripsi_inacbg}
                    </div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 500, color: 'var(--kmk-navy)' }}>{c.idrg_code || '-'}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {c.deskripsi_idrg || '-'}
                    </div>
                  </td>
                  <td><span style={{ background: '#eee', padding: '2px 6px', borderRadius: 4, fontSize: 11, fontFamily: 'monospace' }}>{c.diaglist?.split(';')[0]}</span></td>
                  <td style={{ color: c.tarif_rs > c.tarif_inacbg ? 'var(--kmk-red)' : 'var(--kmk-green)' }}>Rp {c.tarif_rs?.toLocaleString('id-ID')}</td>
                  <td>Rp {c.tarif_inacbg?.toLocaleString('id-ID')}</td>
                  <td>{getStatusBadge(c.sep)}</td>
                  <td>
                    <Link to={`/kkr-dr01/${encodeURIComponent(c.sep)}`} className="btn btn-primary" style={{ padding: '4px 8px', fontSize: 11 }}>
                      <ClipboardList size={12} /> Buka KKR
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        
        {/* Pagination */}
        <div style={{ padding: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            Menampilkan halaman {data.page} dari {data.total_pages} (Total: {data.total} kasus)
          </div>
          <div style={{ display: 'flex', gap: 4 }}>
            <button className="btn btn-outline" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Prev</button>
            <button className="btn btn-outline" disabled={page === data.total_pages} onClick={() => setPage(p => p + 1)}>Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
