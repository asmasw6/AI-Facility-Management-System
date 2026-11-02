import re
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ---- Arabic preprocessing: must be identical to the training one ----
_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_LOCATION_PATTERNS = [
    re.compile(r"(?:العنوان|الموقع|المكان)\s*:"),
    re.compile(r"(?:رقم\s+)?(?:الشقه|شقه|شقتي|وحده)\s*(?:رقم\s*)?\d+"),
    re.compile(r"(?:الدور|الطابق)\s*\d+"),
    re.compile(r"(?:المبني|مبني|العماره|برج)\s+[ابجدهa-e](?![ء-يa-z0-9])"),
]


def preprocess_arabic(text: str) -> str:
    text = str(text).lower().translate(_DIGITS)
    text = _DIACRITICS.sub("", text).replace("\u0640", "")
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    for pat in _LOCATION_PATTERNS:
        text = pat.sub(" ", text)
    text = re.sub(r"[^\u0621-\u064A\s]", " ", text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    return re.sub(r"\s+", " ", text).strip()
