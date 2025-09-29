import logging
from typing import Optional
import aiohttp

from src.config import BASE_URL_V2

from src.models.api2_models.agent import SubmissionModel, SubmissionResponseModel, SubmissionListResponseModel, SubmissionFilterModel

logger = logging.getLogger(__name__)

async def create_submission(submission_data: SubmissionModel) -> Optional[SubmissionResponseModel]:
    """Create a new submission asynchronously using aiohttp.

    Args:
        submission_data (SubmissionModel): Data for the new submission.

    Returns:
        Optional[SubmissionResponseModel]: Created submission details if successful; None otherwise.
    """
    url = f"{BASE_URL_V2}/submissions/projects/{submission_data.project_id}/agent"
    payload = submission_data.model_dump()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return SubmissionResponseModel(**data['data'])
                else:
                    error_message = await response.text()
                    logger.error(f"Failed to create submission: {error_message}")
                    return None
        except Exception as e:
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
                    return SubmissionListResponseModel(**data['data'])
                else:
                    error_message = await response.text()
                    logger.error(f"Failed to fetch submissions: {error_message}")
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
    params = {k: v for k, v in filter_data.model_dump().items() if v is not None}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return SubmissionListResponseModel(**data['data'])
                else:
                    error_message = await response.text()
                    logger.error(f"Failed to fetch all submissions: {error_message}")
                    return None
        except Exception as e:
            logger.error(f"Exception during fetching all submissions: {e}")
            return None