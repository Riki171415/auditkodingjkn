import { useEffect, useState } from 'react';
import axios from 'axios';

export default function OutputLibrary() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    axios.get('/api/outputs', {signal: controller.signal})
      .then(res => setItems(res.data.data))
      .catch(err => { if (!axios.isCancel(err)) setError('Daftar outputs gagal dimuat. Muat ulang halaman untuk mencoba lagi.'); });
    return () => controller.abort();
  }, []);
  const filtered = items.filter(item => item.path.toLowerCase().includes(search.toLowerCase()));
  return <section className="glass-panel" style={{padding: 20, marginBottom: 24}}>
    <h2>Dokumen hasil generate (outputs)</h2>
    <p>Unduh file asli dari folder outputs. PDF KKR per SEP tersedia di halaman KKR.</p>
    <input aria-label="Cari dokumen outputs" placeholder="Cari nama RS, file, atau folder…" value={search} onChange={e => setSearch(e.target.value)} style={{width: '100%', padding: 10, margin: '12px 0'}} />
    {error && <p role="alert">{error}</p>}
    <div style={{maxHeight: 320, overflow: 'auto'}}>
      {filtered.slice(0, 100).map(item => <div key={item.path} style={{padding: '8px 0', borderBottom: '1px solid #ddd', overflowWrap: 'anywhere'}}>
        <a href={`/api/outputs/file/${item.path.split('/').map(encodeURIComponent).join('/')}`}>{item.filename}</a>
        <div style={{fontSize: 11, color: '#64748b'}}>{item.path}</div>
      </div>)}
    </div>
    <small>{filtered.length} dokumen; maksimal 100 ditampilkan. Gunakan pencarian untuk mempersempit.</small>
  </section>;
}
