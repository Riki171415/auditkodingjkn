"""test_key.py — Quick test API key baru"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.shared.gemini_client import call_gemini, get_model_name

model = get_model_name()
print(f"Model: {model}")
print("Testing API key...")

result = call_gemini(
    "Jawab HANYA dengan kalimat ini persis: API_KEY_VALID",
    temperature=0.0,
    max_tokens=20,
    max_retries=2,
    retry_delay=5,
    verbose=True
)

if result:
    print(f"\n[OK] API Key valid. Response: {result.strip()}")
else:
    print("\n[FAIL] API Key tidak berfungsi.")
