import json
from docx import Document

def clear_table_rows(table):
    # Keep header (row 0), delete the rest
    # python-docx doesn't have an easy way to delete rows, so we remove the XML element
    for row in table.rows[1:]:
        table._tbl.remove(row._tr)

def test_update():
    doc = Document('Template_Laporan_RS.docx')
    with open('exports/agent_outputs/data_review/data_review_1275655.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    dr_data = metadata.get('dr_data', [])
    
    # Table 1: Lampiran 1
    t1 = doc.tables[1]
    clear_table_rows(t1)
    
    for i, d in enumerate(dr_data, 1):
        row = t1.add_row()
        cells = row.cells
        cells[0].text = str(i)
        cells[1].text = str(d.get('nomor_sep', ''))
        cells[2].text = str(d.get('ina_cbg', ''))
        cells[3].text = str(d.get('idrg', ''))
        skor = d.get('skor_knavp', 0.0)
        # Sesuai request: jangan tulis 1.0, tulis 1
        cells[4].text = str(int(skor)) if skor == int(skor) else str(skor)
        cells[5].text = str(d.get('tingkat_risiko', ''))
        cells[6].text = str(len(d.get('triggered_rules', [])))
        cells[7].text = str(d.get('mismatch_count', 0))
        cells[8].text = str(d.get('keputusan', ''))

    print("Table 1 updated. New rows:", len(t1.rows))

if __name__ == '__main__':
    test_update()
