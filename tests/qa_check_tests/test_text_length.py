import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import pytest
from src.services.quality_assurance.text_length_check import check_length_and_truncation

@pytest.mark.parametrize("source,translation,expected_pass,expected_reason", [
    # Good translations (balanced)
    ("Good morning", "Habari za asubuhi", True, None),            # Swahili
    ("How are you?", "Ẹ n lẹ", True, None),                      # Yoruba
    ("Hello", "Sawubona", True, None),                           # Zulu
    ("Peace be upon you", "Salam aleikum", True, None),          # Somali
    ("Welcome", "Dumela", True, None),                           # Tswana
    ("How are you?", "Tena yistilign", True, None),              # Amharic

    # Too short
    ("How are you feeling today? I hope everything is going well at work", "Nzuri", False, "Too short"),
    ("What is your favorite food? Where did you go yesterday?", "Ugali", False, "Too short"),

    # Too long
    ("Hello", "Karibu sana kwenye mkutano huu wa kisayansi unaohusisha wanasayansi kutoka nchi mbalimbali", False, "Too long"),
    ("Hi", "Leo tunazungumzia umuhimu wa elimu katika jamii ya Kisomali, hasa katika maeneo ya vijijini", False, "Too long"),

    # Truncated endings
    ("I love to run because it keeps me active", "Napenda kukimbia kwa sababu", False, "truncated"),
    ("Explain your answer", "Jibu langu ni hili lakini", False, "truncated"),
    ("Describe AI", "AI ni muhimu kwa sababu", False, "truncated"),

    # Empty or null inputs
    ("", "Habari yako", False, "Empty source text"),
    ("Peace", "", False, "Empty translation"),
    (None, "Habari", False, "Invalid input types"),
    ("Hello", None, False, "Invalid input types"),

    # Ratio boundary 
    ("How are you?", "Nzuri sana, asante", True, None),
    ("What is AI?", "AI ni akili ya bandia", True, None),
])
def test_translation_length_check_from_english(source, translation, expected_pass, expected_reason):
    result = check_length_and_truncation(source, translation)

    assert isinstance(result, dict)
    assert "passed" in result and "reason" in result

    assert result["passed"] == expected_pass

    if not expected_pass:
        assert expected_reason.lower() in result["reason"].lower()
    else:
        assert result["reason"] is None
