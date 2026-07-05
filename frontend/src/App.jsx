import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Building2, ClipboardCheck, BriefcaseMedical, FileText } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Hospitals from './pages/Hospitals';
import DeskReview from './pages/DeskReview';
import KKRForm from './pages/KKRForm';

function Sidebar() {
  const location = useLocation();
  const path = location.pathname;

  return (
    <div className="sidebar" style={{ width: 280 }}>
      <div className="sidebar-logo">
        <h2 style={{ color: 'white', margin: 0, fontSize: '18px' }}>Pusat Pembiayaan</h2>
        <div style={{ color: 'var(--kmk-cyan)', fontSize: '12px', fontWeight: 600 }}>KEMENTERIAN KESEHATAN RI</div>
        <div style={{ marginTop: '16px', fontSize: '11px', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase' }}>
          Tahapan Audit Koding 2025
        </div>
      </div>

      <div style={{ padding: '0 24px 8px', fontSize: 11, color: 'var(--kmk-cyan)', fontWeight: 600, marginTop: 16 }}>FASE PERSIAPAN</div>
      <Link to="/" className={`nav-item ${path === '/' ? 'active' : ''}`}>
        <LayoutDashboard size={16} /> 1. Analisis Casemix (Scatter)
      </Link>
      <Link to="/hospitals" className={`nav-item ${path.includes('/hospitals') ? 'active' : ''}`}>
        <Building2 size={16} /> 2. Penetapan Sasaran RS
      </Link>
      
      <div style={{ padding: '0 24px 8px', fontSize: 11, color: 'var(--kmk-cyan)', fontWeight: 600, marginTop: 24 }}>FASE PELAKSANAAN</div>
      <Link to="/desk-review-all" className={`nav-item ${path.includes('/desk-review') || path.includes('/kkr-dr01') ? 'active' : ''}`}>
        <ClipboardCheck size={16} /> 3. Desk Review (KKR-DR01)
      </Link>
      <Link to="/onsite-audit" className={`nav-item ${path.includes('/onsite-audit') ? 'active' : ''}`}>
        <BriefcaseMedical size={16} /> 4. On-Site Audit (KKR-OS01)
      </Link>

      <div style={{ padding: '0 24px 8px', fontSize: 11, color: 'var(--kmk-cyan)', fontWeight: 600, marginTop: 24 }}>FASE FINALISASI</div>
      <Link to="/laporan" className={`nav-item ${path === '/laporan' ? 'active' : ''}`}>
        <FileText size={16} /> 5. Rekonsiliasi & Laporan
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
          <Route path="/desk-review-all" element={<div className="glass-panel fade-in" style={{padding: 24}}><h2>Tahap 3: Pelaksanaan Desk Review</h2><p>Pilih Rumah Sakit di menu Tahap 2 untuk memulai Desk Review kasusnya.</p></div>} />
          <Route path="/desk-review/:kode_rs" element={<DeskReview />} />
          <Route path="/kkr-dr01/:sep" element={<KKRForm />} />
          <Route path="/onsite-audit" element={<div className="glass-panel fade-in" style={{padding: 24}}><h2>Tahap 4: On-Site Audit</h2><p>Daftar kasus yang direkomendasikan On-Site Audit berdasarkan tingkat keparahan (High). Segera hadir...</p></div>} />
          <Route path="/laporan" element={<div className="glass-panel fade-in" style={{padding: 24}}><h2>Tahap 5: Rekonsiliasi & Laporan Hasil Audit</h2><p>Mengekspor seluruh Kertas Kerja Reviewer ke format rekapitulasi akhir (Segera hadir...)</p></div>} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
