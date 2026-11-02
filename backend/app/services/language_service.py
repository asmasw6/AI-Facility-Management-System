from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    try:
        language = detect(text)
        if language in {"ar", "fr", "en"}:
            return language
    except LangDetectException:
        pass

    return "en"