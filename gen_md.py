
import pickle
with open('rs_stats_dump.pkl', 'rb') as f:
    rs_stats = pickle.load(f)

print('## Lampiran B: Daftar Distribusi Keputusan per Rumah Sakit')
print('Tabel berikut menyajikan rincian akumulasi volume sampel per fasilitas kesehatan beserta hasil ajudikasi akhir (Keputusan Reviewer).\\n')
print('| No | Nama Rumah Sakit | Total Kasus | Lolos (Tidak Perlu Tindak Lanjut) | Direkomendasikan On-Site Audit |')
print('|:---|:---|---:|---:|---:|')

for i, rs in enumerate(rs_stats, 1):
    print('| ' + str(i) + ' | ' + str(rs['nama']) + ' | ' + str(rs['total']) + ' | ' + str(rs['lolos']) + ' | ' + str(rs['onsite']) + ' |')

