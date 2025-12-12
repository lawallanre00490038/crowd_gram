from loguru import logger
from typing import List, Optional
import aiohttp

from src.config import BASE_URL_V2
from src.models.api2_models.projects import (Project, ProjectListResponseModel, ProjectReviewerDetailsResponseModel, ProjectUpdateModel,
                                             ProjectTaskDetailsResponseModel, ProjectTaskRequestModel, ReviewAssignment, ReviewAssignmentsResponse, ReviewerTaskRequestModel, Submission)


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
                    return Project.model_validate(project_result)
                else:
                    logger.error(
                        f"Failed to fetch project: {project_result.get('message', 'Unknown error')}")
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
                    return ProjectListResponseModel.model_validate(projects_result)
                else:
                    logger.error(
                        f"Failed to fetch projects: {projects_result.get('message', 'Unknown error')}")
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
                    return Project.model_validate(update_result)
                else:
                    logger.error(
                        f"Failed to update project: {update_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during updating project: {str(e)}")
        return None

    # """Fetch assigned tasks for a specific project.

    # Args:
    #     project_data (ContributorProjectTaskRequestModel): The project data containing the project ID.
    # Returns:
    #     Optional[ProjectAssignedTasksResponseModel]: The assigned tasks or None if an error occurs.
    # """
    # url = f"{BASE_URL_V2}/project/{project_data.project_id}/tasks/agent"
    # params = {**project_data.model_dump(exclude_none=True)}

    # try:
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url, params=params) as response:
    #             tasks_result = await response.json()

    #             if response.status == 200:
    #                 return ProjectTaskAllocationResponseModel.model_validate(tasks_result)
    #             else:
    #                 logger.error(
    #                     f"Failed to fetch assigned tasks: {tasks_result.get('message', 'Unknown error')}")
    #                 return None
    # except Exception as e:
    #     logger.error(f"Exception during fetching assigned tasks: {str(e)}")
    #     return None

    # """
    # Fetch task details for a specific project.

    # Args:
    #     project_data (ContributorProjectTaskRequestModel): The project data containing the project ID.

    # Returns:
    #     Optional[ProjectTaskDetailsResponseModel]: The task details or None if an error occurs.
    # """
    # url = f"{BASE_URL_V2}/project/{project_data.project_id}/tasks/agent/detailed"

    # try:
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url) as response:
    #             tasks_result = await response.json()

    #             if response.status == 200:
    #                 return ProjectTaskDetailsResponseModel.model_validate(tasks_result)
    #             else:
    #                 logger.error(
    #                     f"Failed to fetch project task details: {tasks_result.get('message', 'Unknown error')}")
    #                 return None
    # except Exception as e:
    #     logger.error(
    #         f"Exception during fetching project task details: {str(e)}")
    #     return None

    # """Fetch task details for a specific project.

    # Args:
    #     project_data (ReviewerProjectAssignedTasksResponseModel): The project data containing the project ID.

    # Returns:
    #     Optional[ProjectTaskDetailsResponseModel]: The task details or None if an error occurs.
    # """
    # url = f"{BASE_URL_V2}/project/{project_data.project_id}/tasks/reviewer/detailed"

    # try:
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url) as response:
    #             tasks_result = await response.json()

    #             if response.status == 200:
    #                 return ReviewerProjectAssignedTasksResponseModel.model_validate(tasks_result)
    #             else:
    #                 logger.error(
    #                     f"Failed to fetch reviewer project task details: {tasks_result.get('message', 'Unknown error')}")
    #                 return None
    # except Exception as e:
    #     logger.error(
    #         f"Exception during fetching reviewer project task details: {str(e)}")
    #     return None


