import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pytest
import pandas as pd
from src.services.quality_assurance.text_language_validation_text import detect_message_language


# --------------------------
# Single Detection Test
# --------------------------
@pytest.mark.parametrize("text,expected_code", [
    ("Habari za asubuhi", "swh"),
    ("Jina langu ni Amina", "swh"),
    ("Karibu nyumbani kwetu", "swh"),
    ("Asante sana kwa msaada wako", "swh")
])
def test_detect_message_language(text, expected_code):
    result = detect_message_language(text)
    print(f"Detected: {result['code']} ({result['code']}) with a confidence of {result['confidence']:.2%} script: {result['script']}")
    
    assert result["code"] == expected_code
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0

# --------------------------
# Simulated Batch Detection Test
# --------------------------
@pytest.mark.parametrize("texts,expected_codes", [
    (
        ["Habari yako", "Jina langu ni Tunu"],
        ["swh", "swh"]
    )
])
def test_batch_detection_simulated(texts, expected_codes):
    results = [detect_message_language(text)["code"] for text in texts]
    assert results == expected_codes
