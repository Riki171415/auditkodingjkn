"""
run_framework_v2.py -- Orchestrator
====================================
AI Report Generation Framework V2
Kementerian Kesehatan RI / Pusat Pembiayaan Kesehatan

Pipeline 5-Agent:
  RAW DATA -> Agent1 -> Agent2 -> Agent3 -> Agent4 -> Agent5 -> DOCX/PDF/PNG

Penggunaan:
  python run_framework_v2.py                        # Satu RS default (1275655)
  python run_framework_v2.py --kode_rs 1275655      # Satu RS spesifik
  python run_framework_v2.py --all                  # Semua 44 RS
  python run_framework_v2.py --all --start 3573011  # Lanjut dari RS tertentu
  python run_framework_v2.py --kode_rs 1275655 --skip_to agent3  # Loncat ke agent tertentu
"""

import os
import sys
import time
import argparse
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Import semua agents
from agents.agent1_data_reviewer   import run as agent1_run, COCHRAN_MASTER
from agents.agent2_senior_auditor  import run as agent2_run
from agents.agent3_editorial_reviewer import run as agent3_run
from agents.agent4_report_designer import run as agent4_run
from agents.agent5_qa_auditor      import run as agent5_run
from agents.agent_template_filler  import run as template_filler_run

# Import generator
from generate_from_md import generate_all_outputs

LOG_DIR = os.path.join(BASE_DIR, 'exports', 'agent_outputs')


def print_banner(template_mode: bool = False):
    print("=" * 66)
    print("  AI REPORT GENERATION FRAMEWORK V2")
    print("  Kementerian Kesehatan RI -- Pusat Pembiayaan Kesehatan")
    print("  Audit Koding INA-CBG / iDRG -- Tahun 2025")
    print("-" * 66)
    if template_mode:
        print("  [TEMPLATE MODE] Skip Agent 2/3/4 (LLM) -- hemat token")
        print("  AGENT 1 : DATA REVIEWER        --> JSON Metadata")
        print("  TEMPLATE: Python Filler        --> Final Markdown (.md)")
        print("  AGENT 5 : QUALITY ASSURANCE    --> Approved (.md) + QA Report")
        print("  GENERATOR: generate_from_md.py --> DOCX / PDF / PNG Chart")
    else:
        print("  AGENT 1 : DATA REVIEWER        --> JSON Metadata")
        print("  AGENT 2 : SENIOR AUDITOR       --> Audit Outline (.md)")
        print("  AGENT 3 : EDITORIAL REVIEWER   --> Draft Laporan (.md)")
        print("  AGENT 4 : REPORT DESIGNER      --> Final Markdown (.md)")
        print("  AGENT 5 : QUALITY ASSURANCE    --> Approved (.md) + QA Report")
        print("  GENERATOR: generate_from_md.py --> DOCX / PDF / PNG Chart")
    print("=" * 66)


def run_single_rs_template(kode_rs: str, verbose: bool = True) -> dict:
    """
    Jalankan pipeline FAST (tanpa LLM) menggunakan Template Filler.
    """
    result = {
        'kode_rs': kode_rs,
        'rs_name': COCHRAN_MASTER.get(kode_rs, {}).get('rs_name', kode_rs),
        'started_at': datetime.now().isoformat(),
        'steps': {},
        'success': False,
        'errors': [],
    }

    print(f"\n{'-'*65}")
    print(f"  RS: {result['rs_name']} ({kode_rs}) [TEMPLATE MODE]")
    print(f"{'-'*65}")

    try:
        # 1. Agent 1 (Data Review)
        if verbose: print("\n[1/4] Menjalankan Agent 1: Data Reviewer...")
        meta_dict = agent1_run(kode_rs, verbose=verbose)
        if not meta_dict:
            result['errors'].append("Agent1 failed")
            return result
        result['steps']['agent1'] = "OK"

        # 2. Template Filler
        if verbose: print("\n[2/4] Menjalankan Template Filler...")
        final_md = template_filler_run(kode_rs, verbose=verbose)
        if not final_md:
            result['errors'].append("Template Filler failed")
            return result
        result['steps']['template_filler'] = "OK"

        # 3. QA / LLM (Dilewati di Template Mode)
        if verbose: print("\n[3/4] Skip QA (Template sudah valid secara bawaan)...")
        approved_md = final_md
        result['steps']['agent5'] = "SKIPPED"

        # 4. Generator
        if verbose: print("\n[4/4] Menjalankan Generator (DOCX/PNG)...")
        outputs = generate_all_outputs(kode_rs, approved_md, meta_dict)
        if not outputs.get('docx'):
            result['errors'].append("Generator failed")
            return result
        result['steps']['generator'] = outputs

        result['success'] = True

    except Exception as e:
        result['errors'].append(f"System Error: {str(e)}")

    return result


