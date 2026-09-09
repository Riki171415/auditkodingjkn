"""
banned_phrases.py — Daftar frasa AI yang dilarang dalam laporan resmi.
Digunakan oleh Agent 3 (Editorial Reviewer) dan Agent 5 (QA Auditor).
"""

# Frasa-frasa yang terdengar seperti AI atau tidak layak laporan pemerintah
BANNED_PHRASES = [
    # Generic AI openers
    "dengan demikian, dapat disimpulkan",
    "hal ini menunjukkan bahwa",
    "sangat penting untuk dicatat",
    "memberikan gambaran yang komprehensif",
    "secara keseluruhan, dapat dikatakan",
    "dalam rangka meningkatkan",
    "perlu mendapat perhatian serius",
    "perlu diperhatikan bahwa",
    "perlu dicatat bahwa",
    "tidak dapat dipungkiri",
    "sudah tidak diragukan lagi",
    "pada dasarnya",
    "pada intinya",

    # Sensationalist / click-bait words
    "membongkar",
    "mengungkap",
    "mengejutkan",
    "terungkap",
    "fenomenal",
    "luar biasa",
    "revolusioner",
    "ilusi",
    "paradoks",

    # Vague modifiers
    "signifikan",
    "robust",
    "holistik",
    "komprehensif dalam arti luas",
    "secara menyeluruh dan terperinci",
    "sangat relevan",
    "amat krusial",
    "betapa pentingnya",
    "sungguh mengkhawatirkan",

    # Promotional language
    "membuktikan komitmen",
    "dengan bangga",
    "pencapaian yang luar biasa",
    "keunggulan dalam",
    "terdepan dalam",
    "menjadi solusi terbaik",
    "menjawab tantangan",

    # Redundant conclusions
    "berdasarkan uraian di atas, dapat disimpulkan bahwa",
    "dari seluruh pembahasan yang telah dipaparkan",
    "sebagaimana telah dijelaskan sebelumnya",
    "sebagaimana diuraikan di atas",
    "merujuk pada uraian di atas",

    # Filler phrases
    "perlu diakui",
    "harus diakui",
    "tidak bisa disangkal",
    "sejalan dengan",
    "seiring dengan",
    "dalam konteks ini",
    "dalam hal ini",
    "lebih jauh lagi",

    # Hyperbole / exaggeration
    "sangat mengkhawatirkan",
    "mengancam keberlangsungan",
    "berdampak masif",
    "dapat meruntuhkan",
    "krisis serius",
    "alarm bagi",

    # Vague AI safety nets
    "namun perlu diingat",
    "meskipun demikian, perlu diperhatikan",
    "di sisi lain, tidak bisa diabaikan",
    "kesimpulannya, masalah ini kompleks",
]

# Frasa-frasa yang diizinkan sebagai pengganti (mapping)
REPLACEMENT_SUGGESTIONS = {
    "signifikan": "tercatat / teridentifikasi / sejumlah",
    "komprehensif": "menyeluruh",
    "sangat penting": "penting",
    "dalam rangka meningkatkan": "untuk meningkatkan",
    "memberikan gambaran": "menunjukkan",
    "secara keseluruhan": "berdasarkan seluruh data yang dievaluasi",
}


def check_banned(text: str) -> list:
    """
    Periksa apakah teks mengandung frasa terlarang.
    Return list frasa yang ditemukan.
    """
    text_lower = text.lower()
    found = []
    for phrase in BANNED_PHRASES:
        if phrase.lower() in text_lower:
            found.append(phrase)
    return found


def count_violations(text: str) -> int:
    """Return jumlah frasa terlarang dalam teks."""
    return len(check_banned(text))
