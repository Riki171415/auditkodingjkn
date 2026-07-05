import os
import json
import sqlite3
import zipfile

def main():
    print("Mengekstrak file laporan_lengkap.zip...")
    if not os.path.exists('laporan_lengkap.zip'):
        print("Error: laporan_lengkap.zip tidak ditemukan!")
        return
        
    os.makedirs('exports', exist_ok=True)
    with zipfile.ZipFile('laporan_lengkap.zip', 'r') as zip_ref:
        zip_ref.extractall('exports')
    print("Ekstraksi file berhasil!")
    
    print("Mengupdate database audit.db...")
    if not os.path.exists('reports_metadata.json'):
        print("Error: reports_metadata.json tidak ditemukan!")
        return
        
    with open('reports_metadata.json', 'r') as f:
        metadata = json.load(f)
        
    conn = sqlite3.connect('audit.db')
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS generated_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_type TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Import records
    count = 0
    for record in metadata:
        # Check if exists
        cursor.execute("SELECT id FROM generated_reports WHERE filename = ?", (record['filename'],))
        if cursor.fetchone():
            continue
            
        cursor.execute(
            "INSERT INTO generated_reports (report_type, filename, file_path, created_at) VALUES (?, ?, ?, ?)",
            (record['report_type'], record['filename'], record['file_path'], record['created_at'])
        )
        count += 1
        
    conn.commit()
    conn.close()
    
    print(f"Selesai! {count} record laporan berhasil ditambahkan ke database.")
    print("Sekarang Anda bisa me-reload web app di PythonAnywhere!")

if __name__ == '__main__':
    main()
