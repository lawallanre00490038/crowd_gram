import pytest
from src.services.quality_assurance.audio_parameter_check import (check_audio_file_format, 
                                                                  check_audio_file_length, 
                                                                  check_audio_sample_rate, 
                                                                  check_audio_bit_depth)

@pytest.mark.parametrize("file_name, expected_format, result", [
    ("voice.mp3", "mp3", True),
    ("recording.wav", "wav", True),
    ("track.flac", "mp3", False),  # mismatch
    ("music.m4a", None, True),     # any supported format accepted
    ("note.ogg", "ogg", True),
    ("audiofile.txt", None, False),  # unsupported extension
    ("clip", None, False),           # no extension
    ("sample.MP3", "mp3", True),     # case-insensitive
    ("test.aac", "flac", False),     # mismatch
])
def test_check_audio_file_format(file_name, expected_format, result):
    assert check_audio_file_format(file_name, expected_format) == result

@pytest.mark.parametrize("file_path, min_len, max_len, expected", [
    ("tests/assets/sample_1s_16kHz_16bit.wav", 0.5, 60.0, True),
    ("tests/assets/sample_short.mp3", 0.5, 60.0, False),
    ("tests/assets/sample_long.wav", 0.5, 60.0, False),
])
def test_check_audio_file_length(file_path, min_len, max_len, expected):
    result = check_audio_file_length(file_path, min_length=min_len, max_length=max_len)
    assert result == expected

@pytest.mark.parametrize("file_path, expected_sr, expected", [
    ("tests/assets/sample_1s_16kHz_16bit.wav", 16000, True),
    ("tests/assets/sample_2s_44kHz_32bit.flac", 16000, False),
    ("tests/assets/sample_2s_44kHz_32bit.flac", 44100, True),
])
def test_check_audio_sample_rate(file_path, expected_sr, expected):
    result = check_audio_sample_rate(file_path, expected_sample_rate=expected_sr)
    assert result == expected

@pytest.mark.parametrize("file_path, expected_bit_depth, expected", [
    ("tests/assets/sample_1s_16kHz_16bit.wav", 32, True),
    ("tests/assets/sample_1s_16kHz_16bit.wav", 16, False),
    ("tests/assets/sample_2s_44kHz_32bit.flac", 32, True),
    ("tests/assets/sample_2s_44kHz_32bit.flac", 16, False),
])
def test_check_audio_bit_depth(file_path, expected_bit_depth, expected):
    result = check_audio_bit_depth(file_path, expected_bit_depth=expected_bit_depth)
    assert result == expected



