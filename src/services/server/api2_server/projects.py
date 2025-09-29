import logging
from typing import Optional
import aiohttp

from src.config import BASE_URL_V2
from src.models.api2_models.projects import Project, ProjectListResponseModel, ProjectTaskAllocationResponseModel, ProjectUpdateModel, ProjectTaskDetailsResponseModel, ReviewerProjectAssignedTasksResponseModel, ContributorProjectTaskRequestModel, ReviewerProjectAssignedTasksResponseModel

logger = logging.getLogger(__name__)


async def get_projects(project_data: dict) -> Optional[Project]:
    """Fetch a project by its ID.

    Args:
        project_data (dict): A dictionary containing the project ID.

    Returns:
        Optional[Project]: The fetched project or None if not found.
    """
    url = f"{BASE_URL_V2}/project/get/project"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=project_data) as response:
                project_result = await response.json()
                
                if response.status == 200:
                    return Project.model_validate(project_result['data'])
                else:
                    logger.error(f"Failed to fetch project: {project_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during fetching project: {str(e)}")
        return None
    
async def get_all_projects() -> Optional[ProjectListResponseModel]:
    """Fetch all projects.

    Returns:
        Optional[ProjectListResponseModel]: The list of all projects or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/project/list/projects"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                projects_result = await response.json()
                
                if response.status == 200:
                    return ProjectListResponseModel.model_validate(projects_result['data'])
                else:
                    logger.error(f"Failed to fetch projects: {projects_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during fetching projects: {str(e)}")
        return None
    
async def update_project(project_data: ProjectUpdateModel) -> Optional[Project]:    
    """Update a project.

    Args:
        project_data (ProjectUpdateModel): The project data to update.

    Returns:
        Optional[Project]: The updated project or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/project/update/project"
    
    try:
        async with aiohttp.ClientSession() as session:
            data = project_data.model_dump()
            async with session.put(url, json=data) as response:
                update_result = await response.json()
                
                if response.status == 200:
                    return Project.model_validate(update_result['data'])
                else:
                    logger.error(f"Failed to update project: {update_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during updating project: {str(e)}")
        return None
    

async def get_agent_project_assigned_tasks(project_data: ContributorProjectTaskRequestModel) -> Optional[ProjectTaskAllocationResponseModel]:
    """Fetch assigned tasks for a specific project.

    Args:
        project_data (ContributorProjectTaskRequestModel): The project data containing the project ID.
    Returns:
        Optional[ProjectAssignedTasksResponseModel]: The assigned tasks or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/project/{project_data.project_id}/tasks/agent"
    params = {**project_data.model_dump(exclude_none=True)}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return ProjectTaskAllocationResponseModel.model_validate(tasks_result['data'])
                else:
                    logger.error(f"Failed to fetch assigned tasks: {tasks_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during fetching assigned tasks: {str(e)}")
        return None


async def get_reviewer_project_assigned_tasks(project_data: ReviewerProjectAssignedTasksResponseModel) -> Optional[ProjectTaskAllocationResponseModel]:
    """Fetch assigned tasks for reviewers in a specific project.

    Args:
        project_data (ReviewerProjectAssignedTasksResponseModel): The project data containing the project ID.
    Returns:
        Optional[ReviewerProjectAssignedTasksResponseModel]: The assigned tasks for reviewers or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/project/{project_data.project_id}/tasks/reviewer"
    params = {**project_data.model_dump(exclude_none=True)}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return ProjectTaskAllocationResponseModel.model_validate(tasks_result['data'])
                else:
                    logger.error(f"Failed to fetch reviewer assigned tasks: {tasks_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during fetching reviewer assigned tasks: {str(e)}")
        return None

async def get_agent_project_task_details(project_data: ContributorProjectTaskRequestModel) -> Optional[ProjectTaskDetailsResponseModel]:
    """
    Fetch task details for a specific project.

    Args:
        project_data (ContributorProjectTaskRequestModel): The project data containing the project ID.
        
    Returns:
        Optional[ProjectTaskDetailsResponseModel]: The task details or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/project/{project_data.project_id}/tasks/agent/detailed"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return ProjectTaskDetailsResponseModel.model_validate(tasks_result['data'])
                else:
                    logger.error(f"Failed to fetch project task details: {tasks_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during fetching project task details: {str(e)}")
        return None


async def get_reviewer_project_task_details(project_data: ReviewerProjectAssignedTasksResponseModel) -> Optional[ReviewerProjectAssignedTasksResponseModel]:
    """Fetch task details for a specific project.

    Args:
        project_data (ReviewerProjectAssignedTasksResponseModel): The project data containing the project ID.

    Returns:
        Optional[ProjectTaskDetailsResponseModel]: The task details or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/project/{project_data.project_id}/tasks/reviewer/detailed"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return ReviewerProjectAssignedTasksResponseModel.model_validate(tasks_result['data'])
                else:
                    logger.error(f"Failed to fetch reviewer project task details: {tasks_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during fetching reviewer project task details: {str(e)}")
        return None