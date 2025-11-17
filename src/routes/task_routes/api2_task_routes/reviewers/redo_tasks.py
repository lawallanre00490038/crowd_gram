from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from typing import Optional

from loguru import logger

from aiogram.types import URLInputFile

from src.constant.task_constants import ContributorTaskStatus
from src.handlers.task_handlers.reviewer_handler import send_reviewer_task, prepare_reviewer_state
from src.handlers.task_handlers.utils import extract_project_info, fetch_reviewer_tasks, fetch_user_tasks, format_submission
from src.keyboards.inline import next_task_inline_kb, build_predefined_comments_kd, review_task_inline_kb, create_score_kb, summary_kb
from src.states.tasks import ReviewStates
from src.services.server.api2_server.projects import get_project_review_parameters, get_project_tasks_assigned_to_user
from src.services.server.api2_server.reviewer import submit_review_details
from src.responses.task_formaters import REVIEWER_TASK_MSG
from src.models.api2_models.projects import ContributorRole, ProjectTaskRequestModel
from src.utils.file_url_handlers import build_file_section
from src.models.api2_models.reviewer import ReviewModel, ReviewSubmissionResponse


router = Router()


@router.callback_query(F.data == "start_reviewer_redo_task")
async def start_reviewer_task(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        project_info = extract_project_info(user_data)

        if not project_info["email"] or not project_info["id"]:
            await callback.message.answer("Please select a project first using /project.")
            return

        allocations = await fetch_reviewer_tasks(project_info, status=ContributorTaskStatus.PENDING)

        logger.trace(f"Allocation: {allocations}")

        await send_reviewer_task(callback.message, allocations[0], project_info)

        if len(allocations) == 0:
            await callback.message.answer("No tasks to REDO at the moment...")
            return

        await send_reviewer_task(callback.message, allocations[0], project_info)

        # Update state
        state_data = prepare_reviewer_state(allocations[0])
        state_data.update(
            {"project_id": project_info["id"], "redo_task": True})
        await state.update_data(**state_data)

    except Exception as e:
        logger.error(f"Error in start_reviewer_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")

    return
