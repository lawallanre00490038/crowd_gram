from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
import logging

from src.keyboards.inline import start_agent_task_inline_kb, start_reviewer_task_inline_kb
from src.responses.project_responses import PROJECT_FULL_WELCOME_MSG

from src.states.tasks import TaskState



logger = logging.getLogger(__name__)


router = Router()


@router.callback_query(F.data.startswith("proj_"))
async def handle_project_selection(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        project_index = int(callback.data.split("_")[1])
        user_data = await state.get_data()
        projects_details = user_data.get("projects_details", [])
        role = user_data.get('role')
        
        if 0 <= project_index < len(projects_details):
            selected_project = projects_details[project_index]
            await state.update_data(project_index=project_index)
            if role == "agent":
                    user_type = "Agent"
                    agent_coin = selected_project.get("agent_coin", 0.0)
                    welcome_message = PROJECT_FULL_WELCOME_MSG.format(
                        project_name=selected_project.get("name", "Unknown Project"),
                        project_instruction=selected_project.get("agent_instructions", "No instructions provided."),
                        user_type=user_type,
                        user_coin=agent_coin,
                        total_tasks=selected_project.get("total_tasks", 0)
                    )
                    await callback.message.answer(welcome_message, reply_markup=start_agent_task_inline_kb())
            elif role == "reviewer":
                    user_type = "Reviewer"
                    reviewer_coin = selected_project.get("reviewer_coin", 0.0)
                    welcome_message = PROJECT_FULL_WELCOME_MSG.format(
                        project_name=selected_project.get("name", "Unknown Project"),
                        project_instruction=selected_project.get("reviewer_instructions", "No instructions provided."),
                        user_type=user_type,
                        user_coin=reviewer_coin
                    )
                    await callback.message.answer(welcome_message, reply_markup=start_reviewer_task_inline_kb())
        else:
            await callback.message.answer("Invalid project selection. Please try again.")
    except Exception as e:
        logger.error(f"Error in handle_project_selection: {str(e)}")
        await callback.answer("Error occurred, please try again")

