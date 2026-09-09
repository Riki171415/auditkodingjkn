def fix_qr_import():
    with open('generate_laporan_akhir_nasional.py', 'r', encoding='utf-8') as f:
        content = f.read()
    bad_import = "from modules.export_generator import generate_custom_qr_bytes, QR_AVAILABLE, PIL_AVAILABLE"
    good_import = "from modules.export_generator import generate_qr_image_bytes as generate_custom_qr_bytes, QR_AVAILABLE, PIL_AVAILABLE"
    
    if bad_import in content:
        content = content.replace(bad_import, good_import)
        with open('generate_laporan_akhir_nasional.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Import fixed!")
    else:
        print("Import not found!")

if __name__ == '__main__':
    fix_qr_import()
