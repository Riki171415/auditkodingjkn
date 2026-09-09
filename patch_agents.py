"""
patch_agents.py — Patch all agent files to use shared gemini_client.py
"""
import os

def patch_file(fp, replacements):
    if not os.path.exists(fp):
        print(f"SKIP (not found): {fp}")
        return
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()
    
    changed = False
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new, 1)
            changed = True
        else:
            print(f"  [WARN] Pattern not found in {fp}:")
            print(f"         '{old[:80]}...'")
    
    if changed:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched: {fp}")
    else:
        print(f"No changes needed: {fp}")


# ─── AGENT 2 ──────────────────────────────────────────────────────
a2_old_call = (
    "        model, model_name = get_gemini_client()\n"
    "        if verbose:\n"
    "            print(f\"  Model: {model_name}\")\n"
    "\n"
    "        user_prompt = build_user_prompt(metadata)\n"
    "        full_prompt = SYSTEM_PROMPT_AGENT2 + \"\\n\\n\" + user_prompt\n"
    "\n"
    "        response = model.generate_content(\n"
    "            full_prompt,\n"
    "            generation_config={\n"
    "                \"temperature\": 0.2,      # Rendah = deterministik & presisi\n"
    "                \"top_p\": 0.8,\n"
    "                \"max_output_tokens\": 4096,\n"
    "            }\n"
    "        )\n"
    "        outline_text = response.text"
)
a2_new_call = (
    "        model_name = get_model_name()\n"
    "        if verbose:\n"
    "            print(f\"  Model: {model_name}\")\n"
    "\n"
    "        user_prompt = build_user_prompt(metadata)\n"
    "        full_prompt = SYSTEM_PROMPT_AGENT2 + \"\\n\\n\" + user_prompt\n"
    "\n"
    "        outline_text = call_gemini(full_prompt, temperature=0.2, max_tokens=4096, verbose=verbose)"
)

patch_file("agents/agent2_senior_auditor.py", [(a2_old_call, a2_new_call)])


# ─── AGENT 3 ──────────────────────────────────────────────────────
a3_old1 = (
    "        model, model_name = get_gemini_client()\n"
    "        if verbose:\n"
    "            print(f\"  Model: {model_name}\")"
)
a3_new1 = (
    "        model_name = get_model_name()\n"
    "        if verbose:\n"
    "            print(f\"  Model: {model_name}\")"
)
a3_old2 = (
    "        response = model.generate_content(\n"
    "            full_prompt,\n"
    "            generation_config={\n"
    "                \"temperature\": 0.3,\n"
    "                \"top_p\": 0.85,\n"
    "                \"max_output_tokens\": 8192,\n"
    "            }\n"
    "        )\n"
    "        draft_text = response.text"
)
a3_new2 = "        draft_text = call_gemini(full_prompt, temperature=0.3, max_tokens=8192, verbose=verbose)"

patch_file("agents/agent3_editorial_reviewer.py", [(a3_old1, a3_new1), (a3_old2, a3_new2)])


# ─── AGENT 4 ──────────────────────────────────────────────────────
a4_old1 = (
    "        model, model_name = get_gemini_client()\n"
    "        if verbose:\n"
    "            print(f\"  Model: {model_name}\")"
)
a4_new1 = (
    "        model_name = get_model_name()\n"
    "        if verbose:\n"
    "            print(f\"  Model: {model_name}\")"
)
a4_old2 = (
    "        response = model.generate_content(\n"
    "            full_prompt,\n"
    "            generation_config={\n"
    "                \"temperature\": 0.1,   # Sangat deterministik untuk formatting\n"
    "                \"top_p\": 0.8,\n"
    "                \"max_output_tokens\": 8192,\n"
    "            }\n"
    "        )\n"
    "        final_md = response.text"
)
a4_new2 = "        final_md = call_gemini(full_prompt, temperature=0.1, max_tokens=8192, verbose=verbose)"

patch_file("agents/agent4_report_designer.py", [(a4_old1, a4_new1), (a4_old2, a4_new2)])


# ─── AGENT 5 ──────────────────────────────────────────────────────
a5_old = (
    "                model, model_name = get_gemini_client()\n"
    "                issues_text = \"\\n\".join([\n"
    "                    f\"- Poin {i['point']}: {i['description']} (Fix: {i['fix_hint']})\"\n"
    "                    for i in critical_issues\n"
    "                ])\n"
    "                fix_prompt = SYSTEM_PROMPT_AGENT5_FIX.format(issues=issues_text)\n"
    "                fix_prompt += f\"\\n\\nLaporan yang perlu diperbaiki:\\n\\n{current_md[:5000]}\"\n"
    "\n"
    "                response = model.generate_content(\n"
    "                    fix_prompt,\n"
    "                    generation_config={\"temperature\": 0.1, \"max_output_tokens\": 8192}\n"
    "                )\n"
    "                current_md = response.text"
)
a5_new = (
    "                issues_text = \"\\n\".join([\n"
    "                    f\"- Poin {i['point']}: {i['description']} (Fix: {i['fix_hint']})\"\n"
    "                    for i in critical_issues\n"
    "                ])\n"
    "                fix_prompt = SYSTEM_PROMPT_AGENT5_FIX.format(issues=issues_text)\n"
    "                fix_prompt += f\"\\n\\nLaporan yang perlu diperbaiki:\\n\\n{current_md[:5000]}\"\n"
    "\n"
    "                fixed = call_gemini(fix_prompt, temperature=0.1, max_tokens=8192, verbose=verbose)\n"
    "                if fixed:\n"
    "                    current_md = fixed"
)

patch_file("agents/agent5_qa_auditor.py", [(a5_old, a5_new)])

print("\nDone. All agents patched to use shared gemini_client.py")
