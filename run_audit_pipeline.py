import os
import subprocess
import time
import sys

def run_all():
    print("==========================================================================")
    print("     MEMULAI PIPELINE AUDIT KODING KNAVP 2025                             ")
    print("==========================================================================")
    start_all = time.time()

    # STEP 1: Generate Data Audit ke Database
    print("\n[STEP 1/6] Generate Data Audit ke Database (generate_dummy_dr.py)...")
    t0 = time.time()
    ret1 = subprocess.run([sys.executable, "-u", "generate_dummy_dr.py"])
    print(f"--> Step 1 Selesai dalam {time.time() - t0:.1f} detik. (Exit code: {ret1.returncode})")

    # STEP 2: Generate Excel Rekap per RS
    print("\n[STEP 2/6] Generate Excel Rekap per RS (generate_excel_reports_per_rs.py)...")
    t1 = time.time()
    ret2 = subprocess.run([sys.executable, "-u", "generate_excel_reports_per_rs.py"])
    print(f"--> Step 2 Selesai dalam {time.time() - t1:.1f} detik. (Exit code: {ret2.returncode})")
    
    # STEP 2B: Generate Excel Rekap Nasional (generate_recap_desk_review.py)
    print("\n[STEP 3/6] Generate Excel Rekap Nasional (generate_recap_desk_review.py)...")
    t2b = time.time()
    ret2b = subprocess.run([sys.executable, "-u", "generate_recap_desk_review.py"])
    print(f"--> Step 3 Selesai dalam {time.time() - t2b:.1f} detik. (Exit code: {ret2b.returncode})")

    # STEP 3: Generate Word LHR per RS
    print("\n[STEP 4/6] Generate Word LHR per RS (generate_word_lhr_per_rs.py)...")
    t2 = time.time()
    ret3 = subprocess.run([sys.executable, "-u", "generate_word_lhr_per_rs.py"])
    print(f"--> Step 4 Selesai dalam {time.time() - t2:.1f} detik. (Exit code: {ret3.returncode})")

    # STEP 4: Generate PDF KKR-DR01 per Kasus
    print("\n[STEP 5/6] Generate PDF KKR-DR01 per Kasus (generate_kkr_forms_fast.py)...")
    t3 = time.time()
    ret4 = subprocess.run([sys.executable, "-u", "generate_kkr_forms_fast.py"])
    print(f"--> Step 5 Selesai dalam {time.time() - t3:.1f} detik. (Exit code: {ret4.returncode})")
    
    # STEP 5: Pisahkan PDF
    print("\n[STEP 5B/6] Pisahkan file PDF KKR...")
    t4 = time.time()
    pdf_script = "separate_kkr_pdf.py"
    if os.path.exists(pdf_script):
        ret5 = subprocess.run([sys.executable, "-u", pdf_script])
        print(f"--> Step 5B Selesai dalam {time.time() - t4:.1f} detik. (Exit code: {ret5.returncode})")
    else:
        print(f"--> Step 5B Dilewati (script tidak ditemukan).")

    # STEP 6: Generate Laporan Akhir Nasional
    print("\n[STEP 6/6] Generate Laporan Akhir Nasional (generate_laporan_akhir_nasional.py)...")
    t5 = time.time()
    ret6 = subprocess.run([sys.executable, "-u", "generate_laporan_akhir_nasional.py"])
    print(f"--> Step 6 Selesai dalam {time.time() - t5:.1f} detik. (Exit code: {ret6.returncode})")

    total_elapsed = time.time() - start_all
    print("\n==========================================================================")
    print(f"  SELURUH PROSES PIPELINE BERHASIL DISELESAIKAN DALAM {total_elapsed/60:.2f} MENIT!")
    print("==========================================================================")

if __name__ == '__main__':
    run_all()
