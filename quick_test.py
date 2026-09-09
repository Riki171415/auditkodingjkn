"""quick_test.py — Test berbagai model dengan key baru"""
import warnings
warnings.filterwarnings('ignore')

from google import genai
from google.genai import types
import time

API_KEY = "AIzaSyCPweoNd6BKS2uSpGg4CXUIR7UNiqhhfjI"
MODELS_TO_TRY = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
]

client = genai.Client(api_key=API_KEY)

for model_name in MODELS_TO_TRY:
    try:
        resp = client.models.generate_content(
            model=model_name,
            contents="Jawab HANYA: OK",
            config=types.GenerateContentConfig(max_output_tokens=5, temperature=0.0)
        )
        print(f"  [OK]   {model_name} -> {resp.text.strip()[:20]}")
    except Exception as e:
        err = str(e)[:80]
        print(f"  [FAIL] {model_name} -> {err}")
    time.sleep(1)
