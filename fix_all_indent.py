def fix_all_indent():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = -1
    for i, l in enumerate(lines):
        if "_narasi_map = {" in l:
            start_idx = i
            break
            
    if start_idx != -1:
        # Find the end of the block, which is up to document.add_heading('D. Kasus Prioritas', level=2)
        end_idx = -1
        for i in range(start_idx, len(lines)):
            if "document.add_heading('D. Kasus Prioritas'" in lines[i]:
                end_idx = i
                break
                
        if end_idx != -1:
            for i in range(start_idx + 1, end_idx):
                if lines[i].startswith("    "):
                    lines[i] = lines[i][4:]
                    
            with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print("Indentation fixed for _narasi_map block!")
            return
            
    print("Could not find block!")

if __name__ == '__main__':
    fix_all_indent()
