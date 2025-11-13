from email.mime import text
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from typing import Optional
from aiogram.types import URLInputFile

from loguru import logger

from src.constant.task_constants import ContributorTaskStatus
from src.handlers.task_handlers.reviewer_handler import send_reviewer_task, get_first_reviewer, prepare_reviewer_state
from src.handlers.task_handlers.utils import extract_project_info, fetch_user_tasks, format_submission
from src.keyboards.inline import next_task_inline_kb, build_predefined_comments_kd, review_task_inline_kb, create_score_kb, summary_kb
from src.states.tasks import ReviewStates
from src.services.server.api2_server.reviewer import submit_review_details
from src.responses.task_formaters import REVIEWER_TASK_MSG
from src.models.api2_models.reviewer import ReviewModel, ReviewSubmissionResponse


router = Router()

@router.callback_query(F.data == "start_reviewer_task")
async def start_reviewer_task(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        project_info = extract_project_info(user_data)

        if not project_info["email"] or not project_info["id"]:
            await callback.message.answer("Please select a project first using /project.")
            return

        allocations = await fetch_user_tasks(project_info, status=ContributorTaskStatus.PENDING)
        if not allocations:
            await callback.message.answer("No tasks available at the moment. Please check back later.")
            return
        
        first_reviewer, first_task = get_first_reviewer(allocations)
        if not first_task:
            await callback.message.answer("No submissions available for review at the moment. Please check back later.")
            return

        await send_reviewer_task(callback.message, first_task, project_info)
        # Update state
        state_data = prepare_reviewer_state(allocations.reviewers)
        state_data.update({"project_id": project_info["id"]})
        await state.update_data(**state_data)

    except Exception as e:
        logger.error(f"Error in start_reviewer_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")



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
    """Handle task rejection by reviewer."""
    await callback.answer()
    data = await state.get_data()

    try:
        project_id = data.get("project_id")
        projects = data.get("projects_details", [])
        project = next((p for p in projects if p.get("id") == project_id), None)

        options = project.get("predefined_comments", []) if project else []
        logger.trace(f"Predefined comments options: {options}")

        await state.update_data(all_comments=options, selected_comments=[])

        await callback.message.answer(
            "🗒️ Select the reason(s) for rejection:",
            reply_markup=build_predefined_comments_kd(options, [])
        )
        await state.set_state(ReviewStates.choosing_comments)

    except Exception as e:
        logger.exception(f"Error in handle_reject: {e}")
        await callback.message.answer("❌ Error occurred, please try again.")


@router.callback_query(F.data.startswith("toggle_comment:"))
async def toggle_comment_handler(callback: CallbackQuery, state: FSMContext):
    """Toggle a predefined comment on or off."""
    await callback.answer()
    option = callback.data.split(":", 1)[1]
    data = await state.get_data()

    selected = set(data.get("selected_comments", []))
    all_options = data.get("all_comments", [])

    # Toggle option
    selected.symmetric_difference_update({option})
    await state.update_data(selected_comments=list(selected))

    await callback.message.edit_reply_markup(
        reply_markup=build_predefined_comments_kd(all_options, list(selected))
    )


@router.callback_query(F.data == "confirm_comments")
async def confirm_comments_handler(callback: CallbackQuery, state: FSMContext):
    """Confirm selected predefined comments or request additional input."""
    await callback.answer()
    data = await state.get_data()
    selected = data.get("selected_comments", [])

    # 🛑 Require at least one comment
    if not selected:
        await callback.answer("Please select or write at least one comment.", show_alert=True)
        return

    if any(opt.lower() == "other" for opt in selected):
        await callback.message.answer("✏️ Please type your additional comment(s):")
        await state.set_state(ReviewStates.typing_extra_comment)
    else:
        await show_comment_summary(callback.message, state)


@router.message(ReviewStates.typing_extra_comment)
async def handle_extra_comment(message: Message, state: FSMContext):
    """Capture additional comment text."""
    extra_comment = message.text.strip()

    if not extra_comment:
        await message.answer("⚠️ Please enter a valid comment (cannot be empty).")
        return

    data = await state.get_data()
    selected = set(data.get("selected_comments", [])) | {extra_comment}

    await state.update_data(selected_comments=list(selected))
    await show_comment_summary(message, state)


async def show_comment_summary(message: Message, state: FSMContext):
    """Show a summary of all selected and written comments."""
    data = await state.get_data()
    selected_comments = [
        c for c in data.get("selected_comments", []) if c.lower() != "other"
    ]

    comments_text = (
        "\n".join([f"• {comment}" for comment in selected_comments])
        if selected_comments
        else "No comments provided."
    )

    await message.answer(
        REVIEWER_TASK_MSG["review_summary"].format(comments=comments_text),
        parse_mode="HTML",
        reply_markup=summary_kb()
    )

    await state.update_data(selected_comments=selected_comments)
    await state.set_state(ReviewStates.summary)

@router.callback_query(F.data == "submit_review")
async def confirm_comment_submission(callback: CallbackQuery, state: FSMContext):
    """Submit final review with selected comments."""
    await callback.answer()
    data = await state.get_data()
    selected_comments = data.get("selected_comments", [])

    if not selected_comments:
        await callback.message.answer("⚠️ Please select or write at least one comment before submitting.")
        return

    try:
        project_id = data.get("project_id")
        reviewers_list = data.get("reviewers_list", [])
        submission_id = data.get("submission_id")

        if not submission_id and reviewers_list:
            first_task = reviewers_list[0].get("tasks", [{}])[0]
            submission_id = (first_task.get("submission")).get("submission_id")

        reviewer_email = data.get("user_email")

        review_data = ReviewModel(
            submission_id=submission_id,
            project_id=project_id,
            reviewer_identifier=reviewer_email,
            decision="reject",
            reviewer_comments=selected_comments,
        )

        logger.trace(review_data)
        result: Optional[ReviewSubmissionResponse] = await submit_review_details(review_data)

        if result and result.submission_status:
            await callback.message.answer("✅ Review submitted successfully!")
        else:
            await callback.message.answer("❌ Failed to submit review. Please try again later.")

    except Exception as e:
        logger.exception(f"Error in confirm_comment_submission: {e}")
        await callback.message.answer("⚠️ Error occurred, please try again.")

    redo_task = data.get("redo_task", False)

    if redo_task:
        await callback.message.answer("Begin the next redo review task.", reply_markup=next_task_inline_kb(user_type="reviewer", task_type="redo"))
    else:
        await callback.message.answer("Begin the next review task.", reply_markup=next_task_inline_kb(user_type="reviewer", task_type="task"))
    return


@router.callback_query(F.data == "restart_review")
async def restart_comment_submission(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🔁 Let's start again. Please select your comments.")
    await start_reviewer_task(callback, state)

    return
