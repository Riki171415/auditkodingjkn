import os
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'exports', 'kkr_forms')
DEST_DIR = os.path.join(BASE_DIR, 'exports', 'Form_KKR_PDF_Per_RS')
ZIP_PATH = os.path.join(BASE_DIR, 'exports', 'Form_KKR_PDF_Per_RS.zip')

def package_only_pdfs():
    print("=" * 60)
    print("Membuat paket folder & ZIP khusus PDF per Rumah Sakit...")
    print("=" * 60)

    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
    os.makedirs(DEST_DIR, exist_ok=True)

    rs_folders = [f for f in os.listdir(SRC_DIR) if os.path.isdir(os.path.join(SRC_DIR, f))]
    print(f"Ditemukan {len(rs_folders)} folder Rumah Sakit.")

    total_pdfs = 0
    for rs_folder in rs_folders:
        src_rs_path = os.path.join(SRC_DIR, rs_folder)
        dest_rs_path = os.path.join(DEST_DIR, rs_folder)
        
        # Cari file PDF saja
        pdfs = [f for f in os.listdir(src_rs_path) if f.lower().endswith('.pdf')]
        if pdfs:
            os.makedirs(dest_rs_path, exist_ok=True)
            for pdf_file in pdfs:
                shutil.copy2(os.path.join(src_rs_path, pdf_file), os.path.join(dest_rs_path, pdf_file))
                total_pdfs += 1

    print(f"Berhasil menyalin {total_pdfs} berkas PDF ke: {DEST_DIR}")

    print("Membuat arsip ZIP...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DEST_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, os.path.join(BASE_DIR, 'exports'))
                zipf.write(abs_path, arcname=rel_path)

    print(f"SELESAI! Arsip ZIP tersimpan di: {ZIP_PATH}")

if __name__ == '__main__':
    package_only_pdfs()