async def get_projects_details_by_user_email(user_email: str) -> Optional[ProjectListResponseModel]:
    """Fetch projects associated with a specific user email.

    Args:
        user_email (str): The user's email address.

    Returns:
        Optional[ProjectListResponseModel]: The list of projects or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/project/projects/by-email/{user_email}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                projects_result = await response.json()

                if response.status == 200:
                    return ProjectListResponseModel.model_validate(projects_result)
                else:
                    logger.error(
                        f"Failed to fetch projects by user email: {projects_result}")
                    return None
    except Exception as e:
        logger.error(
            f"Exception during fetching projects by user email: {str(e)}")
        return None


async def get_project_tasks_assigned_to_reviewer(task_details: ReviewerTaskRequestModel) -> Optional[ProjectReviewerDetailsResponseModel]:
    """Fetch project task allocations assigned to a specific reviewer.

    Args:
        task_details (ReviewerTaskRequestModel): The task details containing the user email.

    Returns:
        Optional[ProjectReviewerDetailsResponseModel]: The task allocations or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/results/{task_details.project_id}/reviewer-allocations"
    params = {**task_details.model_dump(exclude_none=True, mode="json")}
    logger.debug(
        f"Fetching project tasks from URL: {url} with params: {params}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return ProjectReviewerDetailsResponseModel.model_validate(tasks_result)
                else:
                    logger.error(
                        f"Failed to fetch project tasks allocations by user: {tasks_result}")
                    return None
    except Exception as e:
        logger.error(
            f"Exception during fetching project tasks allocations by user: {str(e)}")
        return None

async def get_task_submission(submission_id: str) -> Optional[Submission]:
    """Fetch project task allocations assigned to a specific reviewer.

    Args:
        task_details (ReviewerTaskRequestModel): The task details containing the user email.

    Returns:
        Optional[ProjectReviewerDetailsResponseModel]: The task allocations or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/submission/{submission_id}/agent".format(submission_id)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return Submission.model_validate(tasks_result)
                else:
                    logger.error(
                        f"Failed to fetch project tasks allocations by user: {tasks_result}")
                    return None
    except Exception as e:
        logger.error(
            f"Exception during fetching project tasks allocations by user: {str(e)}")
        return None
    
async def get_submission_reviewer_allocation(submission_id: str) -> Optional[List[ReviewAssignment]]:
    """Fetch project task allocations assigned to a specific reviewer.

    Args:
        task_details (ReviewerTaskRequestModel): The task details containing the user email.

    Returns:
        Optional[ProjectReviewerDetailsResponseModel]: The task allocations or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/submission/{submission_id}/agent/review_allocations".format(submission_id)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return [ReviewAssignment.model_validate(i) for i in tasks_result]
                else:
                    logger.error(
                        f"Failed to fetch project tasks allocations by user: {tasks_result}")
                    return None
    except Exception as e:
        logger.error(
            f"Exception during fetching project tasks allocations by user: {str(e)}")
        return None

async def get_project_tasks_assigned_to_user(task_details: ProjectTaskRequestModel) -> Optional[ProjectTaskDetailsResponseModel]:
    """Fetch project task allocations assigned to a specific user.

    Args:
        task_details (ProjectTaskRequestModel): The task details containing the user email.

    Returns:
        Optional[ProjectTaskDetailsResponseModel]: The task allocations or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/results/{task_details.project_id}/agent-allocations"
    params = {**task_details.model_dump(exclude_none=True, mode="json")}
    logger.debug(
        f"Fetching project tasks from URL: {url} with params: {params}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                tasks_result = await response.json()

                if response.status == 200:
                    return ProjectTaskDetailsResponseModel.model_validate(tasks_result)
                else:
                    logger.error(
                        f"Failed to fetch project tasks allocations by user: {tasks_result}")
                    return None
    except Exception as e:
        logger.error(
            f"Exception during fetching project tasks allocations by user: {str(e)}")
        return None


async def get_projects_details(user_email: str) -> list[dict]:
    """Fetch all project details by calling get_projects_details_by_user_email method.

    Args:
        user_email (str): The user's email address.

    Returns:
        list[dict]: A list of project important details or an empty list if none found.
    """

    try:
        projects = await get_projects_details_by_user_email(user_email)

        if projects:
            return [proj.model_dump() for proj in projects.root]
        else:
            return []
    except Exception as e:
        logger.error(f"Exception during fetching project names: {str(e)}")
        return []


async def get_project_review_parameters(project_id: str) -> list[str]:
    """Fetch review parameters for a specific project."""
    url = f"{BASE_URL_V2}/project/project/{project_id}/review-parameters"

    # Add logging to see the exact URL being called
    logger.info(f"Fetching review parameters from: {url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # Log the response status and content
                logger.info(f"Response status: {response.status}")

                if response.status == 200:
                    params_result = await response.json()
                    logger.info(f"Review parameters received: {params_result}")

                    # Handle different possible response structures
                    if isinstance(params_result, list):
                        return params_result
                    elif isinstance(params_result, dict) and 'review_parameters' in params_result:
                        return params_result['review_parameters']
                    elif isinstance(params_result, dict) and 'parameters' in params_result:
                        return params_result['parameters']
                    else:
                        logger.warning(
                            f"Unexpected response structure: {params_result}")
                        return list(params_result.keys()) if isinstance(params_result, dict) else []
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Failed to fetch project review parameters. Status: {response.status}, Response: {error_text}")
                    return []
    except Exception as e:
        logger.error(
            f"Exception during fetching project review parameters: {str(e)}")
        return []
