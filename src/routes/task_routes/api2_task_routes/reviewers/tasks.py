from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from loguru import logger

from src.constant.task_constants import ContributorTaskStatus, ReviewerTaskStatus
from src.handlers.task_handlers.reviewer_handler import add_submission, handle_reviewer_task_start, process_review_submission
from src.keyboards.inline import build_predefined_comments_kd, summary_kb
from src.states.tasks import ReviewStates
from src.responses.task_formaters import REVIEWER_TASK_MSG


router = Router()

@router.callback_query(F.data == "start_reviewer_task")
async def start_reviewer_task(callback: CallbackQuery, state: FSMContext):
    try:
        await state.update_data(redo_task=False)
        await handle_reviewer_task_start(
            callback=callback,
            state=state,
            status_filter=ReviewerTaskStatus.PENDING,
            no_tasks_message="No tasks available at the moment. Please check back later."
        )
    except Exception as e:
        logger.error(f"Error in start_reviewer_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")

@router.callback_query(F.data == "skip_reviewer_task")
async def skip_reviewer_task(callback: CallbackQuery, state: FSMContext):
    user_state = await state.get_data()

    skipped_task = user_state.get("skipped_task", [])
    task_id = user_state.get("submission_id")
    skipped_task.append(task_id)

    logger.debug(f"Skipping task ID: {task_id} Skipped tasks so far: {skipped_task}")
        
    await state.update_data(skipped_task=skipped_task)

    try:
        if user_state.get("redo_task", False):
            await handle_reviewer_task_start(
                callback=callback,
                state=state,
                status_filter=ReviewerTaskStatus.REDO,
                no_tasks_message="No tasks to REDO at the moment..."
            )
        else:
            await handle_reviewer_task_start(
                callback=callback,
                state=state,
                status_filter=ReviewerTaskStatus.PENDING,
                no_tasks_message="No tasks available at the moment. Please check back later."
            )
    except Exception as e:
        logger.error(f"Error in start_reviewer_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")



@router.callback_query(F.data == "accept")
async def handle_accept(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    try:
        success = await process_review_submission(
            callback,
            data,
            decision="accept",
            comments=data.get("comments", []),
        )

        if not success:
            await add_submission(state)
            return

    except Exception as e:
        logger.error(f"Error in handle_accept: {e}")
        await callback.message.answer("⚠️ Error occurred, please try again.")
        return

@router.callback_query(F.data == "reject")
async def handle_reject(callback: CallbackQuery, state: FSMContext):
    """Handle task rejection by reviewer."""
    await callback.answer()
    data = await state.get_data()

    try:
        project_id = data.get("project_id")
        projects = data.get("projects_details", [])
        project = next(
            (p for p in projects if p.get("id") == project_id), None)

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
    await callback.answer()
    data = await state.get_data()

    selected_comments = data.get("selected_comments", [])
    if not selected_comments:
        await callback.message.answer("⚠️ Please select or write at least one comment before submitting.")
        return

    try:
        success = await process_review_submission(
            callback,
            data,
            decision="reject",
            comments=selected_comments,
        )

        if not success:
            await add_submission(state)

    except Exception as e:
        logger.exception(f"Error in confirm_comment_submission: {e}")
        await callback.message.answer("⚠️ Error occurred, please try again.")


@router.callback_query(F.data == "restart_review")
async def restart_comment_submission(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🔁 Let's start again. Please select your comments.")
    await start_reviewer_task(callback, state)

    return
    