import os
import json
import pandas as pd
from datetime import datetime
from modules.db_manager import get_recap_desk_review
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports', 'rekap')

def generate_recap_excel():
    print("Mengambil data Desk Review dari database...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    dr_data = get_recap_desk_review()
    print(f"Ditemukan {len(dr_data)} data Desk Review.")
    
    if not dr_data:
        print("Data kosong. Tidak ada yang diekspor.")
        return None
        
    master_data = []
    for row in dr_data:
        try:
            form_data = json.loads(row.get('tindakan_reviewer') or '{}')
        except:
            form_data = {}
            
        tarif_ina = float(row.get('tarif_inacbg') or 0)
        tarif_rs = float(row.get('tarif_rs') or 0)
        selisih = tarif_ina - tarif_rs
        
        master_data.append({
            'Nomor SEP': row.get('sep'),
            'Kode RS': row.get('kode_rs'),
            'Nama RS': row.get('nama_rs'),
            'Kelas RS': row.get('kelas'),
            'Regional': row.get('regional'),
            'Reviewer': row.get('reviewer_name') or form_data.get('reviewer') or 'System',
            'Tanggal Review': str(row.get('updated_at'))[:10] if row.get('updated_at') else form_data.get('tanggal_review'),
            'Kode INA-CBG': row.get('inacbg'),
            'Tarif INA-CBG': tarif_ina,
            'Tarif RS (Standar)': tarif_rs,
            'Selisih Tarif (Rp)': selisih,
            'Keputusan Reviewer': form_data.get('keputusan_reviewer', 'Belum Direview'),
            'Kategori Perubahan Tarif': form_data.get('kategori_perubahan_tarif', '-'),
            'Analisis / Alasan': form_data.get('analisis_reviewer', '-'),
            'Tingkat Keyakinan': form_data.get('tingkat_keyakinan', '-'),
            'Rekomendasi Lanjut': form_data.get('rekomendasi_lanjut', '-')
        })
        
    df_master = pd.DataFrame(master_data)
    
    # Buat Sheet 2: Ringkasan per RS
    print("Menyusun ringkasan agregat per Rumah Sakit...")
    summary_data = []
    
    # Group by RS
    for rs_code, group in df_master.groupby('Kode RS'):
        rs_name = group['Nama RS'].iloc[0]
        total_kasus = len(group)
        sesuai = len(group[group['Keputusan Reviewer'] == 'Sesuai (Terbukti Valid)'])
        tidak_sesuai = len(group[group['Keputusan Reviewer'] == 'Tidak Sesuai (Terindikasi Fraud/Error)'])
        belum_direview = total_kasus - sesuai - tidak_sesuai
        
        total_selisih_rs = group['Selisih Tarif (Rp)'].sum()
        
        summary_data.append({
            'Kode RS': rs_code,
            'Nama RS': rs_name,
            'Total Kasus Audit': total_kasus,
            'Kasus Sesuai (Valid)': sesuai,
            'Kasus Tidak Sesuai': tidak_sesuai,
            'Belum Direview': belum_direview,
            'Total Potensi Selisih Tarif (Rp)': total_selisih_rs
        })
        
    df_summary = pd.DataFrame(summary_data)
    
    filename = f"Laporan_Akhir_Desk_Review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    print(f"Menyimpan ke Excel: {filename}...")
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Ringkasan Eksekutif', index=False)
        df_master.to_excel(writer, sheet_name='Master Data (Rincian)', index=False)
        
        # Styling
        workbook = writer.book
        
        header_fill = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                             top=Side(style='thin'), bottom=Side(style='thin'))
        
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            # Format Headers
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border
            
            # Format currency columns and borders
            for row in worksheet.iter_rows(min_row=2):
                for cell in row:
                    cell.border = thin_border
                    if isinstance(cell.value, (int, float)) and cell.value > 1000:
                        cell.number_format = '#,##0'
            
            # Auto-adjust column widths
            for col in worksheet.columns:
                max_length = 0
                col_letter = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)
                
    print(f"SELESAI! Laporan akhir berhasil disimpan di: {filepath}")
    return filepath

if __name__ == '__main__':
    generate_recap_excel()
