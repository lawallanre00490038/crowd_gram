from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from typing import Optional

from loguru import logger

from src.models.api2_models.agent import SubmissionModel
from src.keyboards.inline import next_task_inline_kb, build_predefined_comments_kd, review_task_inline_kb, create_score_kb, summary_kb
from src.states.tasks import TaskState, ReviewStates
from src.services.server.api2_server.projects import get_project_review_parameters, get_project_tasks_assigned_to_user
from src.services.server.api2_server.reviewer import submit_review_details
from src.services.server.api2_server.agent_submission import create_submission
from src.handlers.task_handlers.audio_task_handler import handle_api2_audio_submission
from src.responses.task_formaters import REVIEWER_TASK_MSG
from src.models.api2_models.projects import ProjectTaskRequestModel
from src.utils.file_url_handlers import build_file_section
from src.utils.submission_utils import get_submission_info
from src.models.api2_models.reviewer import ReviewModel, ReviewSubmissionResponse


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
                reply_markup=review_task_inline_kb()
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


@router.callback_query(F.data == "accept")
async def handle_accept(callback: CallbackQuery, state: FSMContext):
    """Handle task acceptance by reviewer"""
    await callback.answer()
    decision = "accept"
    data = await state.get_data()

    try:
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
            decision=decision,
            reviewer_comments=data.get("comments", []),
        )

        logger.trace(review_data)

        result: Optional[ReviewSubmissionResponse] = await submit_review_details(review_data)
        logger.trace(result)
        if result and result.submission_status:
            await callback.message.answer("✅ Review accepted successfully!")
        else:
            await callback.message.answer("❌ Failed to accept review. Please try again later.")

    except Exception as e:
        logger.error(f"Error in handle_accept: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")

    await callback.message.answer("Begin the next review task.", reply_markup=next_task_inline_kb(user_type="reviewer", task_type="normal"))

    return


@router.callback_query(F.data == "reject")
async def handle_reject(callback: CallbackQuery, state: FSMContext):
    """Handle task rejection by reviewer"""
    await callback.answer()
    data = await state.get_data()

    try:
        project_id = data.get("project_id")
        options: list[str] = await get_project_review_parameters(project_id=project_id)

        logger.trace(f"Predefined comments options: {options}")

        await state.update_data(all_comments=options, selected_comments=[])
        await callback.message.answer(
            "🗒️ Select the reason(s) for rejection:",
            reply_markup=build_predefined_comments_kd(options)
        )
        await state.set_state(ReviewStates.choosing_comments)
    except Exception as e:
        logger.error(f"Error in handle_reject: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")


@router.callback_query(F.data.startswith("toggle_comment:"))
async def toggle_comment_handler(callback: CallbackQuery, state: FSMContext):
    option = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = set(data.get("selected_comments", []))
    all_options = data.get("all_comments", [])

    # Toggle the selected option
    if option in selected:
        selected.remove(option)
    else:
        selected.add(option)

    await state.update_data(selected_comments=list(selected))
    await callback.message.edit_reply_markup(
        reply_markup=build_predefined_comments_kd(all_options, selected)
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_comments")
async def confirm_comments_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = set(data.get("selected_comments", []))

    if "other" in selected:
        await callback.message.answer("✏️ Please type your additional comments:")
        await state.set_state(ReviewStates.typing_extra_comment)
    else:
        await callback.message.answer(f"✅ Comments selected: {', '.join(selected) or 'None'}")
        await show_comment_summary(callback.message, state)

    await callback.answer()
    return


@router.message(ReviewStates.typing_extra_comment)
async def handle_extra_comment(message: Message, state: FSMContext):
    extra_comment = message.text.strip()
    data = await state.get_data()
    selected = set(data.get("selected_comments", []))

    selected.add(extra_comment)
    await show_comment_summary(message, state)
    state.update_data("selected_comments", list(selected))
    return


async def show_comment_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_comments = data.get("selected_comments", [])
    comments_text = "\n".join([f"• {comment}" for comment in selected_comments]
                              ) if selected_comments else "No comments provided."

    await message.answer(
        REVIEWER_TASK_MSG['review_summary'].format(
            comments=comments_text
        ),
        parse_mode="HTML",
        reply_markup=summary_kb()
    )
    await state.set_state(ReviewStates.summary)
    return


@router.callback_query(F.data == "submit_review")
async def confirm_comment_submission(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    decision = "reject"
    data = await state.get_data()

    try:
        selected_comments = data.get("selected_comments", [])
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
            decision=decision,
            reviewer_comments=selected_comments,
        )

        logger.trace(review_data)

        result: Optional[ReviewSubmissionResponse] = await submit_review_details(review_data)
        logger.trace(result)
        if result and result.submission_status:
            await callback.message.answer("✅ Review accepted successfully!")
        else:
            await callback.message.answer("❌ Failed to accept review. Please try again later.")

    except Exception as e:
        logger.error(f"Error in handle_accept: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")

    await callback.message.answer("Begin the next review task.", reply_markup=next_task_inline_kb(user_type="reviewer", task_type="normal"))

    return


@router.callback_query(F.data == "restart_review")
async def restart_comment_submission(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🔁 Let's start again. Please select your comments.")
    await start_reviewer_task(callback, state)

    return
