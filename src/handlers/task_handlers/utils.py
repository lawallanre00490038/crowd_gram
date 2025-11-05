from loguru import logger
from src.models.api2_models.projects import ProjectTaskRequestModel
from src.responses.task_formaters import TASK_MSG
from src.services.server.api2_server.projects import get_project_tasks_assigned_to_user
from src.states.tasks import TaskState


def _extract_project_info(user_data: dict):
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


async def _fetch_user_tasks(project_info):
    """Retrieve allocated tasks for the user."""
    task_request = ProjectTaskRequestModel(
        project_id=project_info["id"],
        email=project_info["email"],
        status="assigned"
    )
    allocations = await get_project_tasks_assigned_to_user(task_request)
    logger.trace(f"Fetched allocations: {allocations}")
    return allocations if allocations and getattr(allocations, "tasks", None) else None


async def _fetch_user_redo_tasks(project_info):
    """Retrieve allocated tasks for the user."""
    task_request = ProjectTaskRequestModel(
        project_id=project_info["id"],
        email=project_info["email"],
        status="assigned"
    )
    allocations = await get_project_tasks_assigned_to_user(task_request)
    logger.trace(f"Fetched allocations: {allocations}")
    return allocations if allocations and getattr(allocations, "tasks", None) else None


def _get_first_task(allocations):
    """Get the first available task from allocations."""
    tasks = getattr(allocations, "tasks", [])
    return tasks[0] if tasks else None


def _build_task_message(task, instruction, return_type):
    """Construct the appropriate message for the task type."""
    type_map = {
        "text": "Text",
        "audio": "Audio",
        "image": "Image",
        "video": "Video"
    }

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


async def _update_state_with_task(state, project_info, task, task_type, task_msg):
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
