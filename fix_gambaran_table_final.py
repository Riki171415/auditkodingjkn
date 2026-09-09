def fix_table():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    bad_block = """    narasi_gb = (
        f"Berdasarkan data Kertas Kerja Review (KKR-DR01), total kasus sampel yang direviu "
        f"pada {rs_name} berjumlah {len(cases)} kasus, yang mencakup {rj_rs} kasus rawat jalan dan {ri_rs} kasus rawat inap. "
        f"Dari hasil analisis reviewer terhadap indikasi ketidaksesuaian pengodean, "
        f"terdapat {onsite} kasus yang direkomendasikan untuk pelaksanaan On-Site Audit, "
        f"dan {sampling} kasus untuk Audit Sampling / Klarifikasi Administratif. "
        f"Sisa {monitor} kasus lainnya dinyatakan lolos validasi tanpa catatan khusus."
    )
    add_p(narasi_gb, align=3, size_pt=12, space_after_pt=12)
    
    table_gb = document.add_table(rows=6, cols=2)
    gb_data = [
        ['Uraian', 'Jumlah'],
        ['Total Kasus Direview (Sampel)', str(len(cases))],
        ['Rawat Jalan', str(rj_rs)],
        ['Rawat Inap', str(ri_rs)],
        ['Rekomendasi On-Site Audit', str(onsite)],
        ['Rekomendasi Audit Sampling', str(sampling)]
    ]
    for i, row in enumerate(gb_data):
        table_gb.rows[i].cells[0].text = row[0]
        table_gb.rows[i].cells[1].text = row[1]
    format_table(table_gb, font_size_pt=12)
    add_p("", space_after_pt=12)"""

    good_block = """    sampel_rj = sum(1 for c in cases if str(c.get('inacbg', '')).endswith('-0'))
    sampel_ri = len(cases) - sampel_rj

    narasi_gb = (
        f"Berdasarkan hasil rekapitulasi data klaim {rs_name}, fasilitas kesehatan ini memiliki "
        f"total populasi sebanyak {total_rs:,} kasus. Dari populasi tersebut, ditarik sampel sebanyak "
        f"{len(cases)} kasus untuk dilakukan verifikasi melalui Kertas Kerja Review (KKR-DR01). "
        f"Setelah proses validasi selesai, didapatkan {onsite} kasus yang direkomendasikan untuk "
        f"pelaksanaan On-Site Audit, dan {sampling} kasus untuk Audit Sampling (Klarifikasi Administratif). "
        f"Sisa {monitor} kasus lainnya lolos validasi tanpa catatan khusus."
    )
    add_p(narasi_gb, align=3, size_pt=12, space_after_pt=12)
    
    table_gb = document.add_table(rows=4, cols=3)
    gb_data = [
        ['Uraian', 'Total Populasi Klaim RS', 'Sampel Direview'],
        ['Total Kasus', f"{total_rs:,}", f"{len(cases):,}"],
        ['Rawat Jalan', f"{rj_rs:,}", f"{sampel_rj:,}"],
        ['Rawat Inap', f"{ri_rs:,}", f"{sampel_ri:,}"]
    ]
    for i, row in enumerate(gb_data):
        table_gb.rows[i].cells[0].text = row[0]
        table_gb.rows[i].cells[1].text = row[1]
        table_gb.rows[i].cells[2].text = row[2]
        
    # Bold the header row
    for cell in table_gb.rows[0].cells:
        for p in cell.paragraphs:
            for run in p.runs:
                run.bold = True
                
    format_table(table_gb, font_size_pt=12)
    add_p("", space_after_pt=12)"""

    if bad_block in content:
        content = content.replace(bad_block, good_block)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Gambaran Data Table updated with population vs sample!")
    else:
        print("Bad block not found!")

if __name__ == '__main__':
    fix_table()
