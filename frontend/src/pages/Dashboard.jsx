import { useState, useEffect } from 'react';
import { Activity, Building, FileSpreadsheet, AlertTriangle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis, ReferenceLine, ReferenceArea } from 'recharts';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [scatter, setScatter] = useState([]);
  const [scatterMeta, setScatterMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sampleOnly, setSampleOnly] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      axios.get(`/api/dashboard/stats?sample_only=${sampleOnly}`),
      axios.get(`/api/dashboard/scatter?sample_only=${sampleOnly}`)
    ]).then(([resStats, resScatter]) => {
      setStats(resStats.data.data);
      if (resScatter.data.data.points) {
        setScatter(resScatter.data.data.points);
        setScatterMeta({
          boundaries: resScatter.data.data.boundaries || {},
          insights: resScatter.data.data.insights || {}
        });
      } else {
        // Fallback for old API payload format
        setScatter(resScatter.data.data || []);
      }
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [sampleOnly]);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{ background: 'white', padding: '12px', border: '1px solid var(--border-color)', borderRadius: '8px', boxShadow: 'var(--shadow-md)', fontSize: '12px' }}>
          <p style={{ fontWeight: 600, color: 'var(--kmk-navy)', marginBottom: 4 }}>{data.nama_rs}</p>
          <p>Kode RS: {data.kode_rs}</p>
          <p>Rata-rata CMI: {data.x.toFixed(2)}</p>
          <p>Rata-rata ALOS: {data.y.toFixed(1)} hari</p>
          <p>Total Kasus: {data.z}</p>
          <p style={{ fontWeight: 600, color: data.fill, marginTop: 4 }}>Status: {data.status}</p>
        </div>
      );
    }
    return null;
  };

  if (loading) return <div className="fade-in"><div className="spinner" style={{width:24,height:24,border:'3px solid var(--kmk-cyan)',borderTopColor:'transparent',borderRadius:'50%'}}></div></div>;
  if (!stats || Object.keys(stats).length === 0) return <div>Gagal memuat data. Kemungkinan file data.db tidak ditemukan di server.</div>;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '24px', margin: 0 }}>Tahap 1: Analisis Casemix (Dashboard)</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>Gambaran umum populasi klaim dan identifikasi Rumah Sakit anomali</p>
        </div>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.05)', padding: '6px 12px', borderRadius: 20 }}>
            <span style={{ fontSize: 13, marginRight: 8, fontWeight: !sampleOnly ? 600 : 400, color: !sampleOnly ? 'var(--kmk-navy)' : 'var(--text-muted)' }}>Nasional</span>
            <label style={{ display: 'inline-flex', alignItems: 'center', cursor: 'pointer', position: 'relative' }}>
              <input type="checkbox" style={{ opacity: 0, position: 'absolute' }} checked={sampleOnly} onChange={e => setSampleOnly(e.target.checked)} />
              <div style={{ width: 40, height: 22, background: sampleOnly ? 'var(--kmk-cyan)' : '#ccc', borderRadius: 20, position: 'relative', transition: '0.3s' }}>
                <div style={{ width: 18, height: 18, background: 'white', borderRadius: '50%', position: 'absolute', top: 2, left: sampleOnly ? 20 : 2, transition: '0.3s' }} />
              </div>
            </label>
            <span style={{ fontSize: 13, marginLeft: 8, fontWeight: sampleOnly ? 600 : 400, color: sampleOnly ? 'var(--kmk-cyan)' : 'var(--text-muted)' }}>40 RS Sampel</span>
          </div>
          <Link to="/hospitals" className="btn btn-primary">
            Lanjut Tahap 2: Penetapan Sasaran <ArrowRight size={16} />
          </Link>
        </div>
      </div>
      
      <div className="grid-cards">
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            <Activity size={20} color="var(--kmk-cyan)" /> Populasi Kasus
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--kmk-navy)' }}>
            {stats.total_kasus.toLocaleString('id-ID')}
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            <Building size={20} color="var(--kmk-cyan)" /> Populasi Rumah Sakit
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--kmk-navy)' }}>
            {stats.total_rs.toLocaleString('id-ID')}
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            <FileSpreadsheet size={20} color="var(--kmk-red)" /> RS Outlier (2SD)
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--kmk-red)' }}>
            {stats.audit_2sd ? stats.audit_2sd.toLocaleString('id-ID') : '0'}
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            <AlertTriangle size={20} color="#D4AC0D" /> RS Outlier (IQR)
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: '#D4AC0D' }}>
            {stats.audit_iqr ? stats.audit_iqr.toLocaleString('id-ID') : '0'}
          </div>
        </div>
      </div>

      {stats.cmi_metrics && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ margin: '0 0 16px 0', color: 'var(--kmk-navy)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={20} color="var(--kmk-cyan)" /> Scorecard CMI
          </h3>
          <div className="grid-cards" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
            <div className="glass-panel" style={{ padding: '16px 20px', borderTop: '4px solid var(--kmk-navy)' }}>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>Nasional</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--kmk-navy)' }}>{stats.cmi_metrics['Nasional']?.toFixed(4) || '0.0000'}</div>
            </div>
            {['A', 'B', 'C', 'D'].map(cls => (
              <div key={cls} className="glass-panel" style={{ padding: '16px 20px', borderTop: '4px solid var(--kmk-cyan)' }}>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>Kelas {cls}</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--kmk-navy)' }}>{stats.cmi_metrics[`Kelas ${cls}`]?.toFixed(4) || '0.0000'}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="glass-panel" style={{ padding: '24px 24px 32px 24px', minHeight: 400 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div>
            <h3 style={{ margin: 0, color: 'var(--kmk-navy)' }}>Scatter Plot: CMI vs ALOS per Rumah Sakit</h3>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0, marginTop: 4 }}>
              Setiap titik merepresentasikan 1 Rumah Sakit. Ukuran titik bergantung pada volume kasus. 
              <span style={{ color: 'var(--kmk-red)', fontWeight: 600, marginLeft: 8 }}>Merah = Outlier (Direkomendasikan Audit)</span>
            </p>
          </div>
        </div>
        
        <div style={{ height: 400, width: '100%' }}>
          <ResponsiveContainer>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis 
                type="number" 
                dataKey="x" 
                name="CMI" 
                tick={{fontSize: 12}} 
                label={{ value: 'Case Mix Index (CMI)', position: 'insideBottom', offset: -10, fontSize: 12, fill: 'var(--text-muted)' }} 
              />
              <YAxis 
                type="number" 
                dataKey="y" 
                name="ALOS" 
                tick={{fontSize: 12}} 
                label={{ value: 'Average Length of Stay (ALOS)', angle: -90, position: 'insideLeft', offset: 10, fontSize: 12, fill: 'var(--text-muted)' }} 
              />
              <ZAxis type="number" dataKey="z" range={[10, 200]} name="Volume Kasus" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
              
              {scatterMeta?.boundaries?.mean_cmi && (
                <>
                  <ReferenceArea x1={scatterMeta.boundaries.bawah_2sd} x2={scatterMeta.boundaries.atas_2sd} fill="#27AE60" fillOpacity={0.05} />
                  <ReferenceLine x={scatterMeta.boundaries.bawah_2sd} stroke="#EB5757" strokeDasharray="3 3" label={{ position: 'insideBottomLeft', value: 'Batas Bawah 2SD', fill: '#EB5757', fontSize: 11 }} />
                  <ReferenceLine x={scatterMeta.boundaries.atas_2sd} stroke="#EB5757" strokeDasharray="3 3" label={{ position: 'insideBottomRight', value: 'Batas Atas 2SD', fill: '#EB5757', fontSize: 11 }} />
                  <ReferenceLine x={scatterMeta.boundaries.mean_cmi} stroke="#3498DB" strokeOpacity={0.5} label={{ position: 'insideTop', value: 'Rata-rata CMI', fill: '#3498DB', fontSize: 11 }} />
                </>
              )}
              
              <Scatter name="Rumah Sakit" data={scatter} opacity={0.65} isAnimationActive={false} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      {scatterMeta?.insights && (
        <div className="glass-panel" style={{ padding: 24, marginTop: 24, borderLeft: '4px solid var(--kmk-cyan)' }}>
          <h3 style={{ margin: 0, marginBottom: 8, color: 'var(--kmk-navy)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={20} color="var(--kmk-cyan)"/> Insight Analisis Casemix
          </h3>
          <p style={{ margin: 0, color: 'var(--text-main)', lineHeight: '1.6' }}>
            Dari total populasi <strong>{scatterMeta.insights.total_rs?.toLocaleString('id-ID')}</strong> Fasilitas Kesehatan di seluruh Indonesia, 
            rata-rata nasional Casemix Index (CMI) berada di angka <strong>{scatterMeta.boundaries.mean_cmi?.toFixed(2)}</strong>. 
            Secara statistik, terdapat <strong>{scatterMeta.insights.outlier_2sd_count} RS</strong> yang menembus batas kewajaran 2SD (Standar Deviasi) dan 
            <strong> {scatterMeta.insights.outlier_iqr_count} RS</strong> menembus batas IQR. Rumah Sakit yang berada di area batas luar ini dikategorikan sebagai <em>Outlier</em> (warna merah/oranye pada grafik di atas) dan direkomendasikan untuk ditarik sebagai sampel Audit pada tahap berikutnya.
          </p>
        </div>
      )}

      {scatter && scatter.length > 0 && (
        <div className="glass-panel" style={{ padding: 24, marginTop: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ margin: 0, color: 'var(--kmk-navy)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Building size={20} color="var(--kmk-cyan)" /> Data Seluruh Rumah Sakit
            </h3>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Menampilkan {scatter.length} Fasilitas Kesehatan</div>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{width: 50}}>No</th>
                  <th style={{width: 100}}>Kode RS</th>
                  <th>Nama RS</th>
                  <th style={{width: 80, textAlign: 'center'}}>Kelas</th>
                  <th style={{width: 100, textAlign: 'right'}}>Total Kasus</th>
                  <th style={{width: 100, textAlign: 'right'}}>Rata-rata CMI</th>
                  <th style={{width: 100, textAlign: 'right'}}>Rata-rata ALOS</th>
                  <th style={{width: 150}}>Status Outlier</th>
                </tr>
              </thead>
              <tbody>
                {scatter.map((rs, idx) => (
                  <tr key={idx}>
                    <td>{idx + 1}</td>
                    <td>{rs.kode_rs}</td>
                    <td style={{fontWeight: 500}}>{rs.nama_rs}</td>
                    <td style={{textAlign: 'center'}}>{rs.kelas || '-'}</td>
                    <td style={{textAlign: 'right'}}>{rs.z.toLocaleString('id-ID')}</td>
                    <td style={{textAlign: 'right', fontWeight: 600}}>{rs.x.toFixed(4)}</td>
                    <td style={{textAlign: 'right'}}>{rs.y.toFixed(2)}</td>
                    <td>
                      <span style={{
                        padding: '4px 8px', borderRadius: 4, fontSize: 12, fontWeight: 600,
                        backgroundColor: rs.status.includes('Outlier') ? '#fee2e2' : '#e0f2fe',
                        color: rs.status.includes('Outlier') ? '#991b1b' : '#075985'
                      }}>
                        {rs.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
