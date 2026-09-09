import os
import json
import re
import docx
import fitz  # PyMuPDF

ICS_DOCX = r"C:\Users\User\Downloads\ICS v7.docx"
BA_PDFS = [
    r"C:\Users\User\Downloads\DATABASE LLM\BA_Pending_Klaim_Tahun_2019_Publish.pdf",
    r"C:\Users\User\Downloads\DATABASE LLM\3760.BA-Administrasi-dg-Kemkes-tahun-2024 (1).pdf",
    r"C:\Users\User\Downloads\DATABASE LLM\BA-Kesepakatan-Koding-tahun-2023-1-dan-2-bisa-di-search-dan-tanpa-surat-pengantar (1).pdf"
]
RULES_JSON = "rules/audit_rules.json"

def tokenize(text):
    return set(re.findall(r'\b\w+\b', str(text).lower()))

def extract_ics():
    doc = docx.Document(ICS_DOCX)
    paragraphs = []
    current_headings = {}
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt: continue
        if p.style.name.startswith('Heading'):
            try:
                level = int(p.style.name.split(' ')[1])
                current_headings[level] = txt
                for l in range(level + 1, 10):
                    current_headings.pop(l, None)
            except:
                pass
        else:
            context = ' > '.join([current_headings[k] for k in sorted(current_headings.keys())])
            paragraphs.append({
                'source': f"Draft Indonesian Coding Standard (ICS) [{context}]",
                'text': txt,
                'tokens': tokenize(txt)
            })
    return paragraphs

def extract_pdfs():
    paragraphs = []
    for pdf_path in BA_PDFS:
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            continue
        try:
            doc = fitz.open(pdf_path)
            title = os.path.basename(pdf_path).replace('.pdf', '')
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("blocks")
                for b in blocks:
                    txt = b[4].strip().replace('\n', ' ')
                    if len(txt) > 20: # ignore small artifacts
                        paragraphs.append({
                            'source': f"Berita Acara (BA) {title} [Halaman {page_num+1}]",
                            'text': txt,
                            'tokens': tokenize(txt)
                        })
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
    return paragraphs

def main():
    print("Extracting ICS...")
    ics_paragraphs = extract_ics()
    print("Extracting BA PDFs...")
    ba_paragraphs = extract_pdfs()
    
    all_paragraphs = ics_paragraphs + ba_paragraphs
    print(f"Total paragraphs extracted: {len(all_paragraphs)}")
    
    with open(RULES_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    rules = data.get('rules', [])
    updated = 0
    
    for rule in rules:
        # Build query tokens
        query_text = f"{rule.get('nama_aturan', '')} {rule.get('pesan_validasi', '')}"
        
        # Add condition ICDs to query text to increase accuracy
        cond = rule.get('condition', {})
        if 'diag_a' in cond: query_text += " " + " ".join(cond['diag_a'])
        if 'diag_b' in cond: query_text += " " + " ".join(cond['diag_b'])
        if 'proc_a' in cond: query_text += " " + " ".join(cond['proc_a'])
        if 'proc_b' in cond: query_text += " " + " ".join(cond['proc_b'])
        if 'diag' in cond: query_text += " " + " ".join(cond['diag'])
        if 'proc' in cond: query_text += " " + " ".join(cond['proc'])
        
        query_tokens = tokenize(query_text)
        
        # Stop words to ignore
        stop_words = {'dan', 'atau', 'dengan', 'pada', 'yang', 'di', 'dari', 'jika', 'tidak', 'sebagai', 'kode', 'utama', 'sekunder', 'diagnosis', 'pasien', 'oleh'}
        query_tokens = query_tokens - stop_words
        
        best_match = None
        best_score = 0
        
        for p in all_paragraphs:
            intersection = query_tokens.intersection(p['tokens'])
            if len(intersection) == 0: continue
            
            # Weighted score: hitting an ICD code is heavily weighted
            score = 0
            for t in intersection:
                if re.match(r'^[a-z]\d{2}', t): # looks like ICD-10
                    score += 5
                elif re.match(r'^\d{2}\.\d{1,2}', t): # looks like ICD-9-CM
                    score += 5
                else:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = p
                
        # If score is sufficiently high, assign it
        if best_match and best_score >= 3:
            sumber = f"Sumber {best_match['source']} \"{best_match['text'][:150]}...\""
            rule['sumber_referensi'] = sumber
            updated += 1
            print(f"Matched [{rule['rule_id']}] {rule['nama_aturan']}")
            print(f"   Score: {best_score}")
            print(f"   Source: {best_match['source']}")
        else:
            print(f"No match for [{rule['rule_id']}] {rule['nama_aturan']} (Best Score: {best_score})")

    with open("rules/audit_rules_updated.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"\nDone! Successfully mapped {updated}/{len(rules)} rules.")

if __name__ == '__main__':
    main()
