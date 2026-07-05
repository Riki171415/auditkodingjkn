# Konfigurasi WSGI untuk PythonAnywhere
import sys
import os

# 1. Sesuaikan path ini dengan folder aplikasi Anda di PythonAnywhere
# Contoh: '/home/username/audit-app'
project_home = u'/home/GANTI_DENGAN_USERNAME_ANDA/audit-app'

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 2. Set environment variable jika diperlukan
# os.environ['FLASK_ENV'] = 'production'

# 3. Import aplikasi Flask Anda
# Asumsikan aplikasi Flask Anda ada di app.py dan bernama 'app'
from app import app as application
