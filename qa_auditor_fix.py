import os

file_path = "modules/export_generator.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace literary/AI words with formal auditor terms
replacements = {
    "menyerap postur beban klaim": "memetakan distribusi beban klaim",
    "niscaya membawa risiko clerical error atau kesalahan input apabila kendali mutu rumah sakit tidak berjalan spartan": "secara inheren membawa risiko clerical error apabila kendali mutu internal tidak dilaksanakan secara optimal",
    "Membongkar struktur peringatan": "Mengevaluasi struktur peringatan",
    "ilusi kompleksitas kasus": "bias kompleksitas kasus",
    "menyingkap tabir bahwa": "mengindikasikan bahwa",
    "membedah rekam medis fisik": "memverifikasi rekam medis fisik",
    "Membongkar struktur peringatan (alerts) yang diterbitkan oleh sistem KNAVP": "Mengevaluasi struktur peringatan (alerts) yang diterbitkan oleh sistem KNAVP"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("QA Auditor fixes applied successfully.")
