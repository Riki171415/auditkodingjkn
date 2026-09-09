import os
import subprocess
import time
import sys

def run_all():
    print("==========================================================================")
    print("     MEMULAI BULK GENERATION AUDIT KODING DAN VERIFIKASI DUAL CODING     ")
    print("                    PUSAT PEMBIAYAAN KESEHATAN - 2026                     ")
    print("==========================================================================")
    start_all = time.time()

    # 1. Generate 2.001 KKR-DR01 Forms (PDF & Excel)
    print("\n[STEP 1/3] Memproses 2.001 Kasus KKR-DR01 (PDF & Excel Kertas Kerja)...")
    t0 = time.time()
    ret1 = subprocess.run([sys.executable, "-u", "generate_kkr_forms_fast.py"])
    print(f"--> Step 1 Selesai dalam {time.time() - t0:.1f} detik. (Exit code: {ret1.returncode})")

    # 2. Generate Word Laporan Hasil Audit (LHA) Per Rumah Sakit
    print("\n[STEP 2/3] Memproses Laporan Hasil Audit Word (.docx) Per Rumah Sakit...")
    t1 = time.time()
    ret2 = subprocess.run([sys.executable, "-u", "generate_word_reports.py"])
    print(f"--> Step 2 Selesai dalam {time.time() - t1:.1f} detik. (Exit code: {ret2.returncode})")

    # 3. Generate Laporan Akhir Nasional (.docx)
    print("\n[STEP 3/5] Memproses Laporan Akhir Audit Koding Nasional 2025 (.docx)...")
    t2 = time.time()
    ret3 = subprocess.run([sys.executable, "-u", "generate_laporan_akhir_nasional.py"])
    print(f"--> Step 3 Selesai dalam {time.time() - t2:.1f} detik. (Exit code: {ret3.returncode})")

    # 4. Generate Rekap Laporan Excel (.xlsx)
    print("\n[STEP 4/5] Memproses Rekapitulasi Laporan Akhir (Excel)...")
    t3 = time.time()
    ret4 = subprocess.run([sys.executable, "-u", "generate_recap_desk_review.py"])
    print(f"--> Step 4 Selesai dalam {time.time() - t3:.1f} detik. (Exit code: {ret4.returncode})")

    # 5. Pisahkan File PDF KKR
    print("\n[STEP 5/5] Memisahkan File PDF KKR ke folder khusus...")
    t4 = time.time()
    # Assume the script is in scratch dir, we will copy it to scripts/ or run it from scratch
    scratch_dir = os.path.join(os.environ.get('USERPROFILE', 'C:\\Users\\User'), '.gemini', 'antigravity', 'brain', 'b0b7275c-dfaf-4744-8993-7c4272e274e2', 'scratch')
    pdf_script = os.path.join(scratch_dir, 'separate_kkr_pdf.py')
    if os.path.exists(pdf_script):
        ret5 = subprocess.run([sys.executable, "-u", pdf_script])
        print(f"--> Step 5 Selesai dalam {time.time() - t4:.1f} detik. (Exit code: {ret5.returncode})")
    else:
        print(f"--> Step 5 Dilewati (Script {pdf_script} tidak ditemukan).")

    total_elapsed = time.time() - start_all
    print("\n==========================================================================")
    print(f"  SELURUH PROSES BULK GENERATION BERHASIL DISELESAIKAN DALAM {total_elapsed/60:.2f} MENIT!")
    print("  Semua file PDF & Excel tersimpan di : exports/kkr_forms/")
    print("  Semua file Word LHA tersimpan di     : exports/word_reports/")
    print("==========================================================================")

if __name__ == '__main__':
    run_all()
