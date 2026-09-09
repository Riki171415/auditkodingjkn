import os
import glob
import shutil

kkr_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'kkr_forms')
pdf_only_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'kkr_forms_pdf_only')

if not os.path.exists(pdf_only_dir):
    os.makedirs(pdf_only_dir)

# Cari semua file PDF secara rekursif
pdf_files = glob.glob(os.path.join(kkr_dir, "**", "*.pdf"), recursive=True)
print(f"Menemukan {len(pdf_files)} file PDF untuk dipindahkan...")

moved_count = 0
for pdf in pdf_files:
    # Dapatkan nama folder RS (parent directory dari file pdf)
    rs_folder = os.path.basename(os.path.dirname(pdf))
    filename = os.path.basename(pdf)
    
    # Buat subfolder RS di dalam pdf_only_dir agar terstruktur rapi
    dest_rs_dir = os.path.join(pdf_only_dir, rs_folder)
    os.makedirs(dest_rs_dir, exist_ok=True)
    
    dest = os.path.join(dest_rs_dir, filename)
    shutil.move(pdf, dest)
    moved_count += 1
    
print(f"Selesai memindahkan {moved_count} file PDF ke: {pdf_only_dir} (beserta subfoldernya)")
