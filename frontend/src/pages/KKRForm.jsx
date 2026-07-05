import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ChevronLeft, Save, Download, Printer, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function KKRForm() {
  const { sep } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    reviewer_name: '',
    tanggal_review: new Date().toISOString().split('T')[0],
    catatan: ''
  });

  useEffect(() => {
    // Load validation rules and case
    axios.get(`/api/validate/${encodeURIComponent(sep)}`)
      .then(res => {
        setData(res.data.data);
        setLoading(false);
        // Load saved kkr if exists
        axios.get(`/api/kkr-dr01/load/${encodeURIComponent(sep)}`)
          .then(res_load => {
            if (res_load.data.data) {
              setFormData(f => ({
                ...f,
                reviewer_name: res_load.data.data.reviewer_name || '',
                tanggal_review: res_load.data.data.tanggal_review || f.tanggal_review,
                catatan: res_load.data.data.catatan || ''
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
      ...data,
      ...formData,
      sep: sep
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

  const handleExportPDF = () => {
    window.location.href = `/api/export/dr01/pdf/${encodeURIComponent(sep)}`;
  };
  
  const handleExportExcel = () => {
    window.location.href = `/api/export/dr01/excel/${encodeURIComponent(sep)}`;
  };

  if (loading) return <div className="fade-in"><div className="spinner" style={{margin:'auto', width:40,height:40,border:'4px solid var(--kmk-cyan)',borderTopColor:'transparent',borderRadius:'50%'}}></div></div>;
  if (!data) return <div>Gagal memuat formulir.</div>;

  return (
    <div className="fade-in" style={{ maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <button onClick={() => window.history.back()} className="btn btn-outline" style={{ border: 'none', padding: 0 }}>
          <ChevronLeft size={16} /> Kembali
        </button>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-outline" onClick={handleExportExcel}>
            <Download size={16} /> Excel
          </button>
          <button className="btn btn-outline" onClick={handleExportPDF}>
            <Printer size={16} /> PDF
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            <Save size={16} /> {saving ? 'Menyimpan...' : 'Simpan KKR'}
          </button>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: 40, background: 'white' }}>
        <div style={{ textAlign: 'center', marginBottom: 32, borderBottom: '2px solid var(--border-color)', paddingBottom: 16 }}>
          <h2 style={{ color: 'var(--kmk-navy)', margin: 0, textTransform: 'uppercase' }}>Kertas Kerja Reviewer (KKR) - Desk Review</h2>
          <div style={{ color: 'var(--text-muted)', marginTop: 8 }}>KEMENTERIAN KESEHATAN REPUBLIK INDONESIA</div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32 }}>
          <div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Nomor SEP</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--kmk-navy)' }}>{data.case.sep}</div>
            
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 12 }}>Rumah Sakit</div>
            <div style={{ fontSize: 14, fontWeight: 500 }}>{data.case.nama_rs}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Kode INA-CBG</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--kmk-cyan-dark)' }}>{data.case.inacbg}</div>
            
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 12 }}>Deskripsi INA-CBG</div>
            <div style={{ fontSize: 14, fontWeight: 500 }}>{data.case.deskripsi_inacbg}</div>
          </div>
        </div>
        
        <h3 style={{ marginBottom: 16, fontSize: 16, borderBottom: '1px solid #eee', paddingBottom: 8 }}>Hasil Validasi Rule Koding (71 Aturan)</h3>
        {data.total_triggered === 0 ? (
          <div style={{ padding: 16, background: '#E8F8F5', color: 'var(--kmk-green)', borderRadius: 8, display: 'flex', gap: 12 }}>
            <AlertCircle /> Kasus ini sesuai dengan seluruh aturan koding. Tidak ada temuan audit.
          </div>
        ) : (
          <div>
            <div style={{ padding: 16, background: '#FDEDEC', color: 'var(--kmk-red)', borderRadius: 8, display: 'flex', gap: 12, marginBottom: 16 }}>
              <AlertCircle /> Terdapat {data.total_triggered} potensi pelanggaran aturan koding.
            </div>
            
            <table className="bi-table">
              <thead>
                <tr>
                  <th>No</th>
                  <th>Aturan Dilanggar</th>
                  <th>Keterangan</th>
                  <th>Tingkat Keparahan</th>
                </tr>
              </thead>
              <tbody>
                {data.triggered_rules.map((rule, idx) => (
                  <tr key={idx}>
                    <td>{idx + 1}</td>
                    <td style={{ fontWeight: 600 }}>{rule.rule_name}</td>
                    <td>{rule.description}</td>
                    <td>
                      <span className={`badge ${rule.severity === 'High' ? 'badge-danger' : 'badge-warning'}`}>
                        {rule.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        <h3 style={{ marginTop: 32, marginBottom: 16, fontSize: 16, borderBottom: '1px solid #eee', paddingBottom: 8 }}>Tindakan Reviewer</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Catatan Audit (Opsional)</label>
            <textarea 
              value={formData.catatan}
              onChange={e => setFormData({...formData, catatan: e.target.value})}
              style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid var(--border-color)', outline: 'none', minHeight: 80, fontFamily: 'inherit' }}
              placeholder="Tambahkan catatan khusus untuk kasus ini..."
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Nama Reviewer</label>
              <input 
                type="text" 
                value={formData.reviewer_name}
                onChange={e => setFormData({...formData, reviewer_name: e.target.value})}
                style={{ width: '100%', padding: 10, borderRadius: 8, border: '1px solid var(--border-color)', outline: 'none' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Tanggal Review</label>
              <input 
                type="date" 
                value={formData.tanggal_review}
                onChange={e => setFormData({...formData, tanggal_review: e.target.value})}
                style={{ width: '100%', padding: 10, borderRadius: 8, border: '1px solid var(--border-color)', outline: 'none' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
