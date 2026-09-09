def fix_grouped_rules():
    with open('modules/export_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    bad_string = "    from modules.rule_engine import GROUPED_RULES"
    good_string = """    GROUPED_RULES = {
        'mutually_exclusive': {'title': 'Mutually Exclusive (Includes/Excludes)', 'rules': ['KNAVP-ME', 'ME']},
        'underlying_manifestation': {'title': 'Underlying & Manifestation', 'rules': ['KNAVP-UM', 'UM']},
        'procedure_validation': {'title': 'Procedure Validation', 'rules': ['KNAVP-PV', 'PV']},
        'unbundling': {'title': 'Unbundling', 'rules': ['KNAVP-UB', 'UB']},
        'medical_evidence': {'title': 'Medical Evidence', 'rules': ['KNAVP-MEV', 'MEV']},
        'administrative_validation': {'title': 'Administrative', 'rules': ['KNAVP-ADM', 'ADM']},
        'age_validation': {'title': 'Age Validation', 'rules': ['KNAVP-AGE', 'AGE']},
        'los_validation': {'title': 'LOS Validation', 'rules': ['KNAVP-LOS', 'LOS']}
    }"""
    
    if bad_string in content:
        content = content.replace(bad_string, good_string)
        with open('modules/export_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("GROUPED_RULES injected!")
    else:
        print("Could not find GROUPED_RULES import!")

if __name__ == '__main__':
    fix_grouped_rules()
