import { useState, useEffect } from 'react';
import { Activity, Building, FileSpreadsheet, AlertTriangle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from 'recharts';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [scatter, setScatter] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get('/api/dashboard/stats'),
      axios.get('/api/dashboard/scatter')
    ]).then(([resStats, resScatter]) => {
      setStats(resStats.data.data);
      setScatter(resScatter.data.data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

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
  if (!stats) return <div>Gagal memuat data</div>;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '24px', margin: 0 }}>Tahap 1: Analisis Casemix (Dashboard)</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>Gambaran umum populasi klaim dan identifikasi Rumah Sakit anomali</p>
        </div>
        <Link to="/hospitals" className="btn btn-primary">
          Lanjut Tahap 2: Penetapan Sasaran <ArrowRight size={16} />
        </Link>
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
              <ZAxis type="number" dataKey="z" range={[20, 400]} name="Volume Kasus" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
              <Scatter name="Rumah Sakit" data={scatter} opacity={0.8} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
