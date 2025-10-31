from loguru import logger
from typing import Optional
import aiohttp
from pathlib import Path
import json

from src.config import BASE_URL_V2

from src.models.api2_models.agent import SubmissionModel, SubmissionResponseModel, SubmissionListResponseModel, SubmissionFilterModel


async def create_submission(submission_data: SubmissionModel, file_path: str | None = None) -> Optional[SubmissionResponseModel]:
    """Create a new submission asynchronously using aiohttp.

    Args:
        submission_data (SubmissionModel): Data for the new submission.
        file_path (str, optional): Path to the file to be uploaded. Defaults to None.

    Returns:
        Optional[SubmissionResponseModel]: Created submission details if successful; None otherwise.
    """
    url = f"{BASE_URL_V2}/submission/projects/{submission_data.project_id}/agent"
    form = aiohttp.FormData()

    # Add text fields
    for key, value in submission_data.model_dump(exclude_none=True, exclude={"file"}).items():
        form.add_field(key, json.dumps(value) if isinstance(value, (dict, list)) else str(value))

    # Add file if provided
    if file_path and Path(file_path).exists():
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()  
            form.add_field(
                "file",
                file_bytes,
                filename=Path(file_path).name,
                content_type="application/octet-stream",
            )
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            return None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=form) as response:
                if response.status == 200:
                    data = await response.json()
                    return SubmissionResponseModel.model_validate(data)
                else:
                    error_message = await response.text()
                    logger.error(f"Failed to create submission: {error_message}")
                    return None
        except Exception as e:
            logger.trace(f"Submitting to {url} with data {form} and file {file_path}")
            logger.error(f"Exception during submission creation: {e}")
            return None


async def get_submissions(submission_id: str) -> Optional[SubmissionListResponseModel]:
    """Fetch submissions based on the provided submission ID.

    Args:
        submission_id (str): The ID of the submission to fetch.

    Returns:
        Optional[SubmissionListResponseModel]: The list of submissions if successful; None otherwise.
    """
    url = f"{BASE_URL_V2}/submission/{submission_id}/agent"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return SubmissionListResponseModel.model_validate(data)
                else:
                    error_message = await response.text()
                    logger.error(
                        f"Failed to fetch submissions: {error_message}")
                    return None
        except Exception as e:
            logger.error(f"Exception during fetching submissions: {e}")
            return None


async def get_all_submissions(filter_data: SubmissionFilterModel) -> Optional[SubmissionListResponseModel]:
    """Fetch all submissions based on the provided filter criteria.

    Args:
        filter_data (SubmissionFilterModel): Filter criteria for fetching submissions.

    Returns:
        Optional[SubmissionListResponseModel]: The list of submissions if successful; None otherwise.
    """
    url = f"{BASE_URL_V2}/submissions/agent"
    params = {k: v for k, v in filter_data.model_dump().items()
              if v is not None}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return SubmissionListResponseModel(**data['data'])
                else:
                    error_message = await response.text()
                    logger.error(
                        f"Failed to fetch all submissions: {error_message}")
                    return None
        except Exception as e:
            logger.error(f"Exception during fetching all submissions: {e}")
            return None
