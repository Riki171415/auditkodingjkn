from docx import Document
import os

doc = Document('Template_Laporan_RS.docx')
found = False
to_remove = []

for el in doc.element.body:
    if found:
        to_remove.append(el)
    else:
        # Instead of el.text which might not exist on all elements, 
        # we check xml text
        if '{KONTEN_LAPORAN}' in el.xml:
            found = True

for el in to_remove:
    el.getparent().remove(el)

doc.save('exports/word_reports/test_del.docx')
print("Done")
