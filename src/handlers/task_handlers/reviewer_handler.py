from typing import Optional, Tuple
from aiogram.types import URLInputFile, Message
from loguru import logger

from src.keyboards.inline import review_task_inline_kb
from src.models.api2_models.reviewer import ReviewerTaskResponseModel
from src.models.api2_models.task import TaskDetailResponseModel
from src.responses.task_formaters import REVIEWER_TASK_MSG
from src.handlers.task_handlers.utils import format_submission

async def send_reviewer_task(message: Message, first_task: ReviewerTaskResponseModel, project_info):
    """
    Sends a reviewer task message with appropriate formatting depending on submission type.

    Args:
        message: Telegram message object (used to send messages).
        first_task: The first task object containing submission and prompt info.
        project_info: Dict containing project details (e.g., name, reviewer_instructions).
    """

    task_text = first_task.prompt.sentence_text
    submission = format_submission(first_task)

    caption = REVIEWER_TASK_MSG['intro'].format(
        project_name=project_info["name"],
        submission_type=first_task.submission.type,
        payload_text=task_text,
        submission=submission,
        reviewer_instruction=project_info["reviewer_instructions"]
    )

    logger.trace(f"Task Submission Type: {first_task.submission.type}")

    if first_task.submission.type == "audio":
        audio_file = URLInputFile(first_task.submission.file_url)
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

def get_first_reviewer(
    allocations
) -> Tuple[Optional[ReviewerTaskResponseModel], Optional[TaskDetailResponseModel]]:
    """
    Returns the first reviewer and their first task, if available.

    Args:
        allocations: Object containing reviewer allocations.

    Returns:
        A tuple of (first_reviewer, first_task), or (None, None) if not found.
    """
    if not allocations or not getattr(allocations, 'reviewers', []):
        return None, None

    first_reviewer = allocations.reviewers[0]
    if not getattr(first_reviewer, 'tasks', []):
        return None, None

    first_task = first_reviewer.tasks[0]
    if getattr(first_task, 'submission', None) is None:
        return None, None

    return first_reviewer, first_task

def prepare_reviewer_state(reviewers_list):
    """
    Convert Pydantic objects to dicts for FSM state storage.
    """
    reviewers_list_dict = [reviewer.model_dump()
                           for reviewer in reviewers_list]
    first_task_dict = reviewers_list_dict[0].get("tasks", [{}])[0] if reviewers_list_dict else {}
    submission_dict = first_task_dict.get("submission") or {}

    return {
        "reviewers_list": reviewers_list_dict,
        "submission_id": submission_dict.get("submission_id"),
        "reviewer_id": reviewers_list_dict[0].get("reviewer_id"),
    }