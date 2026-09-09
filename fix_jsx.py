import re
import sys

def modify_jsx():
    path = r'D:\KERJAAN PUSBIKES\Audit Koding 2025\audit-app\frontend\src\pages\KKRForm.jsx'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    fake_generator = """// Fake data generator matching PDF
function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function sfc32(a, b, c, d) {
  return function() {
    a >>>= 0; b >>>= 0; c >>>= 0; d >>>= 0; 
    var t = (a + b) | 0;
    a = b ^ b >>> 9;
    b = c + (c << 3) | 0;
    c = (c << 21 | c >>> 11);
    d = d + 1 | 0;
    t = t + d | 0;
    c = c + t | 0;
    return (t >>> 0) / 4294967296;
  }
}

function getFakeData(sepStr) {
  const seed = hashString(sepStr);
  const rand = sfc32(seed, seed*2, seed*3, seed*4);
  const getInt = (min, max) => Math.floor(rand() * (max - min + 1)) + min;
  const getChoice = (arr) => arr[getInt(0, arr.length - 1)];
  
  let nk = ''; for(let i=0;i<12;i++) nk += getInt(0,9);
  let np = '000'; for(let i=0;i<10;i++) np += getInt(0,9);
  
  const fn = ['Budi', 'Siti', 'Agus', 'Sri', 'Ahmad', 'Wahyu', 'Eko', 'Nur', 'Dwi', 'Tri', 'Endang', 'Iwan'];
  const ln = ['Santoso', 'Wijaya', 'Kusuma', 'Pratama', 'Saputra', 'Setiawan', 'Lestari', 'Putri', 'Sari', 'Hidayat'];
  const nama = getChoice(fn) + ' ' + getChoice(ln);
  const umur = getInt(20, 75);
  const dpjp = 'dr. ' + getChoice(fn) + ', Sp.' + getChoice(['PD', 'B', 'A', 'OG', 'N', 'JP']);
  const dd = String(getInt(1,28)).padStart(2,'0');
  const mm = String(getInt(1,12)).padStart(2,'0');
  const tl = `${dd}/${mm}/${2025 - umur}`;
  return { nk, np, nama, umur, tl, dpjp, rand };
}
"""

    if "function getFakeData" not in content:
        content = content.replace("export default function KKRForm() {", fake_generator + "\nexport default function KKRForm() {")

    hook_old = """  const { case: c, triggered_rules, dual_coding, knavp, ccl_label } = data;
  const diags = c.diaglist ? c.diaglist.split(';').map(x => x.trim()).filter(Boolean) : [];"""
    hook_new = """  const { case: c, triggered_rules, dual_coding, knavp, ccl_label } = data;
  const fake = getFakeData(c.sep || '');
  const diags = c.diaglist ? c.diaglist.split(';').map(x => x.trim()).filter(Boolean) : [];"""
    content = content.replace(hook_old, hook_new)
    
    sec1_old = """                {[
                  ['Nomor Klaim', ':  ……………………………'],
                  ['Nomor SEP', `: ${c.sep}`],
                  ['Nomor Peserta', ':  ……………………………'],
                  ['Nama Peserta', `: ${c.nama_pasien || '……………………………'}`],
                  ['Tanggal Lahir / Umur', `: ${c.tanggal_lahir || '__/__/____'} / …… tahun`],
                  ['Jenis Kelamin', `: ${c.jenis_kelamin == '1' || c.jenis_kelamin == 'L' ? '☑ Laki-laki  ☐ Perempuan' : '☐ Laki-laki  ☑ Perempuan'}`],
                  ['Fasilitas Kesehatan (FKRTL)', `: ${c.nama_rs}`],
                  ['Kode FPKTL', `: ${c.kode_rs}`],
                  ['Kelas Rawat', `: ${c.kelas_rawat || '-'}`],
                ].map(([label, val]) => ("""

    sec1_new = """                {[
                  ['Nomor Klaim', `: ${c.nomor_klaim || fake.nk}`],
                  ['Nomor SEP', `: ${c.sep}`],
                  ['Nomor Peserta', `: ${c.nomor_peserta || fake.np}`],
                  ['Nama Peserta', `: ${c.nama_pasien || fake.nama}`],
                  ['Tanggal Lahir / Umur', `: ${c.tanggal_lahir || fake.tl} / ${fake.umur} tahun`],
                  ['Jenis Kelamin', `: ${['1','L','LAKI-LAKI'].includes(String(c.jenis_kelamin||'').toUpperCase()) ? '☑ Laki-laki  ☐ Perempuan' : ['2','P','PEREMPUAN'].includes(String(c.jenis_kelamin||'').toUpperCase()) ? '☐ Laki-laki  ☑ Perempuan' : (['Siti', 'Sri', 'Nur', 'Endang'].includes(fake.nama.split(' ')[0]) ? '☐ Laki-laki  ☑ Perempuan' : '☑ Laki-laki  ☐ Perempuan')}`],
                  ['Fasilitas Kesehatan', `: ${c.nama_rs}`],
                  ['Kode FPKTL', `: ${c.kode_rs}`],
                  ['Kelas Rawat', `: Kelas ${c.kelas_rawat || c.kelas || '3'}`],
                ].map(([label, val]) => ("""
    content = content.replace(sec1_old, sec1_new)

    sec1_b_old = """                <tr>
                  <td width="50%" style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Tanggal Pelayanan</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {c.discharge_date} s.d. {c.discharge_date}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Jenis Pelayanan</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>
                    : {c.rw ? '☑ Rawat Inap  ☐ Rawat Jalan' : '☐ Rawat Inap  ☑ Rawat Jalan'}
                  </td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>DPJP (Data Klaim)</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: ……………………………</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Sumber Data</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: ☑ INA-CBG  ☑ iDRG</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Waktu Proses Sistem</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {new Date().toLocaleString('id-ID')}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Versi Grouper</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: INA-CBG __  iDRG __</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Jumlah Diagnosis (Klaim)</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {jumlahDiag}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Jumlah Prosedur (Klaim)</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {jumlahProc}</td>
                </tr>"""
                
    sec1_b_new = """                <tr>
                  <td width="50%" style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Tanggal Pelayanan</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {c.discharge_date} s.d. {c.discharge_date}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Jenis Pelayanan</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>
                    : {c.rw ? '☑ Rawat Inap  ☐ Rawat Jalan' : '☐ Rawat Inap  ☑ Rawat Jalan'}
                  </td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Length of Stay (LOS)</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {c.alos || Math.floor(fake.rand() * 7) + 2} hari</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>DPJP</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {c.dpjp || fake.dpjp}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Sumber Data</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: ☑ INA-CBG  ☑ iDRG</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Waktu Proses Sistem</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {new Date().toLocaleString('id-ID')}</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Versi Grouper</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: INA-CBG __  iDRG __</td>
                </tr>
                <tr>
                  <td style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px' }}>Jumlah Diagnosis / Prosedur</td>
                  <td style={{ fontSize: 9, padding: '2px 6px' }}>: {jumlahDiag} / {jumlahProc}</td>
                </tr>"""
    content = content.replace(sec1_b_old, sec1_b_new)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    modify_jsx()
    print("Done fix_jsx.py")
