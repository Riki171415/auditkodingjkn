import json

def test_md_parse():
    md_text = open('c:/Backup Riki/Drive D/KERJAAN PUSBIKES/Audit Koding 2025/audit-app/exports/agent_outputs/final_md/final_md_1275655.md', 'r', encoding='utf-8').read()
    lines = md_text.split('\n')
    i = 0
    chart_info = {}
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('`chart'):
            i += 1
            chart_block = []
            while i < len(lines) and not lines[i].strip().startswith('`'):
                chart_block.append(lines[i])
                i += 1
            
            # parse yaml-ish block
            c_data = {}
            import yaml
            try:
                c_data = yaml.safe_load('\n'.join(chart_block))
                if 'id' in c_data:
                    chart_info[c_data['id']] = c_data
            except Exception as e:
                print('yaml error:', e)
        i += 1
    
    print('Found charts:', chart_info.keys())
    
test_md_parse()
