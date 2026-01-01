import json
from src.models.api2_models.task import SubmissionResult
from src.services.quality_assurance.video_parameter_check import (
    check_video_file_format,
    check_video_file_length,
    check_video_frame_rate,
    check_video_bit_depth,
)
from src.services.quality_assurance.video_quality_check import (
    check_video_image_quality,
    check_video_audio_quality,
)
from src.services.task_distributor import assign_task, get_full_task_detail, Task
from src.utils.downloader import download_telegram
from loguru import logger


async def handle_video_submission(task_info, file_id, user_id, bot) -> SubmissionResult:
    """
    Handles the video submission for a given task.

    Args:
        task_info (dict): Dictionary containing details about the video task.
        file_id (str): Telegram file_id of the submitted video.
        user_id (int): ID of the user submitting the video.
        bot (Bot): The bot instance for downloading the video.
    """
    task_info = Task(**task_info)
    # task_full_details = await get_full_task_detail(task_info.task_id)

    # Download video from Telegram
    file_path = await download_telegram(file_id, bot=bot)

    # Parameter checks

    if not check_video_file_format(file_path, expected_format="mp4"):
        logger.warning("Invalid video format.")
        return SubmissionResult(success=False,
                                response="Invalid video format. Only MP4 is supported.")

    if not check_video_file_length(file_path, min_length=1, max_length=300):
        logger.warning("Video length not within allowed range (1s–5min).")
        return SubmissionResult(success=False,
                                response="Video length not within allowed range (1s–5min).")

    if not check_video_frame_rate(file_path, expected_frame_rate=30):
        logger.warning("Invalid frame rate.")
        return SubmissionResult(success=False,
                                response="Invalid frame rate. Expected ~30 FPS.")

    if not check_video_bit_depth(file_path, expected_bit_depth=8):
        logger.warning("Unsupported video bit depth.")
        return SubmissionResult(success=False,
                                response= "Unsupported video bit depth. Expected 8-bit.")

    # Quality checks

    frame_results, averages = check_video_image_quality(
        video_path=file_path,
        blur_thresh=100.0,
        max_frames=50,
    )
    if averages.get("average_blurry", 0) > 0.5:  # more than 50% blurry frames
        logger.warning("Video rejected: too many blurry frames.")
        return SubmissionResult(success=False,
                                response="Video too blurry or unclear.")

    audio_report = check_video_audio_quality(file_path)
    try:
        audio_data = json.loads(audio_report)
        if "Low SNR" in audio_data.get("message", ""):
            logger.warning("Audio quality issue detected.")
            return SubmissionResult(success=False,
                                response=f"Audio issue: {audio_data['message']}")
    except Exception:
        logger.warning("Could not parse audio quality report.")
        return SubmissionResult(success=False,
                                response="Audio quality check failed.")

    # If all checks pass
    logger.info("Video passed all checks.")
    return SubmissionResult(success=True,
                            response="Video accepted and passed all checks.", 
                            metadata={"file_path": file_path})
