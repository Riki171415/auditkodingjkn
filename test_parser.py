import re

def parse_md_to_blocks(md_path):
    import os
    if not os.path.exists(md_path):
        return None
        
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
        
    blocks = []
    lines = md_text.split('\n')
    i = 0
    in_toc = False
    while i < len(lines):
        line = lines[i]
        if '<!-- TOC_START -->' in line:
            in_toc = True
            i += 1
            continue
        if '<!-- TOC_END -->' in line:
            in_toc = False
            i += 1
            continue
        if in_toc:
            i += 1
            continue
            
        if line.startswith('`'):
            i += 1
            while i < len(lines) and not lines[i].startswith('`'):
                i += 1
        elif line.startswith('#'):
            header_text = line.lstrip('#').strip()
            blocks.append((header_text, True))
        elif line.strip() and not re.match(r'^[-*_]{3,}$', line.strip()):
            content = line.strip()
            # Remove markdown bold/italic asterisks for simple rendering
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
            content = re.sub(r'\*(.*?)\*', r'\1', content)
            blocks.append((content, False))
        i += 1
    return blocks
