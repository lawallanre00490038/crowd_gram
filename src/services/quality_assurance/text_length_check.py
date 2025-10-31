"""
QA Check: Length and Truncation 
----------------------------------------------
Checks whether a text is:
- Too short or too long compared to the input
- Truncated or incomplete based on known linguistic markers
"""

import unicodedata


TRUNCATION_ENDINGS = {
    # English
    "...", "…", "but", "because",

    # Swahili
    "lakini", "kwa sababu",

    # Yoruba
    "ṣugbọn", "nítorí",

    # Hausa
    "amma", "saboda",

    # Zulu / Xhosa
    "kodwa", "ngoba",

    # Amharic
    "ግን", "ምክንያቱም",

    # Tigrinya
    "ነገር", "ምኽንያቱ",

    # Arabic
    "لكن", "لأن"
}


def is_truncated(text: str,max_ngram=4) -> bool:
    """
    Checks whether the given text appears to be truncated based on known endings.

    Args:
        text (str): The translated or generated text
        max_ngram (int): Max number of trailing words to consider

    Returns:
        bool: True if it ends with a likely truncation marker
    """
    if not text or not isinstance(text, str):
        return False

    words = text.strip().lower().split()
    if not words:
        return False

    if not words:
            return False

    # Check trailing n-grams up to max_ngram
    for n in range(1, min(max_ngram + 1, len(words) + 1)):
        ending_ngram = " ".join(words[-n:])
        if ending_ngram in TRUNCATION_ENDINGS:
            return True

    return False


def check_length_and_truncation(source, translation, min_ratio=0.2, max_ratio=3.0):
    """
    Verifies if the translation is reasonably sized and not truncated.

    Args:
        source (str): The source input text
        translation (str): The generated or translated text
        min_ratio (float): Minimum allowed length ratio (tgt/src)
        max_ratio (float): Maximum allowed length ratio

    Returns:
        dict: {
            "passed": bool,
            "reason": str or None
        }
    """
    if not isinstance(source, str) or not isinstance(translation, str):
        return {"passed": False, "reason": "Invalid input types"}

    if not source.strip():
        return {"passed": False, "reason": "Empty source text"}

    if not translation.strip():
        return {"passed": False, "reason": "Empty translation"}

    src_len = len(source.strip().split())
    tgt_len = len(translation.strip().split())

    ratio = tgt_len / src_len

    if ratio < min_ratio:
        return {"passed": False, "reason": f"Too short: ratio {ratio:.2f} < {min_ratio}"}

    if ratio > max_ratio:
        return {"passed": False, "reason": f"Too long: ratio {ratio:.2f} > {max_ratio}"}

    if is_truncated(translation):
        return {"passed": False, "reason": "Translation appears truncated"}

    return {"passed": True, "reason": None}


def qa_check_turn(source_turn, generated_turn):
    """
    QA wrapper to validate length and truncation in a single-turn pair.

    Args:
        source_turn (str): User's original input
        generated_turn (str): Model's response

    Returns:
        dict: Result of length and truncation QA check
    """
    return check_length_and_truncation(source_turn, generated_turn)
