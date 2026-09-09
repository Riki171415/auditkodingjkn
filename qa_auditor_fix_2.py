import os

file_path = "modules/export_generator.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "Oleh karena itu, ": "Sebagai implikasinya, ",
    "Oleh sebab itu, ": "Berdasarkan hal tersebut, ",
    "tahapan selanjutnya": "tahap lanjutan"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

file_path_2 = "generate_laporan_akhir_nasional.py"
with open(file_path_2, "r", encoding="utf-8") as f:
    content_2 = f.read()

for old, new in replacements.items():
    content_2 = content_2.replace(old, new)

with open(file_path_2, "w", encoding="utf-8") as f:
    f.write(content_2)

print("Second QA pass successful.")
