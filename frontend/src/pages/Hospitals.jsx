import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Building, ChevronRight } from 'lucide-react';
import axios from 'axios';

export default function Hospitals() {
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    axios.get('/api/hospitals')
      .then(res => {
        setHospitals(res.data.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const filtered = hospitals.filter(h => 
    h.nama_rs?.toLowerCase().includes(search.toLowerCase()) || 
    h.kode_rs?.toLowerCase().includes(search.toLowerCase()) ||
    h.regional?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '24px' }}>Daftar RS Sampel Audit</h1>
          <p style={{ color: 'var(--text-muted)' }}>Pilih Rumah Sakit untuk melakukan proses validasi dan Kertas Kerja Reviewer (KKR)</p>
        </div>
        
        <div style={{ position: 'relative', width: 300 }}>
          <Search size={18} style={{ position: 'absolute', left: 12, top: 10, color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            placeholder="Cari RS atau Regional..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ 
              width: '100%', padding: '10px 12px 10px 40px', 
              borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)',
              outline: 'none', background: 'var(--bg-card)'
            }}
          />
        </div>
      </div>

      <div className="table-container glass-panel">
        <table className="bi-table">
          <thead>
            <tr>
              <th style={{ width: '60px' }}>No</th>
              <th>Kode RS</th>
              <th>Nama Rumah Sakit</th>
              <th>Regional</th>
              <th>Total Kasus</th>
              <th>Status Audit</th>
              <th style={{ textAlign: 'right' }}>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="7" style={{ textAlign: 'center', padding: '40px 0' }}><div className="spinner" style={{width:24,height:24,border:'3px solid var(--kmk-cyan)',borderTopColor:'transparent',borderRadius:'50%',margin:'auto'}}></div></td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan="7" style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>Tidak ada RS yang cocok dengan pencarian.</td></tr>
            ) : (
              filtered.map((rs, idx) => (
                <tr key={rs.kode_rs}>
                  <td style={{ color: 'var(--text-muted)' }}>{idx + 1}</td>
                  <td style={{ fontFamily: 'monospace', color: 'var(--kmk-cyan-dark)' }}>{rs.kode_rs}</td>
                  <td style={{ fontWeight: 500 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Building size={14} color="var(--text-muted)" /> {rs.nama_rs || '-'}
                    </div>
                  </td>
                  <td>{rs.regional || '-'}</td>
                  <td>{rs.total_kasus ? parseInt(rs.total_kasus).toLocaleString('id-ID') : '-'}</td>
                  <td>
                    {rs.cmi_info?.Audit_2SD === 'Audit' ? (
                      <span className="badge badge-danger">Perlu Audit</span>
                    ) : rs.cmi_info?.Audit_2SD === 'Aman' ? (
                      <span className="badge badge-success">Aman</span>
                    ) : (
                      <span className="badge badge-info">N/A</span>
                    )}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <Link to={`/desk-review/${rs.kode_rs}`} className="btn btn-outline" style={{ padding: '6px 12px', fontSize: '12px' }}>
                      Buka Review <ChevronRight size={14} />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
