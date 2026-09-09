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
      .then(res => setInfo(res.data.data.info))
      .catch(console.error);
  }, [kode_rs]);

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

  useEffect(() => {
    // Load Cases
    setLoading(true);
    const controller = new AbortController();
    const timer = setTimeout(() => {
      axios.get('/api/cases/' + kode_rs, { params: {page, per_page: 50, search}, signal: controller.signal })
        .then(res => {
            setData(res.data.data);
            // Auto-trigger batch validation so it matches the report without clicking
            handleValidateBatch();
        })
        .catch(err => { if (!axios.isCancel(err)) console.error(err); })
        .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    }, 300);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [kode_rs, page, search]);

  const getStatusBadge = (sep) => {
    if (!batchResults) return <span className="badge badge-info" style={{background: '#eee', color: '#666'}}>Belum Divalidasi</span>;
    const res = batchResults.results.find(r => r.sep === sep);
    if (!res) return <span className="badge badge-info" style={{background: '#eee', color: '#666'}}>Belum Divalidasi</span>;
    
    if (res.rekomendasi.includes('Tidak Sesuai')) {
        return <span className="badge badge-danger">{res.rekomendasi}</span>;
    } else if (res.rekomendasi.includes('Sesuai')) {
        return <span className="badge badge-success">{res.rekomendasi}</span>;
    } else if (res.rekomendasi.includes('Sampling')) {
        return <span className="badge badge-warning">{res.rekomendasi}</span>;
    }
    
    return <span className="badge badge-info">{res.rekomendasi}</span>;
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
                <th>Diagnosa & Prosedur</th>
                <th>INA-CBG</th>
                <th>iDRG</th>
                <th>Skor KNAVP</th>
                <th>Tingkat Risiko</th>
                <th>Rekomendasi</th>
                <th>Aksi KKR</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="9" style={{ textAlign: 'center', padding: '40px 0' }}>Memuat data...</td></tr>
              ) : data.cases.length === 0 ? (
                <tr><td colSpan="9" style={{ textAlign: 'center', padding: '40px 0' }}>Data tidak ditemukan</td></tr>
              ) : (
                data.cases.map((c, i) => {
                  const res = batchResults?.results.find(r => r.sep === c.sep);
                  const skor = res ? res.knavp_skor : '-';
                  const risiko = res ? res.tingkat_risiko : '-';
                  
                  return (
                  <tr key={c.sep}>
                    <td style={{ color: 'var(--text-muted)' }}>{(page-1)*50 + i + 1}</td>
                    <td style={{ fontFamily: 'monospace', fontWeight: 600, color: 'var(--kmk-cyan-dark)' }}>{c.sep}</td>
                    <td>
                      <div style={{ fontSize: 11, marginBottom: 4 }}><strong style={{color:'var(--text-muted)'}}>Diag:</strong> {c.diaglist?.substring(0, 50)}{c.diaglist?.length > 50 ? '...' : ''}</div>
                      <div style={{ fontSize: 11 }}><strong style={{color:'var(--text-muted)'}}>Proc:</strong> {c.proclist?.substring(0, 50)}{c.proclist?.length > 50 ? '...' : ''}</div>
                    </td>
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
                    <td style={{ fontWeight: 600, textAlign: 'center' }}>{skor}</td>
                    <td>
                      {risiko === 'Tinggi' ? <span className="badge badge-danger">Tinggi</span> :
                       risiko === 'Sedang' ? <span className="badge badge-warning">Sedang</span> :
                       risiko === 'Rendah' ? <span className="badge badge-success">Rendah</span> :
                       <span className="badge badge-info">{risiko}</span>}
                    </td>
                    <td>{getStatusBadge(c.sep)}</td>
                    <td>
                      <Link to={`/kkr-dr01/${encodeURIComponent(c.sep)}`} className="btn btn-primary" style={{ padding: '4px 8px', fontSize: 11 }}>
                        <ClipboardList size={12} /> Buka KKR
                      </Link>
                    </td>
                  </tr>
                )})
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
