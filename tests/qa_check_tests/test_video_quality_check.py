import pytest
import os
import json
import tempfile
from src.services.quality_assurance.video_quality_check import (
    extract_audio_from_video,
    check_video_audio_quality,
    check_video_image_quality
)

@pytest.mark.parametrize("video_path, expected_ext", [
    ("tests/assets/sample_video_with_audio.mp4", ".wav"),
])
def test_extract_audio_from_video(video_path, expected_ext):
    audio_path = extract_audio_from_video(video_path)
    assert os.path.exists(audio_path)
    assert audio_path.endswith(expected_ext)
    os.remove(audio_path)  # cleanup


@pytest.mark.parametrize("video_path, snr_min, snr_edit, speech_min, speech_max, noise_min, expect_keys", [
    (
        "tests/assets/sample_video_with_audio.mp4", 
        40, 30, -10, -30, -40,
        {"snr", "silence", "noise_power", "signal_power", "message", "output_video"}
    ),
])
def test_check_video_audio_quality(video_path, snr_min, snr_edit, speech_min, speech_max, noise_min, expect_keys):
    output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

    result_json = check_video_audio_quality(
        file_path=video_path,
        min_snr_value=snr_min,
        min_snr_value_edit=snr_edit,
        min_speech_level=speech_min,
        max_speech_level=speech_max,
        min_noise_level=noise_min,
        replace_audio=True,
        output_video_path=output_path
    )

    result = json.loads(result_json)
    for key in expect_keys:
        assert key in result
    assert os.path.exists(result["output_video"])
    os.remove(result["output_video"])  # cleanup


@pytest.mark.parametrize("video_path, blur_thresh, max_frames", [
    ("tests/assets/sample_video_with_audio.mp4", 100.0, 10),
])
def test_check_video_image_quality(video_path, blur_thresh, max_frames):
    results, averages = check_video_image_quality(video_path, blur_thresh, max_frames)

    assert isinstance(results, list)
    assert "frame" in results[0]
    assert "blurry" in results[0]
    assert "entropy" in results[0]
    assert "niqe_score" in results[0]

    assert averages["frames_processed"] <= max_frames
    assert "average_blurry" in averages
    assert "average_entropy" in averages
    assert "average_niqe_score" in averages
