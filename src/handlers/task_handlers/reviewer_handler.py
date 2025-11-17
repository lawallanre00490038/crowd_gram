from typing import Optional, Tuple
from aiogram.types import URLInputFile, Message
from loguru import logger

from src.keyboards.inline import review_task_inline_kb
from src.models.api2_models.reviewer import ReviewerAllocation, ReviewerTaskResponseModel
from src.models.api2_models.task import TaskDetailResponseModel
from src.responses.task_formaters import REVIEWER_TASK_MSG
from src.handlers.task_handlers.utils import format_submission


async def send_reviewer_task(message: Message, first_task: ReviewerAllocation, project_info):
    """
    Sends a reviewer task message with appropriate formatting depending on submission type.

    Args:
        message: Telegram message object (used to send messages).
        first_task: The first task object containing submission and prompt info.
        project_info: Dict containing project details (e.g., name, reviewer_instructions).
    """

    submission = format_submission(first_task, project_info["return_type"])

    caption = REVIEWER_TASK_MSG['intro'].format(
        project_name=project_info["name"],
        submission_type=project_info["return_type"],
        payload_text=first_task.sentence,
        submission=submission,
        reviewer_instruction=project_info["reviewer_instructions"]
    )

    logger.trace(f"Caption: {caption}")

    if project_info["return_type"] == "audio":

        audio_file = URLInputFile(str(first_task.file_url))
        await message.answer_audio(
            caption=caption,
            audio=audio_file,
            parse_mode="HTML",
            protect_content=True,
            reply_markup=review_task_inline_kb()
        )
    else:
        await message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=review_task_inline_kb()
        )


def prepare_reviewer_state(allocations: ReviewerAllocation):
    """
    Convert Pydantic objects to dicts for FSM state storage.
    """
    return {
        "reviewers_list": allocations.reviewer_allocation_id,
        "submission_id": allocations.submission_id,
        "reviewer_id": allocations.reviewer_id,
    }
