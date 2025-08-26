from typing import Dict, Any, List, Optional
import logging


from .audio_parameter_check import (
    check_audio_parameter,
    TaskParameterModel,
    AudioCheckResult,
)

from .audio_quality_check import check_audio_quality

logger = logging.getLogger("audio_validator")


def validate_audio_input(
    audio_path: str,
    params: TaskParameterModel,
    *,
    try_enhance: Optional[int] = None,
    min_snr_value: Optional[float] = None,
    min_snr_value_edit: Optional[float] = None,
    min_speech_level: Optional[float] = None,
    max_speech_level: Optional[float] = None,
    min_noise_level: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Validate an audio file using ONLY the provided checks:
      - check_audio_parameter(path, params)  # wraps format/length/sample_rate/bit_depth
      - check_audio_quality(file_path=..., ...)

    Returns:
        {
            "success": bool,
            "fail_reasons": List[str],
            "metadata": Dict[str, Any]
        }
    """
    fail_reasons: List[str] = []
    metadata: Dict[str, Any] = {}

    # 1) Parameter bundle check (format, length, sample rate, bit depth)
    try:
        param_result: AudioCheckResult = check_audio_parameter(audio_path, params)
        metadata["parameter_is_valid"] = param_result.is_valid
        metadata["parameter_errors"] = list(param_result.errors or [])
        if not param_result.is_valid:
            # Extend fail reasons with the exact errors from aggregator
            fail_reasons.extend(param_result.errors)
    except Exception as e:
        logger.warning(f"Parameter check failed: {e}")
        fail_reasons.append("Audio parameter check failed.")

    # 2) Quality analysis + decision
    try:
        qa_kwargs = {}
        if try_enhance is not None:
            qa_kwargs["try_enhance"] = try_enhance
        if min_snr_value is not None:
            qa_kwargs["min_snr_value"] = min_snr_value
        if min_snr_value_edit is not None:
            qa_kwargs["min_snr_value_edit"] = min_snr_value_edit
        if min_speech_level is not None:
            qa_kwargs["min_speech_level"] = min_speech_level
        if max_speech_level is not None:
            qa_kwargs["max_speech_level"] = max_speech_level
        if min_noise_level is not None:
            qa_kwargs["min_noise_level"] = min_noise_level

        _, analysis = check_audio_quality(file_path=audio_path, **qa_kwargs)

        # Add metrics & message to metadata
        metadata.update({
            "snr_db": analysis.get("snr"),
            "silence_percent": analysis.get("silence"),
            "noise_power_db": analysis.get("noise_power"),
            "signal_power_db": analysis.get("signal_power"),
            "quality_message": analysis.get("message"),
        })

        # If message isn't "Approved", treat it as a failure reason
        if str(analysis.get("message", "")).strip().lower() != "approved":
            fail_reasons.append(str(analysis.get("message")))
    except Exception as e:
        logger.warning(f"Audio quality check failed: {e}")
        fail_reasons.append("Audio quality check failed.")

    return {
        "success": len(fail_reasons) == 0,
        "fail_reasons": fail_reasons,
        "metadata": metadata,
    }
