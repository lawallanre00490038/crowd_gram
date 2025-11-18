from typing import Dict, Optional, Tuple
from aiogram.types import URLInputFile, Message
from loguru import logger

from aiogram.types import CallbackQuery
from typing import Optional, List

from src.keyboards.inline import next_task_inline_kb, review_task_inline_kb
from src.models.api2_models.reviewer import ReviewModel, ReviewSubmissionResponse, ReviewerAllocation, ReviewerTaskResponseModel
from src.models.api2_models.task import TaskDetailResponseModel
from src.responses.task_formaters import REVIEWER_TASK_MSG
from src.handlers.task_handlers.utils import format_submission
from src.services.server.api2_server.reviewer import submit_review_details


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

async def extract_submission_id(data: dict) -> Optional[str]:
    """Extract submission_id from FSM data or fallback to reviewers_list."""
    submission_id = data.get("submission_id")
    if submission_id:
        return submission_id

    reviewers_list = data.get("reviewers_list", [])
    if reviewers_list:
        first_task = reviewers_list[0].get("tasks", [{}])[0]
        return (first_task.get("submission") or {}).get("submission_id")

    return None


async def build_review_model(data: dict, decision: str, comments: List[str]) -> Optional[ReviewModel]:
    """Build a ReviewModel safely with extracted submission_id."""
    submission_id = await extract_submission_id(data)
    if not submission_id:
        return None

    return ReviewModel(
        submission_id=str(submission_id),
        project_id=str(data.get("project_id")),
        reviewer_identifier=data.get("user_email"),
        decision=decision,
        reviewer_comments=comments,
    )

async def complete_review_response(message: Message, user_data: Dict):
    redo_task = user_data.get("redo_task", False)
    if redo_task:
        await message.answer("Begin the next redo review task.", reply_markup=next_task_inline_kb(user_type="reviewer", task_type="redo"))
    else:
        await message.answer("Begin the next review task.", reply_markup=next_task_inline_kb(user_type="reviewer", task_type="task"))


async def process_review_submission(
    callback: CallbackQuery,
    state_data: dict,
    decision: str,
    comments: List[str]
):
    """Shared logic for submitting review and handling responses."""

    review_data = await build_review_model(state_data, decision, comments)
    if not review_data:
        await callback.message.answer("⚠️ Missing submission ID. Cannot continue.")
        return False

    logger.trace(review_data)

    result: Optional[ReviewSubmissionResponse] = await submit_review_details(review_data)

    if result and result.submission_status:
        await callback.message.answer(
            "✅ Review submitted successfully!" if decision == "reject" else "✅ Review accepted successfully!"
        )
        await complete_review_response(callback.message, state_data.get("redo_task", False))
        return True

    await callback.message.answer("❌ Failed to submit review. Please try again later.")
    return False