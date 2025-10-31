from loguru import logger
from typing import Optional
import aiohttp

from src.config import BASE_URL_V2

from src.models.api2_models.status import StatusModel, StatusContributorResponseModel, StatusReviewerResponseModel,      AnalyticsResponseModel, DailyAnalyticsResponseModel


async def get_contributor_status(contributor_data: StatusModel) -> StatusContributorResponseModel:
    """Fetches the status of a contributor.

    Args:
        contributor_data (StatusModel): The contributor data containing email and time range.

    Returns:
        StatusContributorResponseModel: The status details of the contributor.
    """
    url = f"{BASE_URL_V2}/status/contributor/{contributor_data.email}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, json=contributor_data.model_dump()) as response:
                response_text = await response.text()
                if response.status == 200:
                    data = await response.json()
                    return StatusContributorResponseModel(**data)
                else:
                    logger.error(
                        f"Failed to fetch contributor status: {response_text}")
                    return StatusContributorResponseModel(user_email=contributor_data.email, approved=0, pending=0, rejected=0, per_project=[])
    except Exception as e:
        logger.error(
            f"Error occurred while fetching contributor status: {str(e)}")
        return StatusContributorResponseModel(user_email=contributor_data.email, approved=0, pending=0, rejected=0, per_project=[])


async def get_reviewer_status(reviewer_data: StatusModel) -> StatusReviewerResponseModel:
    """Fetches the status of a reviewer.

    Args:
        reviewer_data (StatusModel): The reviewer data containing email and time range.

    Returns:
        StatusReviewerResponseModel: The status details of the reviewer.
    """
    url = f"{BASE_URL_V2}/status/reviewer/{reviewer_data.email}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, json=reviewer_data.model_dump()) as response:
                response_text = await response.text()
                if response.status == 200:
                    data = await response.json()
                    logger.trace(f"Reviewer info: {data}")
                    return StatusReviewerResponseModel(**data)
                else:
                    logger.error(
                        f"Failed to fetch reviewer status: {response_text}")
                    return StatusReviewerResponseModel(reviewer_email=reviewer_data.email, total_reviews=0, approved_reviews=0, rejected_reviews=0, pending_reviews=0, per_project=[])
    except Exception as e:
        logger.error(
            f"Error occurred while fetching reviewer status: {str(e)}")
        return StatusReviewerResponseModel(reviewer_email=reviewer_data.email, total_reviews=0, approved_reviews=0, rejected_reviews=0, pending_reviews=0, per_project=[])


async def get_analytics() -> AnalyticsResponseModel:
    """Fetches the analytics data.

    Returns:
        AnalyticsResponseModel: The analytics data.
    """
    url = f"{BASE_URL_V2}/status/platform/analytics"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_text = await response.text()
                if response.status == 200:
                    data = await response.json()
                    return AnalyticsResponseModel(**data)
                else:
                    logger.error(
                        f"Failed to fetch analytics data: {response_text}")
                    return AnalyticsResponseModel(
                        total_users=0,
                        total_projects=0,
                        total_allocations=0,
                        total_submissions=0,
                        approved_submissions=0,
                        rejected_submissions=0,
                        pending_review_submissions=0,
                        total_coins_paid=0
                    )
    except Exception as e:
        logger.error(f"Error occurred while fetching analytics data: {str(e)}")
        return AnalyticsResponseModel(
            total_users=0,
            total_projects=0,
            total_allocations=0,
            total_submissions=0,
            approved_submissions=0,
            rejected_submissions=0,
            pending_review_submissions=0,
            total_coins_paid=0
        )


async def get_daily_analytics() -> DailyAnalyticsResponseModel:
    """Fetches the daily analytics data.

    Returns:
        DailyAnalyticsResponseModel: The daily analytics data.
    """
    url = f"{BASE_URL_V2}/status/daily/analytics"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_text = await response.text()
                if response.status == 200:
                    data = await response.json()
                    return DailyAnalyticsResponseModel(**data)
                else:
                    logger.error(
                        f"Failed to fetch daily analytics data: {response_text}")
                    return DailyAnalyticsResponseModel(data=[])
    except Exception as e:
        logger.error(
            f"Error occurred while fetching daily analytics data: {str(e)}")
        return DailyAnalyticsResponseModel(data=[])
