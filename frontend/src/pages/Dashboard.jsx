import { useState, useEffect } from 'react';
import { Activity, Building, FileSpreadsheet, AlertTriangle } from 'lucide-react';
import axios from 'axios';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/dashboard/stats')
      .then(res => {
        setStats(res.data.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="fade-in"><div className="spinner" style={{width:24,height:24,border:'3px solid var(--kmk-cyan)',borderTopColor:'transparent',borderRadius:'50%'}}></div></div>;
  if (!stats) return <div>Gagal memuat data</div>;

  return (
    <div className="fade-in">
      <h1 className="text-gradient" style={{ marginBottom: 24, fontSize: '28px' }}>Executive Summary Dashboard</h1>
      
      <div className="grid-cards">
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            <Activity size={20} color="var(--kmk-cyan)" /> Total Kasus INA-CBG
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--kmk-navy)' }}>
            {stats.total_kasus.toLocaleString('id-ID')}
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            <Building size={20} color="var(--kmk-cyan)" /> RS Sampel Audit
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--kmk-navy)' }}>
            {stats.total_rs.toLocaleString('id-ID')}
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            <FileSpreadsheet size={20} color="var(--kmk-green)" /> RS Audit 2SD
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--kmk-green)' }}>
            {stats.audit_2sd ? stats.audit_2sd.toLocaleString('id-ID') : '0'}
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            <AlertTriangle size={20} color="var(--kmk-red)" /> RS Audit IQR
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--kmk-red)' }}>
            {stats.audit_iqr ? stats.audit_iqr.toLocaleString('id-ID') : '0'}
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: 24, minHeight: 300 }}>
        <h3 style={{ marginBottom: 16 }}>Grafik Distribusi Kasus (Placeholder BI)</h3>
        <div style={{ display: 'flex', height: 200, alignItems: 'flex-end', gap: 16, borderBottom: '1px solid var(--border-color)', paddingBottom: 16 }}>
          {/* Simple CSS Bar Chart Mockup for BI feel */}
          <div style={{ flex: 1, background: 'var(--kmk-cyan)', height: '100%', borderRadius: '4px 4px 0 0', opacity: 0.8 }}></div>
          <div style={{ flex: 1, background: 'var(--kmk-navy)', height: '70%', borderRadius: '4px 4px 0 0', opacity: 0.8 }}></div>
          <div style={{ flex: 1, background: 'var(--kmk-green)', height: '85%', borderRadius: '4px 4px 0 0', opacity: 0.8 }}></div>
          <div style={{ flex: 1, background: 'var(--kmk-yellow)', height: '40%', borderRadius: '4px 4px 0 0', opacity: 0.8 }}></div>
          <div style={{ flex: 1, background: 'var(--kmk-red)', height: '60%', borderRadius: '4px 4px 0 0', opacity: 0.8 }}></div>
        </div>
      </div>
    </div>
  );
}
