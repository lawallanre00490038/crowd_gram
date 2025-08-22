import logging
import librosa
from src.utils.parameters import UserParams

from src.services.task_distributor import assign_task, get_full_task_detail, TranslationTask
from src.services.quality_assurance.audio_parameter_check import check_audio_parameter, TaskParameterModel
from src.services.quality_assurance.audio_quality_check import check_audio_quality
from src.utils.save_audio import save_librosa_audio_as_mp3

from src.responses.task_formaters import (TEXT_TASK_PROMPT, SELECT_TASK_TO_PERFORM,
    APPROVED_TASK_MESSAGE, ERROR_MESSAGE, SUBMISSION_RECIEVED_MESSAGE)

from src.utils.downloader import download_telegram
from src.constant.auth_constants import TOKEN_LOCATION


logger = logging.getLogger(__name__)

async def handle_audio_submission(task_info, file_id, user_id, bot):
    """
    Handles the audio submission for a given task.

    Args:
        task (Task): The task object containing details about the audio task.
        submission (Submission): The submission object containing the audio data.
    """

    task_info = TranslationTask(**task_info) 
    task_full_details = await get_full_task_detail(task_info.task_id)

    file_path = await download_telegram(file_id, bot=bot)
    parameters = TaskParameterModel(min_duration= task_full_details.min_duration.total_seconds(), 
                    max_duration = task_full_details.max_duration.total_seconds(),
                    language = task_full_details.required_language, 
                    expected_format = "oga",
                    sample_rate = 48000,
                    bit_depth = 32)
    
    response = check_audio_parameter(file_path, parameters)

    data, sr = librosa.load(file_path, sr=None)

    new_audio, quality_response = check_audio_quality(data = data, sr = sr)
    
    new_path = file_path.replace(".oga", "_enhanced.oga")

    save_librosa_audio_as_mp3(new_audio, sr, new_path)

    logger.info(f"New audio saved at {new_path}")
    logger.info(f"Audio check result for user {user_id}: {response.is_valid}, errors: {response.errors}, {quality_response}")

    if response.is_valid and (quality_response["message"] == "Approved"):
        return APPROVED_TASK_MESSAGE
    else:
        errors = ""

        if not response.is_valid:
            errors = "\n".join(response.errors)
        if quality_response["message"] != "Approved": 
            errors += f"\nQuality check message: {quality_response['message']}"
        errors = ERROR_MESSAGE.format(errors=errors)

        logger.info(f"Audio submission failed for user {user_id}: {errors}")

        return errors
    