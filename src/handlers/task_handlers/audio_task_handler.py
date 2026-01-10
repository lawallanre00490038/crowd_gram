import os
import librosa
from typing import List
from loguru import logger

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.models.api2_models.task import SubmissionResult
from src.utils.parameters import UserParams
from src.states.tasks import AudioTaskSubmission
from src.utils.downloader import download_telegram
from src.states.test_knowledge import TestKnowledge
from src.constant.auth_constants import TOKEN_LOCATION
from src.utils.save_audio import save_librosa_audio_as_mp3
from src.services.task_distributor import assign_task, get_full_task_detail, Task
from src.services.quality_assurance.audio_quality_check import check_audio_quality
from src.services.quality_assurance.audio_parameter_check import check_audio_parameter, TaskParameterModel
from src.responses.task_formaters import (TEXT_TASK_PROMPT, SELECT_TASK_TO_PERFORM,
                                          APPROVED_TASK_MESSAGE, ERROR_MESSAGE, SUBMISSION_RECIEVED_MESSAGE)

# --- TestKnowledge (quiz) ---


async def send_audio_question_test_knowledge(
    message: Message,
    state: FSMContext,
    audio_quiz_data: List,
    audio_tasks: list
):
    data = await state.get_data()
    q_index = int(data.get("current_aq", 0))
    target_lang = data.get("target_language", "Yoruba")

    logger.debug(
        "send_audio_question_test_knowledge: q_index=%s target_lang=%s total_quiz=%d sampled=%d",
        q_index, target_lang, len(
            audio_quiz_data or []), len(audio_tasks or [])
    )

    if not audio_quiz_data:
        logger.warning("No audio quiz data available")
        await message.answer("❌ No audio quiz data available")
        return

    if q_index >= len(audio_tasks):
        logger.warning(
            "Audio question index out of range: q_index=%d len=%d", q_index, len(audio_tasks))
        await message.answer("❌ Audio question index out of range")
        return

    selected = audio_tasks[q_index]
    logger.info(
        "Sending quiz question idx=%d | theme=%s",
        q_index, selected.get("theme")
    )

    await message.answer(
        f"🎧 Theme: {selected['theme']}\n\n"
        f"📋 Instruction: {selected['instruction']}\n"
        f"💡 Example guidance: {selected['example_prompt']}\n\n"
        f"Please send a **voice note or audio file** in **{target_lang}** (10–20 seconds)."
    )

    logger.debug("Setting state -> TestKnowledge.audio_quiz_submission")
    await state.set_state(TestKnowledge.audio_quiz_submission)


# --- Actual tasks (single assignment ---
async def send_audio_question_actual_tasks(
    message: Message,
    state: FSMContext,
    *,
    task: Task,             # Pydantic model
    state_key_task_id: str = "current_task_id",
    state_key_target_lang: str = "target_language",
    default_duration_text: str = "10–20 seconds",
    show_meta: bool = True,
) -> None:
    """
    Send a single assigned audio task prompt.
    Stores minimal FSM state (task id + target language) and moves to waiting_for_audio.
    """
    logger.debug(
        "send_audio_question_actual_tasks: task_id=%s required_language=%s",
        task.task_id, task.required_language
    )

    language = (task.required_language or "English").strip()

    # Persist minimal state for the real-task flow
    await state.update_data(
        {
            state_key_task_id: task.task_id,
            state_key_target_lang: language,
        }
    )
    logger.info(
        "FSM updated for actual task | %s=%s, %s=%s",
        state_key_task_id, task.task_id, state_key_target_lang, language
    )

    # Build prompt
    theme = (task.task_type or task.category or "Audio Task").strip()
    instruction = (
        task.task_instructions or task.task_description or "Record a short audio sample.").strip()
    description = (task.task_description or "No description provided.").strip()
    duration_text = default_duration_text

    meta_line = ""
    if show_meta:
        bits = []
        if task.rewards:
            bits.append(f"💰 Reward: {task.rewards}")
        if task.deadline:
            bits.append(f"🕒 Deadline: {task.deadline}")
        if task.extend_deadline:
            bits.append(f"➕ Extend: {task.extend_deadline}")
        if bits:
            meta_line = "\n" + " · ".join(bits)
            logger.debug("Meta line for task %s: %s",
                         task.task_id, meta_line.replace("\n", " "))

    # Send message
    logger.info("Sending actual-task prompt | task_id=%s theme=%s",
                task.task_id, theme)
    await message.answer(
        f"🎧 Theme: {theme}\n\n"
        f"📋 Instruction: {instruction}\n"
        f"💡 Description: {description}\n"
        f"⏱ Duration: {duration_text}{meta_line}\n\n"
        f"Please send a **voice note or audio file** in **{language}**."
    )

    # Advance state
    logger.debug("Setting state -> AudioTaskSubmission.waiting_for_audio")
    await state.set_state(AudioTaskSubmission.waiting_for_audio)


