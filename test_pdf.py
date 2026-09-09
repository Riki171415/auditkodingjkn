import sys
sys.path.insert(0, './modules')
from report_pdf import export_saved_pdf
pdf_bytes = export_saved_pdf('0201R0011125V014938')
with open('scratch/new_test.pdf', 'wb') as f: f.write(pdf_bytes)
print('Created scratch/new_test.pdf')
