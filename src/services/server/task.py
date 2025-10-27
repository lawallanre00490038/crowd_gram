from typing import Dict
from src.config import BASE_URL
from src.models.task_models import CategoryListResponseModel
from loguru import logger
import requests


def get_full_task_detail(task_id: str, token: str) -> Dict[str, str]:
    """
    Fetches the full details of a task based on its ID. 
    Args:
        task_id (str): The ID of the task to fetch details for.
        user_id (str): The ID of the user requesting the task details.  
    Returns:
        Dict[str, str]: A dictionary containing the full details of the task.
    """
    url = f"{BASE_URL}/user/task/main_task_detail"
    payload = {"task_id": task_id}

    response = requests.post(url, json=payload, headers={
                             "Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch task details: {response.status_code}, {response.text}")
        return {}
    else:
        logger.info(f"Task details fetched successfully for task_id {task_id}")
        return response.json()


def get_main_task_list(
    token: str,
    category_id: str,
    language: str = "",
    deadlineRange: str = "",
    createdAtRange: str = "",
    coinsRange: str = "",
    search_key: str = "",
    limit: int = 0,
    page: int = 0,
    sort_direction: str = "",
    sort_column: str = ""
):
    '''
    FETCHES the main task list for a user.

    Args:
        token (str): The user's authentication token.
        category_id (str): The category ID to filter tasks.
        language (str): Language filter.
        deadlineRange (str): Deadline range filter.
        createdAtRange (str): Creation date range filter.
        coinsRange (str): Coins range filter.
        search_key (str): Search keyword.
        limit (int): Number of items per page.
        page (int): Page number.
        sort_direction (str): Sort direction.
        sort_column (str): Sort column.
    Returns:
        Dict[str, str]: A dictionary containing the main task list.
    '''
    url = f"{BASE_URL}user/task/main_task_list"
    payload = {
        "language": language,
        "deadlineRange": deadlineRange,
        "createdAtRange": createdAtRange,
        "coinsRange": coinsRange,
        "search_key": search_key,
        "limit": limit,
        "page": page,
        "sort_direction": sort_direction,
        "sort_column": sort_column,
        "category_id": category_id
    }

    response = requests.get(url, params=payload, headers={
                            "Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch main task list: {response.status_code}, {response.text}")
        return {}
    else:
        logger.info(
            f"Main task list fetched successfully for category_id {category_id}")
        return response.json()


def get_category_list(user_id: str) -> CategoryListResponseModel:
    '''
    fetches the list of categories available for a user.

    Args:
        user_id (str): The ID of the user requesting the category list.
    Returns:
        Dict[str, str]: A dictionary containing the list of categories.
    '''
    url = f"{BASE_URL}user/task/category_list"

    payload = {"user_id": user_id, "check_edit_category": "true"}

    response = requests.get(url, params=payload)

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch category list: {response.status_code}, {response.text}")
        return {}
    else:
        logger.info(
            f"Category list fetched successfully for user_id {user_id}")
        return CategoryListResponseModel.model_validate(response.json())


if __name__ == "__main__":
    print(get_category_list("687a7363c2afef2e72355d57"))
