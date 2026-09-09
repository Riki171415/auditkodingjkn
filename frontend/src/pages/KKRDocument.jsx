import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import KKRForm from './KKRForm';
import KKROSForm from './KKROSForm';

// Preview and download use the exact same generator, not a second HTML template.
export default function KKRDocument({ kind = 'DR01' }) {
  const Editor = kind === 'OS01' ? KKROSForm : KKRForm;
  const { sep } = useParams();
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [missing, setMissing] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    let objectUrl;
    setLoading(true); setError(''); setMissing(false); setUrl('');
    axios.get(`/api/outputs/kkr/${kind}/${encodeURIComponent(sep)}?inline=1`, {
      responseType: 'blob', signal: controller.signal, timeout: 60000,
    }).then(res => {
      objectUrl = URL.createObjectURL(res.data);
      setUrl(objectUrl);
    }).catch(err => {
      if (axios.isCancel(err)) return;
      if (err.response?.status === 404) setMissing(true);
      else setError('Dokumen belum berhasil dimuat. Silakan coba lagi.');
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => { controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [sep, revision, kind]);
  if (editing || missing) return <>
    <p className="no-print">{missing ? 'Simpan formulir untuk membuat dokumen KKR.' : kind === 'DR01' ? 'Simpan perubahan, lalu buka pratinjau untuk melihat PDF terbaru.' : 'Simpan perubahan formulir sebelum membuat ulang dokumen.'}</p>
    <button className="btn btn-outline no-print" onClick={() => { setEditing(false); setMissing(false); setRevision(r => r + 1); }}>Lihat pratinjau PDF</button>
    <Editor key={sep} />
  </>;
  return <div>
    <div className="kkr-actions no-print">
      <button className="btn btn-outline" onClick={() => window.history.back()}>Kembali</button>
      <button className="btn btn-primary" onClick={() => setEditing(true)}>Edit formulir</button>
      {url && <a className="btn btn-outline" href={url} download={`KKR-${kind}_${sep}.pdf`}>Unduh PDF</a>}
    </div>
    <p style={{margin: '12px 0'}}>{kind === 'DR01' ? 'KKR-DR01 • Hasil validasi otomatis. Tampilan dan unduhan menggunakan dokumen yang sama dari data terakhir tersimpan. Rincian lengkap tersedia pada lampiran.' : 'KKR-OS01 dari hasil generate tersimpan.'}</p>
    {loading && <p role="status">Memuat dokumen KKR…</p>}
    {error && <div role="alert">{error} <button className="btn btn-outline" onClick={() => setRevision(r => r + 1)}>Coba lagi</button></div>}
    {url && <iframe title={`KKR-${kind} hasil generate`} src={`${url}#view=FitH`} style={{width: '100%', height: '85vh', border: '1px solid #9bbacb', background: '#edf3f5'}} />}
  </div>;
}
