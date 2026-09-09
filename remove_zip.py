import sys

def remove_zip():
    with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/scripts/package_final_reports.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    idx = content.find("zip_path = BASE")
    if idx != -1:
        new_content = content[:idx] + "print('SELESAI. File ZIP tidak dibuat sesuai permintaan user.')\n"
        with open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/scripts/package_final_reports.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Success")
    else:
        print("Could not find ZIP block")

if __name__ == '__main__':
    remove_zip()
