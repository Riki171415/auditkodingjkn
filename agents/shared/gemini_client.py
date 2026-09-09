"""
agents/shared/gemini_client.py
==============================
Shared Gemini client untuk AI Report Generation Framework V2.
Menggunakan google.genai SDK terbaru + retry logic untuk rate limit.
"""

import os
import time
import json


def load_env():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(base_dir, '.env')
    env = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env


def get_model_name():
    env = load_env()
    return env.get('GEMINI_MODEL', 'gemini-2.5-flash')


def get_api_key():
    env = load_env()
    return env.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY', '')


def call_gemini(prompt: str, temperature: float = 0.3, max_tokens: int = 8192,
                max_retries: int = 5, retry_delay: int = 30,
                verbose: bool = True) -> str:
    """
    Panggil Gemini API dengan retry logic untuk rate limit (429).
    Menggunakan google.genai SDK terbaru.
    
    Args:
        prompt: Teks prompt lengkap
        temperature: 0.0-1.0 (rendah = lebih deterministik)
        max_tokens: Max output tokens
        max_retries: Jumlah retry jika terkena rate limit
        retry_delay: Detik tunggu antar retry (default 35 = lebih dari 1 menit free tier limit)
        verbose: Print progress

    Returns:
        String response dari Gemini, atau empty string jika semua retry gagal
    """
    api_key    = get_api_key()
    model_name = get_model_name()

    # Key format AQ. hanya kompatibel dengan old SDK (google.generativeai)
    # Key format AIza kompatibel dengan keduanya
    use_new_sdk = not api_key.startswith('AQ.')

    # ── NEW SDK (google.genai) — hanya untuk key AIza ──────────────────────
    if use_new_sdk:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            for attempt in range(1, max_retries + 1):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens,
                            top_p=0.85,
                        )
                    )
                    return response.text

                except Exception as e:
                    err_str = str(e)
                    is_retryable = any(x in err_str for x in ['429', '503', 'quota', 'rate', 'UNAVAILABLE', 'overload'])
                    if is_retryable and attempt < max_retries:
                        wait = retry_delay * attempt
                        if verbose:
                            print(f"  [RETRY {attempt}/{max_retries}] Model sibuk, tunggu {wait}s...")
                        import time
                        time.sleep(wait)
                    else:
                        if verbose:
                            print(f"  [ERROR] google.genai: {e}")
                        break

        except ImportError:
            pass  # Lanjut ke old SDK

    # ── OLD SDK (google.generativeai) — fallback atau default untuk AQ. key ──
        try:
            import google.generativeai as genai_old
            import warnings
            warnings.filterwarnings('ignore')  # Suppress deprecation warning

            genai_old.configure(api_key=api_key)
            model = genai_old.GenerativeModel(model_name)

            for attempt in range(1, max_retries + 1):
                try:
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": temperature,
                            "top_p": 0.85,
                            "max_output_tokens": max_tokens,
                        }
                    )
                    # Safe text extraction — handle all finish reasons
                    try:
                        text = response.text
                    except Exception:
                        # fallback: try candidates
                        try:
                            text = response.candidates[0].content.parts[0].text
                        except Exception:
                            text = ""
                    return text

                except Exception as e:
                    err_str = str(e)
                    is_retryable = any(x in err_str for x in ['429', '503', 'quota', 'rate', 'UNAVAILABLE', 'overload'])
                    if is_retryable and attempt < max_retries:
                        wait = retry_delay * attempt
                        if verbose:
                            print(f"  [RETRY {attempt}/{max_retries}] Server sibuk, tunggu {wait}s...")
                        time.sleep(wait)
                    elif is_retryable:
                        if verbose:
                            print(f"  [ERROR] Gagal setelah {max_retries} retry.")
                        return ""
                    else:
                        if verbose:
                            print(f"  [ERROR] Gemini API error: {e}")
                        return ""

        except ImportError:
            print("  [FATAL] Tidak ada Gemini SDK yang terinstall.")
            print("  Install: pip install google-genai")
            return ""

    return ""


def test_connection(verbose: bool = True) -> bool:
    """Test koneksi ke Gemini API."""
    if verbose:
        print(f"  Testing Gemini API (model: {get_model_name()})...")
    result = call_gemini(
        "Jawab dengan HANYA kata 'OK'.",
        temperature=0.0,
        max_tokens=10,
        max_retries=2,
        retry_delay=10,
        verbose=verbose
    )
    ok = bool(result and result.strip())
    if verbose:
        print(f"  Gemini API: {'[OK] Terhubung' if ok else '[FAIL] Gagal'}")
    return ok
