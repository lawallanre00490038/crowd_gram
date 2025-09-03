"""
structural_checks.py

Module for running structural QA (quality assurance) checks on text data.
Intended for use in data preprocessing or validation pipelines to detect
junk content, excessive repetition, script mismatch, and profanity.

Dependencies:
    - better_profanity
    - re, logging, unicodedata

Usage:
    from structural_checks import run_all_checks

    result = run_all_checks("some input text", expected_script_prefix="LATIN")
"""

import unicodedata
import logging
import re
from better_profanity import profanity

logger = logging.getLogger(__name__)


def check_junk(text: str) -> bool:
    """
    Check if the text contains junk, placeholder, or irrelevant content.

    Args:
        text: Input string to be evaluated.

    Returns:
        True if junk patterns are found, False otherwise.
    """
    if not text or not isinstance(text, str):
        return True
    return bool(re.search(r"asdf|lorem|click here|\{\{\w+\}\}", text.lower(), re.IGNORECASE))


def has_repeated_chars(text: str, threshold: int = 4) -> bool:
    """
    Detects if the text has excessively repeated characters.

    Args:
        text: Input string to evaluate.
        threshold: Number of consecutive repeated characters to trigger flag.

    Returns:
        True if repetition exceeds threshold, False otherwise.
    """
    if not text or not isinstance(text, str):
        return False
    return bool(re.search(rf"(.)\1{{{threshold},}}", text))


def check_unicode_script(text: str, expected_script_prefix: str) -> bool:
    """
    Check if all characters in the text match the expected Unicode script.

    Args:
        text: Input string to evaluate.
        expected_script_prefix: Unicode script name prefix, e.g., "LATIN", "ARABIC".

    Returns:
        True if all characters match the script prefix, False otherwise.
    """

    if not text or not isinstance(text, str):
        return False
    try:
        for char in text:
            if not char.strip():
                continue  # Skip whitespace
            if unicodedata.category(char).startswith("M"):
                continue  # Skip combining marks
            if unicodedata.category(char).startswith("L"):  # Only enforce check on letters
                name = unicodedata.name(char, "")
                if not name.startswith(expected_script_prefix):
                    return False
        return True
    except Exception as e:
        logger.warning(f"Unicode script check failed: {e}")
        return False
    except Exception as e:
        logger.warning(f"Unicode script check failed: {e}")
        return False



def check_profanity(text: str) -> bool:
    """
    Check if the text contains profanity using better_profanity.

    Args:
        text: Input string to evaluate.

    Returns:
        True if profanity is found, False otherwise.
    """
    if not text or not isinstance(text, str):
        return False
    try:
        return profanity.contains_profanity(text)
    except Exception as e:
        logger.warning(f"Profanity check failed: {e}")
        return False


def run_all_checks(text: str, expected_script_prefix: str = "LATIN", repeat_threshold: int = 4) -> dict:
    """
    Run all structural QA checks on a given text.

    Args:
        text: Input string to evaluate.
        expected_script_prefix: Unicode script prefix to validate (default is "LATIN").
        repeat_threshold: Threshold for character repetition detection.

    Returns:
        Dictionary of check names and their boolean results.
    """
    return {
        "junk": check_junk(text),
        "repeated_chars": has_repeated_chars(text, threshold=repeat_threshold),
        "script_ok": check_unicode_script(text, expected_script_prefix),
        "profanity": check_profanity(text),
    }

