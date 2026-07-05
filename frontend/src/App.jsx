import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Building2, ClipboardCheck, FileText } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Hospitals from './pages/Hospitals';
import DeskReview from './pages/DeskReview';
import KKRForm from './pages/KKRForm';

function Sidebar() {
  const location = useLocation();
  const path = location.pathname;

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <h2 style={{ color: 'white', margin: 0, fontSize: '18px' }}>Pusat Pembiayaan</h2>
        <div style={{ color: 'var(--kmk-cyan)', fontSize: '12px', fontWeight: 600 }}>KEMENTERIAN KESEHATAN RI</div>
        <div style={{ marginTop: '16px', fontSize: '11px', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase' }}>
          Audit Koding 2025
        </div>
      </div>

      <Link to="/" className={`nav-item ${path === '/' ? 'active' : ''}`}>
        <LayoutDashboard size={18} /> Dashboard
      </Link>
      <Link to="/hospitals" className={`nav-item ${path.includes('/hospitals') || path.includes('/desk-review') ? 'active' : ''}`}>
        <Building2 size={18} /> Desk Review (RS)
      </Link>
      <Link to="/laporan" className={`nav-item ${path === '/laporan' ? 'active' : ''}`}>
        <FileText size={18} /> Laporan & Rekap
      </Link>
    </div>
  );
}

function Layout({ children }) {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        {children}
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/hospitals" element={<Hospitals />} />
          <Route path="/desk-review/:kode_rs" element={<DeskReview />} />
          <Route path="/kkr-dr01/:sep" element={<KKRForm />} />
          <Route path="/laporan" element={<div className="glass-panel" style={{padding: 24}}><h2>Laporan & Rekapitulasi</h2><p>Segera hadir...</p></div>} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
