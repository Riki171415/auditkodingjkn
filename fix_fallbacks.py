"""fix_fallbacks.py — Fix empty-string fallback di Agent 3 dan Agent 4"""
import re

fixes = {
    "agents/agent3_editorial_reviewer.py": {
        "old": "        if not draft_text.strip():\n            draft_text = _fallback_draft(outline_text, metadata, kode_rs, rs_name)\n\n    except Exception as e:\n        print(f\"  [ERROR] Gemini API gagal: {e}\")\n        print(f\"  Menggunakan fallback template...\")\n        draft_text = _fallback_draft(outline_text, metadata, kode_rs, rs_name)",
        "new": "        if not draft_text.strip():\n            draft_text = _fallback_draft(outline_text, metadata, kode_rs, rs_name)\n\n    except Exception as e:\n        print(f\"  [WARN] Exception: {e} -- pakai fallback\")\n        draft_text = _fallback_draft(outline_text, metadata, kode_rs, rs_name)\n\n    # Final safety net\n    if not draft_text or not draft_text.strip():\n        draft_text = _fallback_draft(outline_text, metadata, kode_rs, rs_name)",
    },
    "agents/agent4_report_designer.py": {
        "old": "        final_md = call_gemini(full_prompt, temperature=0.1, max_tokens=8192, verbose=verbose)\n\n    except Exception as e:\n        print(f\"  [ERROR] Gemini API gagal: {e}\")\n        print(f\"  Menggunakan fallback struktural...\")\n        final_md = _fallback_structure(draft_text, chart_blocks, metadata, kode_rs, rs_name)",
        "new": "        final_md = call_gemini(\n            full_prompt,\n            temperature=0.1,\n            max_tokens=8192,\n            max_retries=5,\n            retry_delay=40,\n            verbose=verbose\n        )\n        if not final_md:\n            print(f\"  Gemini tidak merespons -- pakai fallback struktural\")\n            final_md = _fallback_structure(draft_text, chart_blocks, metadata, kode_rs, rs_name)\n\n    except Exception as e:\n        print(f\"  [WARN] Exception: {e} -- pakai fallback\")\n        final_md = _fallback_structure(draft_text, chart_blocks, metadata, kode_rs, rs_name)\n\n    # Final safety net\n    if not final_md or not final_md.strip():\n        final_md = _fallback_structure(draft_text, chart_blocks, metadata, kode_rs, rs_name)",
    },
}

for fp, fix in fixes.items():
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    if fix["old"] in content:
        content = content.replace(fix["old"], fix["new"], 1)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched: {fp}")
    else:
        print(f"[WARN] Pattern not found in {fp} -- manual check needed")

print("Done.")
