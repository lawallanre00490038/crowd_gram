from loguru import logger
from typing import Optional
import aiohttp

from src.config import BASE_URL_V2

from src.constant.task_constants import ContributorTaskStatus
from src.models.api2_models.projects import ProjectTaskRequestModel, ReviewerTaskRequestModel
from src.models.api2_models.status import ProjectReviewStats, StatusModel, StatusContributorResponseModel, StatusReviewerResponseModel,      AnalyticsResponseModel, DailyAnalyticsResponseModel
from src.services.server.api2_server.projects import get_project_tasks_assigned_to_reviewer, get_project_tasks_assigned_to_user, get_projects_details_by_user_email


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
                    logger.debug(f"Contributor info: {data}")
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

    projects = await get_projects_details_by_user_email(reviewer_data.email)

    status_review = StatusReviewerResponseModel(reviewer_email=reviewer_data.email, total_reviewed=0, approved_reviews=0, rejected_reviews=0, pending_reviews=0, redo_reviews=0, per_project=[])
    import pandas as pd
    for _, project in projects:
        project = project[0]
        logger.info(f"Processing project: {project.id} - {project.name}")
        task_request = ReviewerTaskRequestModel(
            reviewer_email = reviewer_data.email,
            project_id=project.id,
            status=[],
            limit=100000
        )
        

        logger.info(f"Fetching tasks for project: {task_request}")

        allocate = (await get_project_tasks_assigned_to_reviewer(task_request)).allocations        
        user_df = pd.DataFrame([i.model_dump() for i in allocate])
        user_request_model = ProjectTaskRequestModel(project_id=project.id, status=[ContributorTaskStatus.PENDING], limit=100000)
        user_allocation = (await get_project_tasks_assigned_to_user(user_request_model)).allocations
        agent_df = pd.DataFrame([i.model_dump() for i in user_allocation])

        def correct_status(row):
            if row['status'] == ContributorTaskStatus.PENDING:
                if row["submission_id"] in agent_df['submission_id'].values:
                    logger.info(f"Submission {row['submission_id']} is already in agent_df")
                    return True
                else:
                    return False
            else: 
                return True
        
        project_status = user_df[user_df.apply(correct_status, axis=1)]['status'].value_counts()
        
        # logger.info(f"Total task recovered: {user_df[user_df.apply(correct_status, axis=1)]['status'].value_counts()}")

        status_review.total_reviewed += project_status.sum()
        status_review.approved_reviews += project_status.get(ContributorTaskStatus.ACCEPTED, 0)
        status_review.rejected_reviews += project_status.get(ContributorTaskStatus.REJECTED, 0)
        status_review.pending_reviews += project_status.get(ContributorTaskStatus.PENDING, 0)  
        status_review.redo_reviews += project_status.get(ContributorTaskStatus.REDO, 0)

        status_review.per_project.append(
            ProjectReviewStats(
                project_id=project.id,
                project_name=project.name,
                total_reviewed=project_status.get(ContributorTaskStatus.ACCEPTED, 0) + project_status.get(ContributorTaskStatus.REJECTED, 0) +
                               project_status.get(ContributorTaskStatus.PENDING, 0) + project_status.get(ContributorTaskStatus.REDO, 0),
                approved=project_status.get(ContributorTaskStatus.ACCEPTED, 0),
                rejected=project_status.get(ContributorTaskStatus.REJECTED, 0),
                pending_review=project_status.get(ContributorTaskStatus.PENDING, 0),
                redo=project_status.get(ContributorTaskStatus.REDO, 0),
                number_assigned=project_status.sum(),
                total_coins_earned=0,
                total_amount_earned=0.0
            )
        )


    return status_review

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