def run_single_rs(kode_rs: str, skip_to: str = None, verbose: bool = True) -> dict:
    """
    Jalankan pipeline lengkap untuk satu RS.
    Return: dict berisi status dan path output.
    """
    result = {
        'kode_rs': kode_rs,
        'rs_name': COCHRAN_MASTER.get(kode_rs, {}).get('rs_name', kode_rs),
        'started_at': datetime.now().isoformat(),
        'steps': {},
        'success': False,
        'errors': [],
    }

    agents = ['agent1', 'agent2', 'agent3', 'agent4', 'agent5', 'generator']
    skip_order = {a: i for i, a in enumerate(agents)}
    skip_idx = skip_order.get(skip_to, 0) if skip_to else 0

    print(f"\n{'-'*65}")
    print(f"  RS: {result['rs_name']} ({kode_rs})")
    print(f"{'-'*65}")

    try:
        # -- AGENT 1: DATA REVIEWER ----------------------------------
        if skip_idx <= 0:
            t0 = time.time()
            print(f"\n[1/5] AGENT 1 -- DATA REVIEWER")
            metadata = agent1_run(kode_rs, verbose=verbose)
            elapsed  = round(time.time() - t0, 1)
            if metadata:
                result['steps']['agent1'] = {'status': 'OK', 'elapsed': elapsed}
                print(f"   Agent 1 selesai ({elapsed}s)")
            else:
                result['steps']['agent1'] = {'status': 'ERROR', 'elapsed': elapsed}
                result['errors'].append('Agent 1 gagal menghasilkan metadata')
                return result
        else:
            # Load metadata dari file
            meta_path = os.path.join(LOG_DIR, 'data_review', f'data_review_{kode_rs}.json')
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                print(f"  [SKIP] Agent 1 -- Load dari cache: {meta_path}")
            else:
                print(f"  [ERROR] Cache Agent 1 tidak ditemukan: {meta_path}")
                return result

        # -- AGENT 2: SENIOR AUDITOR ----------------------------------
        if skip_idx <= 1:
            t0 = time.time()
            print(f"\n[2/5] AGENT 2 -- SENIOR AUDITOR (Gemini LLM)")
            outline = agent2_run(kode_rs, metadata=metadata, verbose=verbose)
            elapsed = round(time.time() - t0, 1)
            if outline:
                result['steps']['agent2'] = {'status': 'OK', 'elapsed': elapsed}
                print(f"   Agent 2 selesai ({elapsed}s) -- {len(outline.split()):,} kata")
            else:
                result['steps']['agent2'] = {'status': 'ERROR', 'elapsed': elapsed}
                result['errors'].append('Agent 2 gagal menghasilkan Audit Outline')
                return result
        else:
            outline_path = os.path.join(LOG_DIR, 'audit_outline', f'audit_outline_{kode_rs}.md')
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline = f.read()
            print(f"  [SKIP] Agent 2 -- Load dari cache")

        # -- AGENT 3: EDITORIAL REVIEWER ------------------------------
        if skip_idx <= 2:
            t0 = time.time()
            print(f"\n[3/5] AGENT 3 -- EDITORIAL REVIEWER (Gemini LLM)")
            draft = agent3_run(kode_rs, outline_text=outline, metadata=metadata, verbose=verbose)
            elapsed = round(time.time() - t0, 1)
            if draft:
                result['steps']['agent3'] = {'status': 'OK', 'elapsed': elapsed}
                print(f"   Agent 3 selesai ({elapsed}s) -- {len(draft.split()):,} kata")
            else:
                result['steps']['agent3'] = {'status': 'ERROR', 'elapsed': elapsed}
                result['errors'].append('Agent 3 gagal menghasilkan Draft')
                return result
        else:
            draft_path = os.path.join(LOG_DIR, 'draft', f'draft_{kode_rs}.md')
            with open(draft_path, 'r', encoding='utf-8') as f:
                draft = f.read()
            print(f"  [SKIP] Agent 3 -- Load dari cache")

        # -- AGENT 4: REPORT DESIGNER ---------------------------------
        if skip_idx <= 3:
            t0 = time.time()
            print(f"\n[4/5] AGENT 4 -- REPORT DESIGNER (Gemini LLM)")
            final_md = agent4_run(kode_rs, draft_text=draft, metadata=metadata, verbose=verbose)
            elapsed  = round(time.time() - t0, 1)
            if final_md:
                result['steps']['agent4'] = {'status': 'OK', 'elapsed': elapsed}
                print(f"   Agent 4 selesai ({elapsed}s) -- {len(final_md.split()):,} kata")
            else:
                result['steps']['agent4'] = {'status': 'ERROR', 'elapsed': elapsed}
                result['errors'].append('Agent 4 gagal menghasilkan Final MD')
                return result
        else:
            final_path = os.path.join(LOG_DIR, 'final_md', f'final_md_{kode_rs}.md')
            with open(final_path, 'r', encoding='utf-8') as f:
                final_md = f.read()
            print(f"  [SKIP] Agent 4 -- Load dari cache")

        # -- AGENT 5: QUALITY ASSURANCE --------------------------------
        if skip_idx <= 4:
            t0 = time.time()
            print(f"\n[5/5] AGENT 5 -- QUALITY ASSURANCE")
            approved = agent5_run(kode_rs, final_md=final_md, metadata=metadata, verbose=verbose)
            elapsed  = round(time.time() - t0, 1)
            if approved:
                result['steps']['agent5'] = {'status': 'OK', 'elapsed': elapsed}
                print(f"   Agent 5 selesai ({elapsed}s)")
            else:
                result['steps']['agent5'] = {'status': 'ERROR', 'elapsed': elapsed}
                result['errors'].append('Agent 5 gagal QA')
                # Gunakan final_md meski QA gagal
                approved = final_md
        else:
            approved_path = os.path.join(LOG_DIR, 'approved', f'approved_{kode_rs}.md')
            with open(approved_path, 'r', encoding='utf-8') as f:
                approved = f.read()
            print(f"  [SKIP] Agent 5 -- Load dari cache")

        # -- PYTHON GENERATOR -----------------------------------------
        print(f"\n[GEN] PYTHON GENERATOR -> DOCX / PDF / PNG")
        t0 = time.time()
        outputs = generate_all_outputs(kode_rs, approved, metadata)
        elapsed = round(time.time() - t0, 1)
        result['steps']['generator'] = {'status': 'OK', 'elapsed': elapsed, 'outputs': outputs}
        print(f"   Generator selesai ({elapsed}s)")
        for k, v in outputs.items():
            print(f"     {k}: {v}")

        result['success'] = True

    except Exception as e:
        result['errors'].append(str(e))
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()

    result['finished_at'] = datetime.now().isoformat()
    return result


