import os
import csv
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DB = os.path.join(BASE_DIR, 'data.db')
AUDIT_DB = os.path.join(BASE_DIR, 'audit.db')
CSV_FILE = r"D:\KERJAAN PUSBIKES\Audit Koding 2025\Hasil Penarikan Sample Audit Koding 2025_iDRG_Ujicoba - bq-results-20260723-172134-1784827707386.csv"

def import_csv():
    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found at {CSV_FILE}")
        return

    print("Connecting to data.db...")
    conn_data = sqlite3.connect(DATA_DB)
    cursor_data = conn_data.cursor()

    print("Truncating individual_data table...")
    cursor_data.execute("DELETE FROM individual_data")
    conn_data.commit()

    print("Connecting to audit.db...")
    conn_audit = sqlite3.connect(AUDIT_DB)
    cursor_audit = conn_audit.cursor()
    print("Truncating kkr_dr01 and kkr_os01 tables...")
    cursor_audit.execute("DELETE FROM kkr_dr01")
    cursor_audit.execute("DELETE FROM kkr_os01")
    conn_audit.commit()

    print(f"Reading CSV from {CSV_FILE}...")
    inserted = 0
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            # Map CSV columns to DB schema
            mapped_row = (
                row.get('kode_rs_clean') or row.get('kode_rs', ''),
                row.get('nama_ppk_clean', ''),
                '', # nama_prop
                '', # NAMA_KAB
                row.get('kelas_rs', ''),
                '', # regional
                row.get('kepemilikan_rs', ''),
                1,  # jumlah_kasus
                row.get('sep', ''),
                row.get('nama_pasien', ''),
                row.get('sex', ''),
                row.get('birth_date', ''),
                row.get('admission_date', ''),
                row.get('discharge_date', ''),
                row.get('los', ''),
                row.get('kelas_rawat', ''),
                row.get('diaglist', ''),
                row.get('proclist', ''),
                row.get('inacbg', ''),
                row.get('deskripsi_inacbg', ''),
                float(row.get('tarif_inacbg') or 0),
                float(row.get('tarif_rs') or 0),
                row.get('idrg_drg_code', ''),
                row.get('idrg_drg_description', ''),
                row.get('idrg_diag_lists', ''),
                row.get('idrg_proc_lists', ''),
                row.get('idrg_diag_lists', ''),
                row.get('idrg_proc_lists', '')
            )
            batch.append(mapped_row)

            if len(batch) >= 1000:
                cursor_data.executemany('''
                    INSERT INTO individual_data (
                        kode_rs, nama_rs, nama_prop, NAMA_KAB, kelas, regional, pemilik, jumlah_kasus, 
                        sep, Nama_Pasien, SEX, Birth_date, admission_date, discharge_date, alos, kelas_rawat, 
                        diaglist, proclist, inacbg, deskripsi_inacbg, tarif_inacbg, tarif_rs, idrg_code, 
                        deskripsi_idrg, idrg_diag_lists, idrg_proc_lists, diaglist_idrg, proclist_idrg
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch)
                conn_data.commit()
                inserted += len(batch)
                batch = []

        if batch:
            cursor_data.executemany('''
                INSERT INTO individual_data (
                    kode_rs, nama_rs, nama_prop, NAMA_KAB, kelas, regional, pemilik, jumlah_kasus, 
                    sep, Nama_Pasien, SEX, Birth_date, admission_date, discharge_date, alos, kelas_rawat, 
                    diaglist, proclist, inacbg, deskripsi_inacbg, tarif_inacbg, tarif_rs, idrg_code, 
                    deskripsi_idrg, idrg_diag_lists, idrg_proc_lists, diaglist_idrg, proclist_idrg
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch)
            conn_data.commit()
            inserted += len(batch)

    conn_data.close()
    conn_audit.close()
    print(f"Successfully inserted {inserted} records into data.db individual_data.")
    print("Database cleared and repopulated successfully.")

if __name__ == "__main__":
    import_csv()
