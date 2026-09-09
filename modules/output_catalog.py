"""Read-only access to generated deliverables inside outputs."""
from pathlib import Path
from functools import lru_cache
import time

ROOT = Path(__file__).resolve().parents[1] / 'outputs'

@lru_cache(maxsize=2)
def _catalog(bucket):
    records = []
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix.lower() in {'.pdf', '.docx', '.xlsx', '.zip'}:
            records.append({'path': path.relative_to(ROOT).as_posix(), 'filename': path.name,
                            'modified': path.stat().st_mtime})
    return sorted(records, key=lambda item: (item['modified'], item['path']), reverse=True)

def catalog():
    return _catalog(int(time.monotonic() // 30))

def resolve_output(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
        raise ValueError('Output tidak ditemukan')
    if path.suffix.lower() not in {'.pdf', '.docx', '.xlsx', '.zip'}:
        raise ValueError('Jenis output tidak didukung')
    return path

def find_kkr(sep, kind='DR01'):
    name = f'KKR-{kind}_{sep}.pdf'
    matches = [item for item in catalog() if item['filename'] == name]
    return resolve_output(matches[0]['path']) if matches else None
