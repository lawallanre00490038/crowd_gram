import logging
from typing import Optional
import aiohttp

from src.config import BASE_URL_V2

from src.models.api2_models.reviewer import ReviewerModel, UploadReviewModel, ReviewModel, UpdateReviewModel, ReviewerTaskResponseModel, ReviewFilterModel, ReviewFilterResponseModel, ReviewerHistoryRequestModel, ReviewerHistoryResponseListModel
logger = logging.getLogger(__name__)

async def assign_submission_to_reviewer(reviewer_data: ReviewModel) -> str:
    """Assigns a submission to a reviewer.

    Args:
        reviewer_data (ReviewModel): The reviewer data containing submission details.

    Returns:
        str: A message indicating the result of the assignment.
    """
    url = f"{BASE_URL_V2}/reviewer/assign_submission_to_reviewer"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=reviewer_data.model_dump(exclude_none=True)) as response:
                response_text = await response.text()
                if response.status == 200:
                    return "Submission assigned to reviewer successfully."
                else:
                    return f"Failed to assign submission: {response_text}"
    except Exception as e:
        return f"Error occurred: {str(e)}"
    

async def upload_review_file(review_data: UploadReviewModel) -> str:
    """Uploads a review file to the server.

    Args:
        review_data (UploadReviewModel): The review data to upload.

    Returns:
        str: A message indicating the result of the upload.
    """
    url = f"{BASE_URL_V2}/reviewer/upload_review_file"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=review_data.model_dump()) as response:
                response_text = await response.text()
                if response.status == 200:
                    return "Review file uploaded successfully."
                else:
                    return f"Failed to upload review file: {response_text}"
    except Exception as e:
        return f"Error occurred: {str(e)}"
    

async def submit_review(review_data: ReviewModel) -> str:
    """Submits a review to the server.

    Args:
        review_data (ReviewModel): The review data to submit.

    Returns:
        str: A message indicating the result of the submission.
    """
    url = f"{BASE_URL_V2}/reviewer/submissions/{review_data.submission_id}/review"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=review_data.model_dump(exclude_none=True)) as response:
                response_text = await response.text()
                if response.status == 200:
                    return "Review submitted successfully."
                else:
                    return f"Failed to submit review: {response_text}"
    except Exception as e:
        return f"Error occurred: {str(e)}"
    


async def update_review(review_data: UpdateReviewModel) -> str:
    """Updates an existing review on the server.

    Args:
        review_data (UpdateReviewModel): The review data to update.

    Returns:
        str: A message indicating the result of the update.
    """
    url = f"{BASE_URL_V2}/reviewer/submissions/{review_data.review_id}/review"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=review_data.model_dump()) as response:
                response_text = await response.text()
                if response.status == 200:
                    return "Review updated successfully."
                else:
                    return f"Failed to update review: {response_text}"
    except Exception as e:
        return f"Error occurred: {str(e)}"
    

async def get_filter_review(filter_data: ReviewFilterModel) -> Optional[list[ReviewFilterResponseModel]]:
    """Fetches filtered reviews from the server.

    Args:
        filter_data (ReviewFilterModel): The filter criteria.

    Returns:
        Optional[list[ReviewFilterResponseModel]]: The filtered review responses or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/reviewer/{filter_data.reviewer_id}/filter"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=filter_data.model_dump(exclude_none=True)) as response:
                response_text = await response.text()
                if response.status == 200:
                    data = await response.json()
                    return [ReviewFilterResponseModel(**item) for item in data]
                else:
                    logger.error(f"Failed to fetch filtered reviews: {response_text}")
                    return None
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return None
    

async def get_reviewer_history(reviewer_data: ReviewerHistoryRequestModel) -> Optional[ReviewerHistoryResponseListModel]:
    """Fetches the review history for a specific reviewer.

    Args:
        reviewer_id (str): The ID of the reviewer.
    Returns:
        Optional[ReviewerHistoryResponseListModel]: The reviewer's history response model or None if an error occurs.
    """
    url = f"{BASE_URL_V2}/reviewer/{reviewer_data.reviewer_id}/history"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_text = await response.text()
                if response.status == 200:
                    data = await response.json()
                    return ReviewerHistoryResponseListModel(**data)
                else:
                    logger.error(f"Failed to fetch reviewer history: {response_text}")
                    return None
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return None