async def handle_audio_submission(task_info, file_id, user_id, bot):
    """
    Handles the audio submission for a given task.

    Args:
        task (Task): The task object containing details about the audio task.
        submission (Submission): The submission object containing the audio data.
    """

    task_info = Task(**task_info)
    task_full_details = await get_full_task_detail(task_info.task_id, user_id)

    file_path = await download_telegram(file_id, bot=bot)
    parameters = TaskParameterModel(min_duration=task_full_details.min_duration.total_seconds(),
                                    max_duration=task_full_details.max_duration.total_seconds(),
                                    language=task_full_details.required_language,
                                    expected_format="oga",
                                    sample_rate=48000,
                                    bit_depth=32)

    response = check_audio_parameter(file_path, parameters)

    data, sr = librosa.load(file_path, sr=None)

    new_audio, quality_response = check_audio_quality(data=data, sr=sr)

    new_path = file_path.replace(".oga", "_enhanced.oga")

    save_librosa_audio_as_mp3(new_audio, sr, new_path)

    logger.info(f"New audio saved at {new_path}")
    logger.info(
        f"Audio check result for user {user_id}: {response.is_valid}, errors: {response.errors}, {quality_response}")

    if response.is_valid and (quality_response["message"] == "Approved"):
        return True, APPROVED_TASK_MESSAGE
    else:
        errors = ""

        if not response.is_valid:
            errors = "\n".join(response.errors)
        if quality_response["message"] != "Approved":
            errors += f"\nQuality check message: {quality_response['message']}"
        errors = ERROR_MESSAGE.format(errors=errors)

        logger.info(f"Audio submission failed for user {user_id}: {errors}")

        return False, errors

async def handle_api2_audio_submission(task_info, file_id, user_id, bot) -> SubmissionResult:
    """
    Handles the audio submission for a given task.

    Args:
        task (Task): The task object containing details about the audio task.
        submission (Submission): The submission object containing the audio data.
    """

    file_path = await download_telegram(file_id, bot=bot)
    parameters = TaskParameterModel(min_duration=3,
                                    max_duration=20,
                                    language="English",
                                    expected_format="oga",
                                    sample_rate=48000,
                                    bit_depth=32)

    response = check_audio_parameter(file_path, parameters)

    data, sr = librosa.load(file_path, sr=None)

    new_audio, quality_response = check_audio_quality(data=data, sr=sr)

    new_path = file_path.replace(".oga", "_enhanced.oga")

    save_librosa_audio_as_mp3(new_audio, sr, new_path)

    os.remove(file_path)    

    logger.info(f"New audio saved at {new_path}")
    logger.info(
        f"Audio check result for user {user_id}: {response.is_valid}, errors: {response.errors}, {quality_response}")

    if response.is_valid and (quality_response["message"] == "Approved"):
        return SubmissionResult(
            success=True,
            response=APPROVED_TASK_MESSAGE,
            metadata={"new_path": new_path}
        )
    else:
        errors = ""

        if not response.is_valid:
            errors = "\n *  ".join(response.errors)
        if quality_response["message"] != "Approved":
            errors += f"\n * Quality check: {quality_response['message']}"
        errors = ERROR_MESSAGE.format(errors=errors)

        logger.info(f"Audio submission failed for user {user_id}: {errors}")

        logger.info(f"Failed Audio submission file id: {file_id}")

        return SubmissionResult(
            success = False,
            response = errors,
            metadata =  {"new_path": new_path}
        )