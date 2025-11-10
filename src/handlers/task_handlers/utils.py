from loguru import logger
from src.models.api2_models.projects import ProjectTaskRequestModel
from src.models.api2_models.task import TaskDetailResponseModel
from src.responses.task_formaters import TASK_MSG
from src.services.server.api2_server.projects import get_project_tasks_assigned_to_user
from src.states.tasks import TaskState
from src.constant.task_constants import ContributorTaskStatus
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.utils.file_url_handlers import build_file_section

type_map = {
    "text": "Text",
    "audio": "Audio",
    "image": "Image",
    "video": "Video"
}


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
        "instruction": project.get("agent_instructions", "Please translate carefully."),
        "return_type": project.get("return_type", "text"),
    }


async def fetch_user_tasks(project_info, status=ContributorTaskStatus.ASSIGNED):
    """Retrieve allocated tasks for the user."""
    task_request = ProjectTaskRequestModel(
        project_id=project_info["id"],
        email=project_info["email"],
        status=status
    )
    allocations = await get_project_tasks_assigned_to_user(task_request)
    logger.trace(f"Fetched allocations: {allocations}")
    return allocations if allocations and getattr(allocations, "tasks", None) else None


def get_first_task(allocations):
    """Get the first available task from allocations."""
    tasks = getattr(allocations, "tasks", [])
    return tasks[0] if tasks else None


def build_task_message(task, instruction, return_type):
    """Construct the appropriate message for the task type."""

    task_type = type_map.get(return_type)
    if not task_type:
        logger.error(f"Unknown task type for return_type={return_type}")
        task_type = "Unknown"

    task_text = getattr(task.prompt, "sentence_text",
                        "No task content provided.")

    task_msg = TASK_MSG["intro"].format(
        task_type=task_type,
        task_instruction=instruction,
        task_text=task_text
    )
    return task_msg, task_type


def build_redo_task_message(task: TaskDetailResponseModel, instruction, return_type):
    """Construct the appropriate message for the task type."""
    task_type = type_map.get(return_type)
    if not task_type:
        logger.error(f"Unknown task type for return_type={return_type}")
        task_type = "Unknown"

    task_text = getattr(task.prompt, "sentence_text", "No task content provided.")

    # Handle submission type
    if task.submission.type == "text":
        submission = task.submission.payload_text
    else:
        submission = build_file_section(task.submission.type, task.submission.file_url)

    # Handle missing review object
    if task.review is None or not task.review.reviewers:
        logger.error(f"Task review data missing for return_type={return_type}")
        reviewer_comment = "No reviewer comments available."
    else:
        reviewer_data = task.review.reviewers[0]
        reviewer_comments = reviewer_data.reviewer_comments

        # Ensure reviewer_comments is iterable
        if not reviewer_comments:
            reviewer_comment = "No comments provided."
        elif isinstance(reviewer_comments, str):
            reviewer_comment = reviewer_comments
        elif isinstance(reviewer_comments, (list, set, tuple)):
            reviewer_comment = "\n".join(str(c) for c in reviewer_comments)
        else:
            reviewer_comment = str(reviewer_comments)

    task_msg = TASK_MSG["redo_task"].format(
        task_type=task_type,
        task_instruction=instruction,
        task_text=task_text,
        previous_submission=submission,
        reviewer_comment=reviewer_comment
    )

    return task_msg, task_type



async def update_state_with_task(state, project_info, task, task_type, task_msg):
    """Store task info in FSM state."""
    await state.update_data(
        project_id=project_info["id"],
        task_id=task.task_id,
        assignment_id=task.assignment_id,
        prompt_id=task.prompt.prompt_id,
        sentence_id=task.prompt.sentence_id,
        task_type=task_type,
        task=task_msg
    )
    await state.set_state(TaskState.working_on_task)


async def set_task_state_by_type(message: Message, state: FSMContext):
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
