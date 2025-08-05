import pytest
import librosa
import numpy as np
from src.services.quality_assurance.audio_quality_check import (
    check_audio_quality,
    analyze_audio,
    cal_signal_power,
    cal_noise_floor,
    cal_silence_percentage,
)

# Helper to load test audio
def load_audio(file_path):
    return librosa.load(file_path, sr=None)

@pytest.mark.parametrize("file_path, expected_msg_keywords", [
    ("tests/assets/clean_speech.wav", ["Approved"]),
    ("tests/assets/noisy_speech.wav", ["There is noise where you are."]),
    ("tests/assets/quiet_speech.wav", ["speak louder"]),
])
def test_check_audio_quality(file_path, expected_msg_keywords):
    data, sr = load_audio(file_path)

    enhanced, analysis = check_audio_quality(data, sr)

    assert isinstance(enhanced, np.ndarray)
    assert isinstance(analysis, dict)
    assert "snr" in analysis
    assert "message" in analysis
    assert any(keyword in analysis["message"] for keyword in expected_msg_keywords)


def test_analyze_audio_structure():
    data, sr = load_audio("tests/assets/clean_speech.wav")
    analysis = analyze_audio(data, sr)

    assert isinstance(analysis, dict)
    for key in ["snr", "silence", "noise_power", "signal_power"]:
        assert key in analysis
        assert isinstance(analysis[key], float)


def test_signal_and_noise_power_computation():
    data, sr = load_audio("tests/assets/clean_speech.wav")

    signal_power = cal_signal_power(data)
    noise_floor = cal_noise_floor(data, sr)
    silence_percentage = cal_silence_percentage(data, noise_floor)

    assert isinstance(signal_power, (float, np.floating))
    assert isinstance(noise_floor, (float, np.floating))
    assert isinstance(silence_percentage, (float, np.floating))
    assert 0 <= silence_percentage <= 100

@pytest.mark.parametrize("file_path, min_snr, expect_approval", [
    ("tests/assets/clean_speech.wav", 30, True),
    ("tests/assets/noisy_speech.wav", 40, False),
])
def test_check_audio_quality_snr_threshold(file_path, min_snr, expect_approval):
    data, sr = load_audio(file_path)
    _, analysis = check_audio_quality(data, sr, min_snr_value=min_snr)

    if expect_approval:
        assert "Approved" in analysis["message"]
    else:
        assert "Approved" not in analysis["message"]
