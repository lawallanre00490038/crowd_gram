from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
import logging

from src.services.server.api2_server.task import get_task, get_all_tasks, update_task
from src.models.api2_models.task import TaskModel, TaskListResponseModel, TaskAllocation, PromptInfoModel, SubmissionInfoModel, ReviewInfoModel
from src.keyboards.inline import start_task_inline_kb
from src.states.task_state import TaskState



logger = logging.getLogger(__name__)


router = Router()


@router.callback_query(F.data.startswith("proj_"))
async def handle_project_selection(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        project_index = int(callback.data.split("_")[1])
        user_data = await state.get_data()
        projects = user_data.get("projects_list", [])
        
        if 0 <= project_index < len(projects):
            selected_project = projects[project_index]
            await state.update_data(selected_project=selected_project)
            await callback.message.answer(f"Welcome to {selected_project} project! You can now start working on tasks.", reply_markup=start_task_inline_kb())
            await state.set_state(TaskState.waiting_for_task)
        else:
            await callback.message.answer("Invalid project selection. Please try again.")
    except Exception as e:
        logger.error(f"Error in handle_project_selection: {str(e)}")
        await callback.answer("Error occurred, please try again")