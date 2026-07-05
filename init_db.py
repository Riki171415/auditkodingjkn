"""
Database Initialization Script
Converts the large CSV and Excel files into a smaller, indexed SQLite database
suitable for deployment on Render.com
"""
import pandas as pd
import sqlite3
import os
import sys

# Import Cochran from data_loader
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))
from data_loader import cochran_sample_size

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
    
    # 2. Load Individual Data
    csv_path = os.path.join(BASE_DIR, '..', 'Individual Data_RS Sampel Audit_INACBG_2025_20260704.csv')
    if not os.path.exists(csv_path):
        print(f"ERROR: Individual CSV file not found at {csv_path}")
        return
        
    print(f"Loading Individual data from {csv_path} to calculate Cochran sampling...")
    print("(This step reads the full 1.7M rows into RAM to sample it, reducing the DB size massively)")
    
    # Read entire CSV (since we need to sample per hospital)
    df_ind = pd.read_csv(csv_path, sep=',', dtype=str, on_bad_lines='skip')
    total_original = len(df_ind)
    
    print(f"Loaded {total_original} rows. Processing Cochran sampling per RS...")
    
    import hashlib
    
    sampled_dfs = []
    rs_groups = df_ind.groupby('kode_rs')
    
    for kode_rs, group in rs_groups:
        N = len(group)
        n = cochran_sample_size(N)
        
        # Deterministic seed based on kode_rs
        seed = int(hashlib.md5(str(kode_rs).encode()).hexdigest()[:8], 16) % (2**31)
        
        if n >= N:
            sampled_dfs.append(group)
        else:
            sampled_dfs.append(group.sample(n=n, random_state=seed))
            
    df_sampled = pd.concat(sampled_dfs, ignore_index=True)
    total_sampled = len(df_sampled)
    
    print(f"Sampling complete: reduced from {total_original} to {total_sampled} rows!")
    
    # Save to SQLite
    print("Saving sampled cases to SQLite...")
    df_sampled.to_sql('individual_data', conn, index=False, if_exists='replace')
    
    # Create Individual indexes
    print("Creating indexes...")
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
