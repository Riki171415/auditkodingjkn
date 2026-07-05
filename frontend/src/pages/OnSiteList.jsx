import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Search, MapPin, BriefcaseMedical } from 'lucide-react';

export default function OnSiteList() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    axios.get('/api/onsite/list')
      .then(res => {
        setCases(res.data.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const filteredCases = cases.filter(c => 
    c.sep.toLowerCase().includes(searchTerm.toLowerCase()) || 
    c.nama_rs.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fade-in" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
            <BriefcaseMedical className="text-primary" size={28} />
            Tahap 4: On-Site Audit
          </h1>
          <p className="text-muted" style={{ margin: '8px 0 0 0' }}>
            Daftar kasus yang direkomendasikan untuk verifikasi lapangan (berdasarkan hasil Desk Review KKR-DR01).
          </p>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: 20 }}>
        <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
          <div className="search-bar" style={{ flex: 1, maxWidth: 400 }}>
            <Search size={18} className="text-muted" />
            <input 
              type="text" 
              placeholder="Cari SEP atau Nama Rumah Sakit..." 
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <div className="spinner" style={{ margin: '0 auto 16px' }}></div>
            <div className="text-muted">Memuat daftar kasus...</div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="bi-table">
              <thead>
                <tr>
                  <th>No</th>
                  <th>Nomor SEP</th>
                  <th>Rumah Sakit</th>
                  <th>Reviewer Desk Review</th>
                  <th>Status On-Site</th>
                  <th>Aksi</th>
                </tr>
              </thead>
              <tbody>
                {filteredCases.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: 40 }} className="text-muted">
                      Tidak ada kasus yang direkomendasikan On-Site Audit saat ini.
                    </td>
                  </tr>
                ) : (
                  filteredCases.map((c, i) => (
                    <tr key={c.sep}>
                      <td>{i + 1}</td>
                      <td>
                        <div style={{ fontWeight: 600, fontFamily: 'monospace' }}>{c.sep}</div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <MapPin size={14} className="text-muted" />
                          <span>{c.nama_rs} <span className="text-muted" style={{fontSize: 12}}>({c.kode_rs})</span></span>
                        </div>
                      </td>
                      <td>{c.reviewer_dr || '-'}</td>
                      <td>
                         <span className="badge badge-warning">Menunggu Audit</span>
                      </td>
                      <td>
                        <Link to={`/kkr-os01/${c.sep}`} className="btn btn-primary" style={{ padding: '6px 12px', fontSize: 13 }}>
                          Isi KKR-OS01
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
