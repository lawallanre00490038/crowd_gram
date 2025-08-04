import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from src.services.quality_assurance.text_structural_checks import (
    check_junk,
    has_repeated_chars,
    check_unicode_script,
    check_profanity,
    run_all_checks
)

# -------------------------------
# UNIT TESTS
# -------------------------------

@pytest.mark.parametrize("text,expected", [
    ("asdf", True),
    ("Habari za lorem ipsum", True),
    ("Click here kuendelea", True),
    ("{{jina}} lako ni nani?", True),
    ("Hii ni sentensi halali kabisa.", False),
    ("", True),
    (None, True)
])
def test_check_junk(text, expected):
    assert check_junk(text) == expected


@pytest.mark.parametrize("text,threshold,expected", [
    ("Ndiyooooooo", 3, True),     # Zulu or Swahili repeated
    ("E waaaaaa", 4, True),       # Yoruba
    ("Salammmmmm", 5, True),       
    ("Barka da zuwa", 3, False),  # Hausa normal
    ("", 4, False),
    (None, 4, False)
])
def test_has_repeated_chars(text, threshold, expected):
    assert has_repeated_chars(text, threshold) == expected


@pytest.mark.parametrize("text,script_prefix,expected", [
    ("Habari yako", "LATIN", True),              # Swahili
    ("Sannu da zuwa", "LATIN", True),            # Hausa (Latin alphabet)
    ("እንኳን ደህና መጣህ", "ETHIOPIC", True),       # Amharic (Ethiopic script)
    ("Ẹ káàbọ̀", "LATIN", True),                 # Yoruba (uses diacritics in Latin)
    ("Sawubona", "LATIN", True),                 # Zulu
    ("こんにちは", "LATIN", False),               # Japanese - should fail
    ("", "LATIN", False),
    (None, "LATIN", False)
])
def test_check_unicode_script(text, script_prefix, expected):
    assert check_unicode_script(text, script_prefix) == expected


@pytest.mark.parametrize("text,expected", [
    ("Hii ni barua safi kabisa.", False),  # Swahili
    ("You are a shithead", True),          # Profanity
    ("", False),
    (None, False)
])
def test_check_profanity(text, expected):
    assert check_profanity(text) == expected


# -------------------------------
# INTEGRATION TESTS
# -------------------------------

def test_run_all_checks_swahili_junk_repeats():
    input_text = "asdf Habariiiii {{placeholder}}"
    result = run_all_checks(input_text, expected_script_prefix="LATIN", repeat_threshold=3)

    # assert result["junk"] is True
    # assert result["repeated_chars"] is True
    assert result["script_ok"] is True  # Still all Latin
    assert isinstance(result["profanity"], bool)


def test_run_all_checks_amharic_scripxt_match():
    input_text = "እንኳን ደህና መጣህ"  # Amharic greeting
    result = run_all_checks(input_text, expected_script_prefix="ETHIOPIC")

    assert result["junk"] is False
    assert result["repeated_chars"] is False
    assert result["script_ok"] is True
    assert result["profanity"] is False


def test_run_all_checks_hausa_clean_input():
    input_text = "Sannu da zuwa gida"
    result = run_all_checks(input_text, expected_script_prefix="LATIN")

    assert result == {
        "junk": False,
        "repeated_chars": False,
        "script_ok": True,
        "profanity": False
    }
