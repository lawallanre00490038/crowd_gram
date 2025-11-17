from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import URLInputFile
from loguru import logger

from src.constant.task_constants import ContributorTaskStatus
from src.models.api2_models.agent import SubmissionModel
from src.keyboards.inline import next_task_inline_kb
from src.routes.task_routes.task_formaters import ERROR_MESSAGE
from src.services.quality_assurance.text_validation import validate_text_input
from src.states.tasks import TaskState
from src.services.server.api2_server.agent_submission import create_submission
from src.handlers.task_handlers.audio_task_handler import handle_api2_audio_submission
from src.handlers.task_handlers.utils import extract_project_info, fetch_user_tasks, get_first_task, set_task_state_by_type, update_state_with_task, build_redo_task_message
from src.responses.task_formaters import SUBMISSION_RECIEVED_MESSAGE


router = Router()


@router.callback_query(F.data == "start_agent_redo_task")
async def start_task(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        project_info = extract_project_info(user_data)
        if not project_info:
            await callback.message.answer("Please select a project first using /start.")
            return

        allocations = await fetch_user_tasks(project_info, status=ContributorTaskStatus.REDO)

        if not (allocations and getattr(allocations, "allocations", None)):
            await callback.message.answer("No tasks to REDO at the moment...")
            return

        first_task = get_first_task(allocations)
        logger.trace(f"First redo task: {first_task}")
        if not first_task:
            await callback.message.answer("No tasks to REDO at the moment...")
            return

        task_msg, task_type = build_redo_task_message(
            first_task, project_info["instruction"], project_info["return_type"])

        if first_task.submission.type == "audio":
            audio_file = URLInputFile(first_task.submission.file_url)

            await callback.message.answer_audio(
                caption=task_msg,
                audio=audio_file,
                parse_mode="HTML",
                protect_content=True
            )
        else:
            await callback.message.answer(
                task_msg,
                parse_mode="HTML"
            )

        await update_state_with_task(state, project_info, first_task, task_type, task_msg, redo_task=True)
        await set_task_state_by_type(callback.message, state)

    except Exception as e:
        logger.error(f"Error in start_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")
