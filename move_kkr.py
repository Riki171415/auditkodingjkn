import os, shutil, glob
base = 'outputs/hasil_akhir_20260907'
src = os.path.join(base, 'form_kkr_per_rs')
pdf_dir = os.path.join(base, 'pdf_kkr_per_rs')
xl_dir = os.path.join(base, 'excel_kkr_per_rs')

for root, dirs, files in os.walk(src):
    for file in files:
        src_file = os.path.join(root, file)
        rel_path = os.path.relpath(root, src)
        if file.endswith('.pdf'):
            dst_folder = os.path.join(pdf_dir, rel_path)
            os.makedirs(dst_folder, exist_ok=True)
            shutil.move(src_file, os.path.join(dst_folder, file))
        elif file.endswith('.xlsx'):
            dst_folder = os.path.join(xl_dir, rel_path)
            os.makedirs(dst_folder, exist_ok=True)
            shutil.move(src_file, os.path.join(dst_folder, file))

shutil.rmtree(src)
print('Pemisahan folder selesai!')
