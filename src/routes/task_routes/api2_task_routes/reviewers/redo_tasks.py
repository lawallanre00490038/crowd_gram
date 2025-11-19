from loguru import logger
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.models.api2_models.projects import ContributorRole
from src.constant.task_constants import ReviewerTaskStatus
from src.handlers.task_handlers.utils import extract_project_info
from src.handlers.task_handlers.reviewer_handler import handle_reviewer_task_start, send_reviewer_task, fetch_reviewer_tasks

router = Router()
@router.callback_query(F.data == "start_reviewer_redo_task")
async def start_reviewer_task(callback: CallbackQuery, state: FSMContext):
    try:
        await handle_reviewer_task_start(
            callback=callback,
            state=state,
            status_filter=ReviewerTaskStatus.REDO,
            no_tasks_message="No tasks to REDO at the moment..."
        )

        await state.update_data(redo_task=True)
    except Exception as e:
        logger.error(f"Error in start_reviewer_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")

    return