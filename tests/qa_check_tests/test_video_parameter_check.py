import pytest
from src.services.quality_assurance.video_parameter_check import (
    check_video_file_format,
    check_video_file_length,
    check_video_frame_rate,
    check_video_bit_depth
)

@pytest.mark.parametrize("file_name, expected_format, expected_result", [
    ("movie.mp4", "mp4", True),
    ("clip.avi", "avi", True),
    ("recording.mkv", "mp4", False),   # mismatch
    ("scene.mov", None, True),        # any supported format accepted
    ("video.webm", "webm", True),
    ("animation.flv", None, True),
    ("document.txt", None, False),    # unsupported extension
    ("untitled", None, False),        # no extension
    ("Sample.MP4", "mp4", True),      # case-insensitive
    ("clip.webm", "avi", False),      # mismatch
])
def test_check_video_file_format(file_name, expected_format, expected_result):
    result = check_video_file_format(file_name, expected_format)
    assert result == expected_result


@pytest.mark.parametrize("file_path, min_len, max_len, expected", [
    ("tests/assets/sample_5s_30fps.mp4", 0.5, 600.0, True),
    ("tests/assets/sample_short.mp4", 1.0, 10.0, False),
    ("tests/assets/sample_long.mp4", 0.5, 4.0, False),
])
def test_check_video_file_length(file_path, min_len, max_len, expected):
    result = check_video_file_length(file_path, min_length=min_len, max_length=max_len)
    assert result == expected


@pytest.mark.parametrize("file_path, expected_fps, expected", [
    ("tests/assets/sample_5s_30fps.mp4", 30.0, True),
    ("tests/assets/sample_5s_24fps.mp4", 30.0, False),
    ("tests/assets/sample_5s_24fps.mp4", 24.0, True),
])
def test_check_video_frame_rate(file_path, expected_fps, expected):
    result = check_video_frame_rate(file_path, expected_frame_rate=expected_fps)
    assert result == expected


@pytest.mark.parametrize("file_path, expected_bit_depth, expected", [
    ("tests/assets/sample_8bit.mp4", 8, True),
    ("tests/assets/sample_8bit.mp4", 10, False),
    ("tests/assets/sample_8bit.mkv", 10, False),
    ("tests/assets/sample_8bit.mkv", 8, True),
])
def test_check_video_bit_depth(file_path, expected_bit_depth, expected):
    result = check_video_bit_depth(file_path, expected_bit_depth=expected_bit_depth)
    assert result == expected
