from typing import Dict, Optional, Tuple
from aiogram.types import URLInputFile, Message
from aiogram.fsm.context import FSMContext
from loguru import logger

from aiogram.types import CallbackQuery
from typing import Optional, List

from src.constant.task_constants import ReviewerTaskStatus
from src.keyboards.inline import next_task_inline_kb, review_task_inline_kb
from src.models.api2_models.projects import ReviewerTaskRequestModel
from src.models.api2_models.reviewer import ReviewModel, ReviewSubmissionResponse, ReviewerAllocation, ReviewerTaskResponseModel
from src.models.api2_models.task import TaskDetailResponseModel
from src.responses.task_formaters import REVIEWER_TASK_MSG
from src.handlers.task_handlers.utils import extract_project_info, format_submission
from src.services.server.api2_server.projects import get_project_tasks_assigned_to_reviewer
from src.services.server.api2_server.reviewer import submit_review_details


async def fetch_reviewer_tasks(project_info, status=ReviewerTaskStatus.PENDING) -> Optional[List[ReviewerAllocation]]:
    """Retrieve allocated tasks for the reviewer."""

    task_request = ReviewerTaskRequestModel(
        project_id=project_info["id"],
        reviewer_email=project_info["email"],
        status=[status],
        # status=[ReviewerTaskStatus.PENDING],
        limit=50
    )

    allocations = await get_project_tasks_assigned_to_reviewer(task_request)

    # all_allocation = allocations.allocations

    # if status == ReviewerTaskStatus.REDO:
    #     new_allocation = []
    #     for allocate in all_allocation:
    #         if allocate.reviewed_at is not None:
    #             new_allocation.append(allocate)
    #             break
    #     return new_allocation

    # elif status == ReviewerTaskStatus.PENDING:
    #     new_allocation = []
    #     for allocate in all_allocation:
    #         if allocate.reviewed_at is None:
    #             new_allocation.append(allocate)
    #             break
    #     return new_allocation

    logger.trace(f"Fetched allocations: {allocations}")
    new_allocations = []

    for allocate in allocations.allocations:
        if allocate.reviewed_at is None:
            new_allocations.append(allocate)

    return new_allocations


async def handle_reviewer_task_start(
    callback: CallbackQuery,
    state: FSMContext,
    status_filter: Optional[str],
    no_tasks_message: str,
):
    """
    Reusable function to handle the core logic of fetching, sending, and updating
    state for reviewer tasks.
    """
    user_data = await state.get_data()
    # Ensure extract_project_info is awaited if necessary
    project_info = extract_project_info(user_data)

    # 1. Validation check
    if not project_info or not project_info.get("email") or not project_info.get("id"):
        await callback.message.answer("Please select a project first using /project.")
        return

    # 2. Fetch tasks using the provided status filter
    allocations = await fetch_reviewer_tasks(project_info, status=status_filter)

    # 3. Check for available tasks
    if len(allocations) == 0:
        await callback.message.answer(no_tasks_message)
        return

    first_task = allocations[0]

    # 4. Send the task and update state
    await send_reviewer_task(callback.message, first_task, project_info)

    await state.update_data({
        "project_id": project_info["id"],
        "submission_id": str(first_task.submission_id)
    })


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

        logger.debug(f"Sending audio file from URL: {first_task.file_url}")
        logger.debug(f"With caption: {caption}")
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

    if result:
        await callback.message.answer(
            "✅ Review submitted successfully!"
        )
        await complete_review_response(callback.message, state_data)
        return True

    await callback.message.answer("❌ Failed to submit review. Please try again later.")
    return False
