import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from src.services.quality_assurance.text_coherence_check import calculate_perplexity, embedding_entropy, check_coherence

# --------------------------
# Unit Tests: calculate_perplexity
# --------------------------
@pytest.mark.parametrize("text", [
    "Omi ni mo mu",                       # Yoruba
    "Ninakunywa maji kila asubuhi",      # Swahili
    "I drink water every morning",       # English
    "maji",                               # short valid word
    "",                                   # empty
    "   ",                                # whitespace only
    "!!!!!!@@@@@"                         # gibberish
])
def test_calculate_perplexity_returns_valid_number(text):
    result = calculate_perplexity(text)
    assert isinstance(result, float)
    assert result >= 0.0


# --------------------------
# Unit Tests: embedding_entropy
# --------------------------
@pytest.mark.parametrize("text,min_entropy", [
    ("water", 1.0),
    ("maji", 1.0),
    ("I drink water every morning", 2.0),
    ("Ninakunywa maji kila asubuhi", 2.0),
    ("", 0.0),
    ("xyzxyzxyzxyz", 1.0)
])
def test_embedding_entropy_reasonable(text, min_entropy):
    result = embedding_entropy(text)
    assert isinstance(result, float)
    assert result >= 0.0
    if text.strip():  # only check min threshold if text isn't empty
        assert result >= min_entropy


# --------------------------
# Integration Tests: check_coherence
# --------------------------
@pytest.mark.parametrize("text,expected", [
    ("Ninakunywa maji kila asubuhi", True),  # valid Swahili
    ("I drink water every morning", True),   # valid English
    ("maji", False),                         # valid but short (likely fails entropy threshold)
    ("asdfasdfasdf", False),                 # gibberish
    ("", False),                             # empty
    ("!!!@@###", False),                     # symbols only
])
def test_check_coherence_outcomes(text, expected):
    result = check_coherence(text)
    assert isinstance(result, dict)
    assert "perplexity" in result
    assert "entropy" in result
    assert "coherence_ok" in result
    assert isinstance(result["coherence_ok"], bool)
    assert result["coherence_ok"] == expected
