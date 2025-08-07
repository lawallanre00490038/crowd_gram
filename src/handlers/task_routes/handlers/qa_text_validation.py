# qa_text_validation.py

from typing import Dict, List, Union


from qa_checks.language_validation_text import detect_message_language
from qa_checks.structural_checks import check_junk, has_repeated_chars, check_unicode_script, check_profanity
from qa_checks.text_coherence_check import check_coherence
from qa_checks.text_length_check import check_length_and_truncation




def validate_text_input(text: str, task_lang: str = None, exp_task_script = None) -> Dict[str, Union[bool, List[str], Dict]]:
    """
    Telegram bot–friendly text QA validator.
    Runs all checks, accumulates failures, and returns structured result.

    Args:
        text (str): User input text.
        task_lang (str, optional): Expected language  (e.g., 'English', 'Amharic').

    Returns:
        dict: {
            "success": bool,
            "fail_reasons": [list of str],
            "metadata": {additional stats}
        }
    """
    fail_reasons = []
    metadata = {}

    # 1. Junk Check
    if check_junk(text):
        fail_reasons.append("Text looks like junk or gibberish.")

    # 2. Repeated Characters
    if has_repeated_chars(text, threshold=5):
        fail_reasons.append("Text contains too many repeated characters.")

    # 3. Unicode Script Check
    if not check_unicode_script(text,expected_script_prefix=exp_task_script):
        print(f"expected script: {exp_task_script}")
        fail_reasons.append("Text contains unexpected or invalid characters.")

    # 4. Language Detection
    lang_result = detect_message_language(text)
    detected_lang_code = lang_result.get("code")
    detected_lang = lang_result.get("language","unknown").upper()
    lang_confidence = lang_result.get("confidence", 0.0)
    metadata["language"] = detected_lang
    metadata["language_code"] = detected_lang_code
    metadata["language_confidence"] = lang_confidence

    if task_lang and detected_lang != task_lang:
        fail_reasons.append(
            f"Expected language '{task_lang}', but detected '{detected_lang}' (confidence: {lang_confidence:.2f})."
        )

    # 5. Profanity Check
    if check_profanity(text):
        fail_reasons.append("Text contains profane or inappropriate language.")

    # 6. Length and Truncation

    length_result = check_length_and_truncation(source="This is a sample text to be translated",translation=text)
    if not length_result.get("length_ok", True):
        fail_reasons.append("Text is too short.")
    if length_result.get("is_truncated", False):
        fail_reasons.append("Text appears to be truncated or incomplete.")
    metadata.update(length_result)

    # 7. Coherence Check
    coherence_result = check_coherence(text)
    if not coherence_result.get("coherence_ok", True):
        fail_reasons.append("Text is incoherent or lacks clarity.")
    metadata.update(coherence_result)

    # Final Result
    return {
        "success": len(fail_reasons) == 0,
        "fail_reasons": fail_reasons,
        "metadata": metadata
    }
