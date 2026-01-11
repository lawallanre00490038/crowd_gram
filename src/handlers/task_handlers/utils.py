from calendar import c
from typing import List, Optional, Tuple, Union
from loguru import logger
from src.models.api2_models.projects import ContributorRole, ExtractedProjectInfo, ProjectReviewerDetailsResponseModel, ProjectTaskDetailsResponseModel, ProjectTaskRequestModel, ReviewerTaskRequestModel, UserProjectState
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


def extract_project_info(user_data: dict) -> Optional[ExtractedProjectInfo]:
    """
    Extract and validate project details from user data using Pydantic.
    Returns None if validation fails.
    """
    try:
        state = UserProjectState.model_validate(user_data)

        logger.info(f"This is the project info: {state.project_index}")

        project = state.projects_details[state.project_index]

        return ExtractedProjectInfo(
            email=state.user_email,
            id=str(project.id),
            name=project.name,
            reviewer_instructions=project.reviewer_instructions,
            instruction=project.agent_instructions,
            return_type=project.return_type,
            require_geo=project.require_geo,
            max_submit = user_data.get("max_submit"),
            cur_submit = user_data.get("cur_submit")
        )

    except Exception as e:
        logger.error(f"Error in task processing: {str(e)}")
        return None

async def fetch_user_tasks(project_info: ExtractedProjectInfo, status=ContributorTaskStatus.ASSIGNED, skip = 0) -> Optional[List[TaskDetailResponseModel]]:
    """Retrieve allocated tasks for the user."""
    task_request = ProjectTaskRequestModel(
        agent_email = project_info.email,
        project_id=project_info.id,
        status=[status],
        skip=skip
    )

    logger.trace(f"Fetching tasks with request: {task_request}")

    allocations = await get_project_tasks_assigned_to_user(task_request)
    logger.trace(f"Fetched allocations: {allocations}")

    if allocations == None:
        return None
    
    return allocations.allocations  



async def update_state_with_task(state, project_info: ExtractedProjectInfo, task: TaskDetailResponseModel, task_type, task_msg, redo_task=False):
    """Store task info in FSM state."""
    await state.update_data(
        project_id=project_info.id,
        task_id=task.task_id,
        agent_allocation_id=task.agent_allocation_id,
        sentence_id=task.sentence_id,
        task_type=task_type,
        task=task_msg,
        redo_task=redo_task,
        max_submit=task.max_submissions_allowed,
        cur_submit=task.current_submission_count,
    )
    await state.set_state(TaskState.working_on_task)


async def set_task_state_by_type(message: Message, state: FSMContext, task_type=None):
    try:
        user_data = await state.get_data()
        type = user_data.get("task_type")
        if type == None:
            return
        
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
        return first_task.payload_text
    return build_file_section(submission_type, first_task.file_url)
