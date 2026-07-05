"""
Database Initialization Script
Converts the large CSV and Excel files into a smaller, indexed SQLite database
suitable for deployment on Render.com
"""
import pandas as pd
import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def init_db():
    print("Starting database initialization for Render.com deployment...")
    
    db_path = os.path.join(BASE_DIR, 'data.db')
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}...")
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    
    # 1. Load CMI Data
    cmi_path = os.path.join(BASE_DIR, '..', 'V2_CMI_INACBG_2025_CLEAN_20260704.xlsx')
    if not os.path.exists(cmi_path):
        print(f"ERROR: CMI Excel file not found at {cmi_path}")
        return
        
    print(f"Loading CMI data from {cmi_path}...")
    df_cmi = pd.read_excel(cmi_path, dtype=str)
    
    # Save CMI to SQLite
    df_cmi.to_sql('cmi_data', conn, index=False, if_exists='replace')
    print(f"Saved {len(df_cmi)} CMI records to SQLite.")
    
    # Create CMI indexes
    conn.execute("CREATE INDEX idx_cmi_kode_rs ON cmi_data(kode_rs)")
    
    # 2. Load Individual Data (in chunks to save RAM)
    csv_path = os.path.join(BASE_DIR, '..', 'Individual Data_RS Sampel Audit_INACBG_2025_20260704.csv')
    if not os.path.exists(csv_path):
        print(f"ERROR: Individual CSV file not found at {csv_path}")
        return
        
    print(f"Loading Individual data from {csv_path} in chunks...")
    
    chunk_size = 50000
    total_rows = 0
    
    # First chunk creates table
    for i, chunk in enumerate(pd.read_csv(csv_path, sep=';', dtype=str, on_bad_lines='skip', chunksize=chunk_size)):
        if i == 0:
            chunk.to_sql('individual_data', conn, index=False, if_exists='replace')
        else:
            chunk.to_sql('individual_data', conn, index=False, if_exists='append')
        total_rows += len(chunk)
        print(f"  Processed {total_rows} rows...")
        
    print(f"Saved {total_rows} Individual records to SQLite.")
    
    # Create Individual indexes
    print("Creating indexes (this may take a minute)...")
    conn.execute("CREATE INDEX idx_ind_kode_rs ON individual_data(kode_rs)")
    conn.execute("CREATE INDEX idx_ind_sep ON individual_data(sep)")
    
    conn.commit()
    conn.close()
    
    db_size = os.path.getsize(db_path) / (1024 * 1024)
    print(f"\nDatabase initialization complete!")
    print(f"Database size: {db_size:.2f} MB")
    print(f"Location: {db_path}")
    print("\nNext steps for Render.com deployment:")
    print("1. Commit data.db to Git (or use Git LFS if > 100MB)")
    print("2. Make sure modules/data_loader.py is updated to use SQLite in production")

if __name__ == "__main__":
    init_db()
