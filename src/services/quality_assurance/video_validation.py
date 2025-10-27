import json
from typing import Dict, Any, List
from loguru import logger
import cv2
from src.services.quality_assurance.video_quality_check import (
    check_video_image_quality,
    check_video_audio_quality,
)

from src.services.quality_assurance.video_parameter_check import (
    check_video_file_format,
    check_video_file_length,
    check_video_frame_rate,
    check_video_bit_depth,)

logger = logging.getLogger("video_validator")


def validate_video_input(video_path: str,
                         expected_format: str = "mp4",
                         min_length: float = 0.5,
                         max_length: float = 600.0,
                         expected_frame_rate: float = 30.0,
                         expected_bit_depth: int = 8,
                         blur_thresh: float = 100.0,
                         max_frames: int = 100,
                         min_snr_value: float = 40,
                         min_snr_value_edit: float = 30,
                         min_speech_level: float = -10,
                         max_speech_level: float = -30,
                         min_noise_level: float = -40) -> Dict[str, Any]:
    """
    Validate a given video file against quality criteria.

    Args:
        video_path (str): Path to the video file.
        expected_format (str): Expected video format (e.g., 'mp4').
        min_length (float): Minimum length of video (in seconds).
        max_length (float): Maximum length of video (in seconds).
        expected_frame_rate (float): Expected video frame rate (in FPS).
        expected_bit_depth (int): Expected video bit depth (e.g., 8).
        blur_thresh (float): Threshold for determining blurriness.
        max_frames (int): Maximum frames to analyze for image quality.
        min_snr_value (float): Minimum required Signal-to-Noise Ratio for audio quality.
        min_snr_value_edit (float): SNR value for post-editing audio quality.
        min_speech_level (float): Minimum speech level in dB.
        max_speech_level (float): Maximum speech level in dB.
        min_noise_level (float): Maximum allowed noise level in dB.

    Returns:
        dict: {
            "success": bool,
            "fail_reasons": list[str],
            "metadata": dict[str, any]
        }
    """
    fail_reasons: List[str] = []
    metadata: Dict[str, Any] = {}

    # --- 1. Video Format Check ---
    try:
        format_check = check_video_file_format(video_path, expected_format)
        metadata["format_check"] = format_check
        if not format_check:
            fail_reasons.append(f"Video format is not {expected_format}.")
    except Exception as e:
        logger.warning(f"Format check failed: {e}")

    # --- 2. Video Length Check ---
    try:
        length_check = check_video_file_length(
            video_path, min_length, max_length)
        metadata["length_check"] = length_check
        if not length_check:
            fail_reasons.append(
                f"Video length is outside the acceptable range ({min_length}s - {max_length}s).")
    except Exception as e:
        logger.warning(f"Length check failed: {e}")

    # --- 3. Frame Rate Check ---
    try:
        frame_rate_check = check_video_frame_rate(
            video_path, expected_frame_rate)
        metadata["frame_rate_check"] = frame_rate_check
        if not frame_rate_check:
            fail_reasons.append(
                f"Video frame rate does not match {expected_frame_rate} FPS.")
    except Exception as e:
        logger.warning(f"Frame rate check failed: {e}")

    # --- 4. Bit Depth Check ---
    try:
        bit_depth_check = check_video_bit_depth(video_path, expected_bit_depth)
        metadata["bit_depth_check"] = bit_depth_check
        if not bit_depth_check:
            fail_reasons.append(
                f"Video bit depth does not match {expected_bit_depth}.")
    except Exception as e:
        logger.warning(f"Bit depth check failed: {e}")

    # --- 5. Image Quality Check ---
    try:
        image_quality_results, image_quality_metadata = check_video_image_quality(
            video_path, blur_thresh, max_frames)
        metadata["image_quality_results"] = image_quality_results
        metadata["image_quality_metadata"] = image_quality_metadata
        if image_quality_metadata["average_blurry"] > 0.5:
            fail_reasons.append("Video contains too many blurry frames.")
        if image_quality_metadata["average_entropy"] < 3.0:
            fail_reasons.append(
                f"Video has low average entropy ({image_quality_metadata['average_entropy']:.2f}).")
        if image_quality_metadata["average_niqe_score"] > 6.0:
            fail_reasons.append(
                f"Video has high average NIQE score ({image_quality_metadata['average_niqe_score']:.2f}).")
    except Exception as e:
        logger.warning(f"Image quality check failed: {e}")

    # --- 6. Audio Quality Check ---
    try:
        audio_quality_report = check_video_audio_quality(
            file_path=video_path,
            min_snr_value=min_snr_value,
            min_snr_value_edit=min_snr_value_edit,
            min_speech_level=min_speech_level,
            max_speech_level=max_speech_level,
            min_noise_level=min_noise_level)
        metadata["audio_quality_report"] = audio_quality_report
        audio_data = json.loads(audio_quality_report)
        if audio_data.get("snr", 0) < min_snr_value:
            fail_reasons.append(
                f"Audio has low SNR ({audio_data['snr']:.2f}).")
        if audio_data.get("silence", 0) > 0.1:
            fail_reasons.append(
                f"Audio has excessive silence ({audio_data['silence']:.2f}).")
    except Exception as e:
        logger.warning(f"Audio quality check failed: {e}")

    # Final Success Check
    return {
        "success": len(fail_reasons) == 0,
        "fail_reasons": fail_reasons,
        "metadata": metadata
    }
