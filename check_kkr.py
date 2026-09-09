import sys
sys.path.insert(0, '.')
from modules.report_pdf import export_saved_pdf
from modules.output_catalog import find_kkr
print('In catalog:', find_kkr('0201R0011125V014938'))

