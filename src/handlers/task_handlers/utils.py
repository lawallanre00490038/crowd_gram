from typing import List, Optional, Tuple, Union
from loguru import logger
from src.models.api2_models.projects import ContributorRole, ProjectReviewerDetailsResponseModel, ProjectTaskDetailsResponseModel, ProjectTaskRequestModel, ReviewerTaskRequestModel
from src.models.api2_models.reviewer import ReviewerAllocation, ReviewerTaskResponseModel
from src.models.api2_models.reviewer import ReviewerTaskResponseModel
from src.models.api2_models.task import TaskDetailResponseModel
from src.responses.task_formaters import TASK_MSG
from src.services.server.api2_server.projects import get_project_tasks_assigned_to_reviewer, get_project_tasks_assigned_to_user
from src.states.tasks import TaskState
from src.constant.task_constants import ContributorTaskStatus, ReviewerTaskStatus
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.utils.file_url_handlers import build_file_section


def extract_project_info(user_data: dict):
    """Extract and validate project details from user data."""
    email = user_data.get("user_email")
    project_index = user_data.get("project_index")
    projects = user_data.get("projects_details")

    if not (email and projects and 0 <= project_index < len(projects)):
        return None

    project = projects[project_index]
    return {
        "email": email,
        "id": project["id"],
        "name": project.get('name'),
        'reviewer_instructions': project.get(
            'reviewer_instructions', 'No specific instructions provided.'),
        "instruction": project.get("agent_instructions", "Please translate carefully."),
        "return_type": project.get("return_type", "text"),
    }


async def fetch_user_tasks(project_info, status=ContributorTaskStatus.ASSIGNED) -> Optional[ProjectTaskDetailsResponseModel]:
    """Retrieve allocated tasks for the user."""
    task_request = ProjectTaskRequestModel(
        agent_email = project_info["email"],
        project_id=project_info["id"],
        status=[status]
    )

    logger.trace(f"Fetching tasks with request: {task_request}")

    allocations = await get_project_tasks_assigned_to_user(task_request)
    logger.trace(f"Fetched allocations: {allocations}")
    return allocations.allocations


async def update_state_with_task(state, project_info, task: TaskDetailResponseModel, task_type, task_msg, redo_task=False):
    """Store task info in FSM state."""
    await state.update_data(
        project_id=project_info["id"],
        task_id=task.task_id,
        agent_allocation_id=task.agent_allocation_id,
        sentence_id=task.sentence_id,
        task_type=task_type,
        task=task_msg,
        redo_task=redo_task
    )
    await state.set_state(TaskState.working_on_task)


async def set_task_state_by_type(message: Message, state: FSMContext, task_type=None):
    try:
        user_data = await state.get_data()
        type = user_data.get("task_type")
        if type.lower() == "audio":
            await state.set_state(TaskState.waiting_for_audio)
        elif type.lower() == "text":
            await state.set_state(TaskState.waiting_for_text)
        elif type.lower() == "image":
            await state.set_state(TaskState.waiting_for_image)
        elif type.lower() == "video":
            await state.set_state(TaskState.waiting_for_video)
        else:
            logger.error(f"Unknown task type: {type}")
            return
    except Exception as e:
        logger.error(f"Error in handle_task_submission: {str(e)}")
        await message.answer("Error occurred, please try again.")

    return


def format_submission(first_task: ReviewerAllocation, submission_type: str):
    """
    Return the proper submission content based on type.
    """
    if submission_type == "text":
        return first_task.submitted_text
    return build_file_section(submission_type, first_task.file_url)