def save_run_log(results: list):
    """Simpan log eksekusi pipeline ke JSON."""
    log_path = os.path.join(LOG_DIR, f'run_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  Run log: {log_path}")


def main():
    parser = argparse.ArgumentParser(
        description='AI Report Generation Framework V2 -- Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python run_framework_v2.py                         # Test 1 RS (1275655)
  python run_framework_v2.py --kode_rs 3273015       # RS spesifik
  python run_framework_v2.py --all                   # Semua 44 RS
  python run_framework_v2.py --kode_rs 1275655 --skip_to agent3   # Mulai dari Agent 3
        """
    )
    parser.add_argument('--kode_rs',  type=str, default='1275655', help='Kode RS (default: 1275655 = RSU H. Adam Malik)')
    parser.add_argument('--all',      action='store_true',         help='Proses semua 44 RS secara batch')
    parser.add_argument('--start',    type=str, default=None,      help='Kode RS awal untuk batch (lanjutkan dari RS ini)')
    parser.add_argument('--skip_to',  type=str, default=None,      help='Skip ke agent tertentu: agent1/agent2/.../generator')
    parser.add_argument('--quiet',    action='store_true',         help='Kurangi output verbose')
    parser.add_argument('--template', action='store_true',
                        help='Template mode: skip Agent 2/3/4 (LLM), gunakan Python template filler. Hemat token untuk batch 44 RS.')
    args = parser.parse_args()

    print_banner(template_mode=args.template)
    start_total = time.time()
    all_results = []

    run_fn = run_single_rs_template if args.template else run_single_rs

    if args.all:
        rs_list = list(COCHRAN_MASTER.keys())
        if args.start and args.start in rs_list:
            start_idx = rs_list.index(args.start)
            rs_list   = rs_list[start_idx:]
            print(f"  Melanjutkan dari RS: {args.start} ({len(rs_list)} RS tersisa)")

        mode_label = 'Template (tanpa LLM)' if args.template else 'LLM'
        est_min    = round(len(rs_list) * (0.5 if args.template else 3), 0)
        print(f"\n  Batch mode: {len(rs_list)} RS akan diproses [{mode_label}]")
        print(f"  Estimasi waktu: ~{int(est_min)} menit\n")

        for i, krs in enumerate(rs_list, 1):
            rs_name = COCHRAN_MASTER[krs].get('rs_name', krs)
            print(f"\n[{i}/{len(rs_list)}] {rs_name}")
            result = run_fn(krs, verbose=not args.quiet)
            all_results.append(result)
            status = "[OK]" if result['success'] else "[FAIL]"
            print(f"  {status} {krs} -- {'OK' if result['success'] else ', '.join(result['errors'])}")

    else:
        result = run_fn(args.kode_rs, verbose=not args.quiet)
        all_results.append(result)

    # Summary
    total_elapsed = round(time.time() - start_total, 1)
    success_count = sum(1 for r in all_results if r['success'])
    fail_count    = len(all_results) - success_count

    print(f"""
+==================================================================+
|  SELESAI -- AI Report Generation Framework V2                     |
+==================================================================+
|  Total RS diproses : {len(all_results):<5}                                      |
|  Berhasil          : {success_count:<5}                                      |
|  Gagal             : {fail_count:<5}                                      |
|  Total waktu       : {total_elapsed:<8.1f}s                               |
+==================================================================+
""")

    save_run_log(all_results)

    if fail_count > 0:
        print("  RS yang gagal:")
        for r in all_results:
            if not r['success']:
                print(f"  - {r['kode_rs']} ({r['rs_name']}): {', '.join(r['errors'])}")


if __name__ == '__main__':
    main()
