import logging
from typing import Optional
import aiohttp

from src.config import BASE_URL_V2
from src.models.api2_models.task import TaskModel, TaskListResponseModel, TaskAllocation, PromptInfoModel, SubmissionInfoModel, ReviewInfoModel


logger = logging.getLogger(__name__)


async def get_task(task_id: str) -> Optional[TaskModel]:
    """Fetch a task by its ID.

    Args:
        task_id (str): The ID of the task to fetch.

    Returns:
        Optional[TaskModel]: The fetched task or None if not found.
    """
    url = f"{BASE_URL_V2}/agent/{task_id}/read"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                task_result = await response.json()

                if response.status == 200:
                    return TaskModel.model_validate(task_result['data'])
                else:
                    logger.error(f"Failed to fetch task: {task_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during fetching task: {str(e)}")
        return None
    
async def get_all_tasks() -> Optional[TaskListResponseModel]:
    """Fetch all tasks.

    Returns:
        Optional[TaskListResponseModel]: The list of all tasks or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/agent/read/all"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return TaskListResponseModel.model_validate(tasks_result['data'])
                else:
                    logger.error(f"Failed to fetch tasks: {tasks_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during fetching tasks: {str(e)}")
        return None
    
async def update_task(task_data: dict) -> Optional[TaskModel]:
    """Update a task.

    Args:
        task_data (dict): A dictionary containing the task data to update.

    Returns:
        Optional[TaskModel]: The updated task or None if the update fails.
    """
    url = f"{BASE_URL_V2}/agent/{task_data['task_id']}/update"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=task_data['data']) as response:
                update_result = await response.json()

                if response.status == 200:
                    return TaskModel.model_validate(update_result['data'])
                else:
                    logger.error(f"Failed to update task: {update_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during updating task: {str(e)}")
        return None
    
