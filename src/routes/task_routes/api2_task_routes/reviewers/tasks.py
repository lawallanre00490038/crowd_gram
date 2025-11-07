from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from loguru import logger

from src.models.api2_models.agent import SubmissionModel
from src.keyboards.inline import next_reviewer_task_inline_kb, review_task_kb, create_score_kb, summary_kb
from src.states.tasks import TaskState, ReviewState
from src.services.server.api2_server.projects import get_project_review_parameters, get_project_tasks_assigned_to_user
from src.services.server.api2_server.reviewer import submit_review_details
from src.services.server.api2_server.agent_submission import create_submission
from src.handlers.task_handlers.audio_task_handler import handle_api2_audio_submission
from src.responses.task_formaters import REVIEWER_TASK_MSG
from src.models.api2_models.projects import ProjectTaskRequestModel
from src.utils.file_url_handlers import build_file_section
from src.utils.submission_utils import get_submission_info
from src.models.api2_models.reviewer import ReviewModel


router = Router()


@router.callback_query(F.data == "start_reviewer_task")
async def start_reviewer_task(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        email = user_data.get("user_email")
        project_index = user_data.get("project_index")
        project_id = user_data.get("projects_details")[project_index]['id']
        project_name = user_data.get("projects_details")[project_index]['name']
        reviewer_instruction = user_data.get("projects_details")[project_index].get(
            'reviewer_instructions', 'No specific instructions provided.')

        if not email or not project_id:
            await callback.message.answer("Please select a project first using /start.")
            return

        task_details = ProjectTaskRequestModel(
            project_id=project_id, email=email, status="pending")
        allocations = await get_project_tasks_assigned_to_user(task_details)

        logger.trace(f"Allocation: {allocations}")

        if not allocations:
            await callback.message.answer("No tasks available at the moment. Please check back later.")
            return

        reviewers_list = allocations.reviewers if hasattr(
            allocations, 'reviewers') else []

        if reviewers_list:
            first_reviewer = reviewers_list[0]

            # Check if reviewer has tasks
            if not first_reviewer.tasks or len(first_reviewer.tasks) == 0:
                await callback.message.answer("No review tasks available at the moment. Please check back later.")
                return

            first_task = first_reviewer.tasks[0]

            # Check if task has submission
            if first_task.submission is None:
                await callback.message.answer("No submissions available for review at the moment. Please check back later.")
                return

            task_text = first_task.prompt.sentence_text
            submission_type = first_task.submission.type
            submission_file_url = first_task.submission.file_url

            if first_task.submission.type == "text":
                submission = first_task.submission.payload_text
            else:
                submission = build_file_section(
                    submission_type, submission_file_url)
            await callback.message.answer(
                REVIEWER_TASK_MSG['intro'].format(
                    project_name=project_name,
                    submission_type=submission_type,
                    payload_text=task_text,
                    submission=submission,
                    reviewer_instruction=reviewer_instruction
                ),
                parse_mode="HTML",
                reply_markup=review_task_kb()
            )

            # Convert Pydantic objects to dictionaries for state storage
            reviewers_list_dict = [reviewer.model_dump()
                                   for reviewer in reviewers_list]
            first_task = reviewers_list_dict[0].get(
                "tasks", [{}])[0] if reviewers_list_dict else {}
            submission_dict = first_task.get("submission") or {}
            await state.update_data(
                reviewers_list=reviewers_list_dict,
                project_id=project_id,
                submission_id=submission_dict.get("submission_id"),
                reviewer_id=reviewers_list_dict[0].get("reviewer_id"),
            )
        else:
            await callback.message.answer("No submissions available for review at the moment. Please check back later.")

    except Exception as e:
        logger.error(f"Error in start_reviewer_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")

    return


@router.callback_query(F.data == "review_task")
async def start_review(callback: CallbackQuery, state: FSMContext):
    """Begins the review scoring process"""
    await callback.answer()
    data = await state.get_data()

    projects_details = data.get("projects_details", [])
    reviewers_list = data.get("reviewers_list", [])
    project_index = data.get("project_index")
    project_id = projects_details[project_index]['id']
    current_task = reviewers_list[0].get(
        "tasks", [{}])[0] if reviewers_list else {}
    submission_dict = current_task.get("submission") or {}

    if not reviewers_list or not project_id:
        await callback.message.answer("No assigned review task found.")
        return

    # Fetch review parameters
    review_params = await get_project_review_parameters(project_id=project_id)
    if not review_params:
        await callback.message.answer("No review parameters found for this project.")
        return

    await state.update_data(
        review_params=review_params,
        scores={},
        index=0,
        review_scale=5,
        current_task=current_task,
        project_id=project_id,
        submission_id=submission_dict.get("submission_id"),
        reviewer_id=reviewers_list[0].get("reviewer_id"),
    )

    await ask_next_param(callback.message, state)

    return


async def ask_next_param(message: Message, state: FSMContext):
    """Ask user to rate the next parameter"""
    data = await state.get_data()
    index = data.get("index", 0)
    review_params = data.get("review_params", [])
    scale = data.get("review_scale", 5)

    if index < len(review_params):
        param = review_params[index]
        await message.answer(
            f"🎯 Rate for <b><i>{param.upper()}</i></b> (0–{scale})",
            reply_markup=create_score_kb(index, scale)
        )
        await state.set_state(TaskState.scoring)
    else:
        await message.answer(
            "✍️ Leave a comment for this review (send text)."
        )
        await state.update_data(awaiting_comment=True)
        await state.set_state(TaskState.commenting)

    return


@router.callback_query(F.data.startswith("score:"))
async def handle_score(callback: CallbackQuery, state: FSMContext):
    """Handle each scoring selection"""
    await callback.answer()
    _, param_index, score = callback.data.split(":")
    param_index, score = int(param_index), int(score)

    data = await state.get_data()
    review_params = data.get("review_params", [])
    scores = data.get("scores", {})

    if param_index < len(review_params):
        param = review_params[param_index]
        scores[param] = score

    await state.update_data(scores=scores, index=param_index + 1)
    await ask_next_param(callback.message, state)

    return


@router.message()
async def handle_comment_message(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("awaiting_comment"):
        return  # ignore messages that are not comment inputs

    text = (message.text or "").strip()
    if not text:
        await message.answer("❗ Comment cannot be empty. Please send your comment.")
        return

    # save comment and proceed to summary
    await state.update_data(comments=text, awaiting_comment=False)
    await show_summary(message, state)
    return


async def show_summary(message: Message, state: FSMContext):
    """Display review summary"""
    data = await state.get_data()
    scores = data.get("scores", {})
    scale = data.get("review_scale", 5)
    comments = data.get("comments", "")

    summary_lines = [
        f"• {param.upper()}:  {score}/{scale}" for param, score in scores.items()]
    summary_text = "\n".join(summary_lines)
    comment_section = f"\n\n💬 Comment:\n{comments}" if comments else ""

    await message.answer(
        f"📊 Review Summary:\n\n{summary_text}{comment_section}\n\n✅ Ready to submit?",
        reply_markup=summary_kb()
    )
    await state.set_state(TaskState.summary)
    # clear awaiting_comment flag if present
    await state.update_data(awaiting_comment=False)

    return


@router.callback_query(F.data == "submit_review")
async def submit_review(callback: CallbackQuery, state: FSMContext):
    """Submit completed review"""
    await callback.answer()
    data = await state.get_data()

    try:
        scores = data.get("scores", {})
        project_id = data.get("project_id")
        reviewers_list = data.get("reviewers_list", [])

        submission_id = data.get("submission_id")
        if not submission_id:
            first_task = reviewers_list[0].get("tasks", [{}])[0]
            submission_id = (first_task.get("submission")).get("submission_id")

        reviewer_email = data.get('user_email')

        review_data = ReviewModel(
            submission_id=submission_id,
            project_id=project_id,
            reviewer_identifier=reviewer_email,
            comments=data.get("comments", ""),
            scores=scores
        )

        logger.trace(review_data)
        result = await submit_review_details(review_data)
        logger.trace(result)
        if result:
            await callback.message.answer("✅ Review submitted successfully!")
        else:
            await callback.message.answer("❌ Failed to submit review. Please try again later.")

    except Exception as e:
        logger.exception(f"Error submitting review: {str(e)}")
        await callback.message.answer("⚠️ Error submitting review. Please contact support.")

    await callback.message.answer("Begin the next review task.", reply_markup=next_reviewer_task_inline_kb())

    return


@router.callback_query(F.data == "restart_review")
async def restart_review(callback: CallbackQuery, state: FSMContext):
    """Restart review process"""
    await callback.answer()
    await state.update_data(scores={}, index=0)
    await ask_next_param(callback.message, state)

    return
