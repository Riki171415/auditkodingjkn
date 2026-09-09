"""Package verified reports without including private intermediate snapshots."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import zipfile

BASE = Path(__file__).resolve().parents[1]
PDF = BASE / 'output/pdf/KKR_Per_RS_Terverifikasi_20260831'
REPORTS = BASE / 'outputs/rekonsiliasi_20260831'
DEST = BASE / 'outputs/Paket_Lengkap_KKR_dan_Rekap_20260831.zip'

def main():
    verification = json.loads((PDF / 'verifikasi_pdf.json').read_text(encoding='utf-8'))
    assert verification['status'] == 'PASS' and verification['case_count'] == 5206
    files = [(p, 'pdf_kkr_per_rs/' + p.name) for p in sorted(PDF.glob('*.pdf'))]
    for extension in ('*.xlsx', '*.docx'):
        files += [(p, 'laporan/' + p.relative_to(REPORTS).as_posix()) for p in sorted(REPORTS.rglob(extension))]
    counts = Counter(p.suffix for p, _ in files)
    assert counts == {'.pdf': 44, '.xlsx': 45, '.docx': 45}, counts
    for filename in ('BACA_DULU.txt', 'verifikasi_pdf.json', 'indeks_sep.json', 'temuan_pdf_lama.json'):
        files.append((PDF / filename, filename))
    files += [(REPORTS / 'DAFTAR_RS.txt', 'DAFTAR_RS.txt'), (REPORTS / 'verifikasi.json', 'verifikasi_word_excel.json')]
    manifest = {name: hashlib.sha256(path.read_bytes()).hexdigest() for path, name in files}
    with zipfile.ZipFile(DEST, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, name in files:
            archive.write(path, name)
        archive.writestr('manifest_sha256.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(DEST) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(files) + 1
        for name, digest in manifest.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    print(json.dumps({'status': 'PASS', 'reports': dict(counts), 'zip_bytes': DEST.stat().st_size, 'zip': str(DEST)}, indent=2))

if __name__ == '__main__':
    main()
