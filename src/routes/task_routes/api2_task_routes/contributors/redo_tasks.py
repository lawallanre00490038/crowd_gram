from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from src.constant.task_constants import ContributorTaskStatus
from src.handlers.task_handlers.contributor_handler import build_redo_task_message, process_and_send_task


router = Router()

@router.callback_query(F.data == "start_agent_redo_task")
async def start_task_redo(callback: CallbackQuery, state: FSMContext):
    await process_and_send_task(
        callback=callback,
        state=state,
        # Specific parameters for REDO task
        status_filter=ContributorTaskStatus.REDO,
        no_tasks_message="No tasks to REDO at the moment...",
        project_not_selected_message="Please select a project first using /start.", # Different message for REDO
        build_msg_func=build_redo_task_message,
        is_redo_task=True,
    )
