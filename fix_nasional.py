import re

with open('generate_laporan_akhir_nasional.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace add_p and add_list_item
new_funcs = """    def add_p(text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, bold=False, italic=False, size_pt=12, space_after_pt=6, left_indent_pt=0, hanging_indent=False):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after_pt)
        p.paragraph_format.line_spacing = 1.15
        if left_indent_pt > 0:
            p.paragraph_format.left_indent = Pt(left_indent_pt)
        if hanging_indent:
            p.paragraph_format.first_line_indent = Pt(-18)
            
        import re
        parts = re.split(r'(\*[^\*]+\*|\[\^[^\^\]]+\])', text)
        for part in parts:
            if not part: continue
            if part.startswith('*') and part.endswith('*'):
                run = p.add_run(part[1:-1])
                run.italic = True
                run.bold = bold
                run.font.name = 'Times New Roman'
                run.font.size = Pt(size_pt)
            elif part.startswith('[^') and part.endswith(']'):
                run = p.add_run(part[2:-1])
                run.font.superscript = True
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
            else:
                run = p.add_run(part)
                run.italic = italic
                run.bold = bold
                run.font.name = 'Times New Roman'
                run.font.size = Pt(size_pt)
        return p

    def add_list_item(text, num=None, bullet=False):
        prefix = "•" if bullet else f"{num}."
        return add_p(f"{prefix}\\t{text}", left_indent_pt=36, hanging_indent=True)"""

text = re.sub(r'    def add_p\(.*?return add_p\(f"\{prefix\}\{text\}", left_indent_pt=18\)', new_funcs, text, flags=re.DOTALL)

# Italicize words
words_to_italicize = [
    "clinical coding",
    "cost-effectiveness",
    "evidence-based approach",
    "On-Site Audit",
    "On-Site",
    "Desk Review",
    "Rule-Based Coding Validation",
    "false positive",
    "risk stratification",
    "upper control limit",
    "over-coding",
    "up-coding",
    "Top Rule Violations",
    "medical evidence",
    "resource intensity",
    "grouping",
    "discrepancy",
    "Discrepancy",
    "Dual Coding",
    "flag",
    "outlier",
    "screening",
    "Relative Weight"
]

for w in words_to_italicize:
    # use regex to replace whole words only, avoiding replacing inside existing asterisks if any
    # careful with case
    text = re.sub(rf'\b({w})\b', r'*\1*', text)

# Clean up double asterisks if any (like **word**)
text = text.replace('**', '*')

# Add footnotes
text = text.replace('sampel audit *Desk Review*.', 'sampel audit *Desk Review*.[^Lihat Lampiran 1]')
text = text.replace('untuk konfirmasi rekam administratif.', 'untuk konfirmasi rekam administratif.[^Lihat Lampiran 2]')
text = text.replace('mendistorsi beban iDRG.', 'mendistorsi beban iDRG.[^Lihat Lampiran 2]')

with open('generate_laporan_akhir_nasional.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done replacing.")
