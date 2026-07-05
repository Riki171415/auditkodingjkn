import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'data.db')

def import_new_data():
    csv_path = r'D:\KERJAAN PUSBIKES\Audit Koding 2025\Data Individual 40 RS Audit.csv'
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found at {csv_path}")
        return
        
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path, dtype=str)
    print(f"Loaded {len(df)} rows.")
    
    # Rename columns to match what the backend expects
    column_mapping = {
        'KODE_RS': 'kode_rs',
        'NAMA_PPK': 'nama_rs',
        'KELAS': 'kelas',
        'NAMA_PROP': 'nama_prop',
        'REGIONAL': 'regional',
        'PEMILIK': 'pemilik',
        'PTD': 'jumlah_kasus',
        'SEP': 'sep',
        'discharge_date': 'discharge_date',
        'los': 'alos',
        'kelas_rawat': 'kelas_rawat',
        'inacbg': 'inacbg',
        'deskripsi_inacbg': 'deskripsi_inacbg',
        'Total_Tarif': 'tarif_inacbg',
        'Tarif_rs': 'tarif_rs',
        'idrg_drg_code': 'idrg_code',
        'idrg_drg_description': 'deskripsi_idrg',
    }
    
    df = df.rename(columns=column_mapping)
    
    # The file now contains true 'diaglist' and 'proclist' for INA-CBG.
    # Map the iDRG lists to their respective idrg columns.
    df['diaglist_idrg'] = df['idrg_diag_lists']
    df['proclist_idrg'] = df['idrg_proc_lists']
    
    # Ensure all missing values are empty strings instead of NaN
    df = df.fillna('')
    
    # Format tarif to numeric for DB consistency if possible
    df['tarif_inacbg'] = pd.to_numeric(df['tarif_inacbg'], errors='coerce').fillna(0)
    df['tarif_rs'] = pd.to_numeric(df['tarif_rs'], errors='coerce').fillna(0)
    
    # Save to SQLite
    print("Saving to data.db...")
    conn = sqlite3.connect(db_path)
    df.to_sql('individual_data', conn, index=False, if_exists='replace')
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ind_kode_rs ON individual_data(kode_rs)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ind_sep ON individual_data(sep)")
    
    conn.commit()
    conn.close()
    
    db_size = os.path.getsize(db_path) / (1024 * 1024)
    print(f"Success! DB size: {db_size:.2f} MB")

if __name__ == '__main__':
    import_new_data()
