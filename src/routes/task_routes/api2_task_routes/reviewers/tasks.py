from email.mime import text
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from typing import Optional
from aiogram.types import URLInputFile

from loguru import logger

from src.constant.task_constants import ContributorTaskStatus
from src.handlers.task_handlers.utils import extract_project_info, fetch_user_tasks, format_submission, get_first_reviewer, get_first_task, prepare_reviewer_state
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

        task_text = first_task.prompt.sentence_text

        submission = format_submission(first_task)

        caption = REVIEWER_TASK_MSG['intro'].format(
            project_name=project_info["name"],
            submission_type=first_task.submission.type,
            payload_text=task_text,
            submission=submission,
            reviewer_instruction=project_info["reviewer_instructions"]
        )

        logger.trace(f"Task Submission Type: {first_task.submission.type}")

        if first_task.submission.type == "audio":
            audio_file = URLInputFile(first_task.submission.file_url)

            await callback.message.answer_audio(
                caption=caption,
                audio=audio_file,
                parse_mode="HTML",
                protect_content=True,
                reply_markup=review_task_inline_kb()
            )
        else:
            await callback.message.answer(
                caption,
                parse_mode="HTML",
                reply_markup=review_task_inline_kb()
            )

        # Update state
        state_data = prepare_reviewer_state(first_reviewer)
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

    logger.debug("Starting reviewer accept task...")

    await callback.message.answer("Begin the next review task.", reply_markup=next_task_inline_kb(user_type="reviewer", task_type="normal"))

    return


@router.callback_query(F.data == "reject")
async def handle_reject(callback: CallbackQuery, state: FSMContext):
    """Handle task rejection by reviewer"""
    await callback.answer()
    data = await state.get_data()

    try:
        project_id = data.get("project_id")
        for details in data['projects_details']:
            if details['id'] == project_id:
                options: list[str] = details.get('predefined_comments', [])
                break
        logger.trace(f"Predefined comments options: {options}")

        await state.update_data(all_comments=options, selected_comments=[])
        await callback.message.answer(
            "🗒️ Select the reason(s) for rejection:",
            reply_markup=build_predefined_comments_kd(options, [])
        )
        await state.set_state(ReviewStates.choosing_comments)
    except Exception as e:
        logger.error(f"Error in handle_reject: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")


@router.callback_query(F.data.startswith("toggle_comment:"))
async def toggle_comment_handler(callback: CallbackQuery, state: FSMContext):
    option = callback.data.split(":", 1)[1]
    data = await state.get_data()

    selected = data.get("selected_comments", [])
    all_options = data.get("all_comments", [])

    if option in selected:
        selected.remove(option)
    else:
        selected.append(option)

    await state.update_data(selected_comments=selected)

    await callback.message.edit_reply_markup(
        reply_markup=build_predefined_comments_kd(all_options, selected)
    )

    await callback.answer()


@router.callback_query(F.data == "confirm_comments")
async def confirm_comments_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_comments", [])

    # 🛑 Validation: No comments selected
    if not selected:
        await callback.answer("Please select or write at least one comment before confirming.", show_alert=True)
        return

    logger.trace(selected)
    # Check if 'other' was selected — then ask for extra input
    if "other" in selected or "Other" in selected:
        await callback.message.answer("✏️ Please type your additional comment(s):")
        await state.set_state(ReviewStates.typing_extra_comment)
    else:
        await show_comment_summary(callback.message, state)

    await callback.answer()

    return


@router.message(ReviewStates.typing_extra_comment)
async def handle_extra_comment(message: Message, state: FSMContext):
    extra_comment = message.text.strip()

    # 🛑 Validation: Must not be empty
    if not extra_comment:
        await message.answer("⚠️ Please enter a valid comment (cannot be empty).")
        return

    data = await state.get_data()
    selected = set(data.get("selected_comments", []))
    selected.add(extra_comment)

    await state.update_data(selected_comments=list(selected))
    await show_comment_summary(message, state)
    return


async def show_comment_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_comments = data.get("selected_comments", [])
    if 'other' in selected_comments:
        selected_comments.remove('other')
    if 'Other' in selected_comments:
        selected_comments.remove('Other')
    comments_text = "\n".join([f"• {comment}" for comment in selected_comments]
                              ) if selected_comments else "No comments provided."

    await message.answer(
        REVIEWER_TASK_MSG['review_summary'].format(
            comments=comments_text
        ),
        parse_mode="HTML",
        reply_markup=summary_kb()
    )
    await state.update_data(selected_comments=selected_comments)
    await state.set_state(ReviewStates.summary)
    return


@router.callback_query(F.data == "submit_review")
async def confirm_comment_submission(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    decision = "reject"
    data = await state.get_data()
    selected_comments = data.get("selected_comments", [])

    # 🛑 Final validation before sending to backend
    if not selected_comments:
        await callback.message.answer("⚠️ You must select or write at least one comment before submitting.")
        return

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
