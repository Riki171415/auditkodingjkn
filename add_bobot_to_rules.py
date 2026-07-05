"""
Script untuk menambahkan field 'bobot' dan 'kelompok_rule' ke semua rule di audit_rules.json
"""
import json
import os

RULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rules', 'audit_rules.json')

KATEGORI_TO_KELOMPOK = {
    'combination_code': 'Combination Code',
    'dagger_asterisk': 'Dagger & Asterisk',
    'includes_excludes': 'Includes/Excludes',
    'underlying_manifestation': 'Underlying & Manifestation',
    'procedure_validation': 'Procedure Validation',
    'unbundling': 'Unbundling',
    'dual_coding': 'Dual Coding',
    'medical_evidence': 'Medical Evidence',
    'administrative_validation': 'Administrative',
    'age_validation': 'Age Validation',
    'los_validation': 'LOS Validation',
}

SEVERITY_BOBOT = {
    'High': 3,
    'Medium': 2,
    'Low': 1,
}

with open(RULES_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

rules = data['rules']
updated = 0

for rule in rules:
    changed = False
    
    # Add bobot if missing
    if 'bobot' not in rule:
        severity = rule.get('severity', 'Low')
        rule['bobot'] = SEVERITY_BOBOT.get(severity, 1)
        changed = True
    
    # Add kelompok_rule if missing
    if 'kelompok_rule' not in rule:
        kategori = rule.get('kategori', '')
        rule['kelompok_rule'] = KATEGORI_TO_KELOMPOK.get(kategori, kategori)
        changed = True
    
    if changed:
        updated += 1

with open(RULES_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! Updated {updated}/{len(rules)} rules with 'bobot' and 'kelompok_rule' fields.")
print(f"Saved to: {RULES_PATH}")
