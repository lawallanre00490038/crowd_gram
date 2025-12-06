from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.constant.task_constants import ContributorTaskStatus
from src.handlers.task_handlers.contributor_handler import build_task_message, process_and_send_task
from src.models.api2_models.agent import SubmissionModel
from src.keyboards.inline import next_task_inline_kb
from src.routes.task_routes.task_formaters import ERROR_MESSAGE
from src.services.quality_assurance.text_validation import validate_text_input
from src.states.tasks import TaskState
from src.services.server.api2_server.agent_submission import create_submission
from src.handlers.task_handlers.audio_task_handler import handle_api2_audio_submission
from src.responses.task_formaters import SUBMISSION_RECIEVED_MESSAGE


router = Router()

@router.callback_query(F.data == "start_agent_task")
async def start_task_new(callback: CallbackQuery, state: FSMContext):
    await process_and_send_task(
        callback=callback,
        state=state,
        # Default parameters for NEW task
        status_filter=ContributorTaskStatus.ASSIGNED, # Fetching the default available status
        no_tasks_message="No tasks available at the moment. Please check back later.",
        project_not_selected_message="Please select a project first using /projects.",
        build_msg_func=build_task_message,
        is_redo_task=False,
    )

@router.callback_query(F.data == "skip_agent_task")
async def skip_task_new(callback: CallbackQuery, state: FSMContext):
    skipped_task = await state.get_value("skipped_task", [])
    task_id = await state.get_value("task_id")
    skipped_task.append(task_id)

    logger.debug(f"Skipping task ID: {task_id} Skipped tasks so far: {skipped_task}")
        
    await state.update_data(skipped_task=skipped_task)
    
    await process_and_send_task(
        callback=callback,
        state=state,
        # Default parameters for NEW task
        status_filter=ContributorTaskStatus.ASSIGNED, # Fetching the default available status
        no_tasks_message="No tasks available at the moment. Please check back later.",
        project_not_selected_message="Please select a project first using /projects.",
        build_msg_func=build_task_message,
        is_redo_task=False,
    )

@router.message(TaskState.waiting_for_text)
async def handle_text_input(message: Message, state: FSMContext):
    text = message.text.strip()
    user_data = await state.get_data()

    result = validate_text_input(
        text, task_lang=None, exp_task_script=None)

    submission = SubmissionModel.model_validate(user_data)
    submission.payload_text = text
    submission.type = "text"

    logger.debug(f"Text submission validation result: {result}")
    logger.debug(f"Submission data: {submission}")

    submission_response = await create_submission(submission)
    if result["success"]:
        if not submission_response:
            await message.answer("Failed to submit your work. Please try again.")
            return
        await message.answer("Your text submission has been received and recorded successfully. Thank you!")

        redo_task = user_data.get("redo_task", False)
        if redo_task:
            await message.answer("Begin the next task.", reply_markup=next_task_inline_kb(user_type="agent", task_type='redo'))
        else:
            redo_task = user_data.get("redo_task", False)
        if redo_task:
            await message.answer("Begin the next REDO task.", reply_markup=next_task_inline_kb(user_type="agent", task_type='redo'))
        else:
            await message.answer("Begin the next task.", reply_markup=next_task_inline_kb(user_type="agent", task_type='task'))
    else:
        errors = "\n".join(result["fail_reasons"])
        errors = ERROR_MESSAGE.format(errors=errors)
        await message.answer(errors)

    return


@router.message(TaskState.waiting_for_audio)
async def handle_audio_task_submission(message: Message, state: FSMContext):
    try:
        if not message.voice:
            await message.answer("Please record a voice message.")
            return
        await message.answer(SUBMISSION_RECIEVED_MESSAGE)

        user_data = await state.get_data()

        # REWRITE TO GET THE TASK INFO FROM STATE DATA LIKE AUDIO FILE FORMAT
        response, new_path, out_message = await handle_api2_audio_submission(task_info={}, file_id=message.voice.file_id if message.voice else message.audio.file_id, user_id=message.from_user.id, bot=message.bot)
        if not response:
            await message.answer(out_message or "Failed to process audio submission. Please try again.")
            logger.info("Audio submission failed")
            return

        try:
            submission = SubmissionModel.model_validate(user_data)
            submission.type = "audio"
        except:
            await message.answer("Session data missing. Please restart the task using /start.")
            return

        submission_response = await create_submission(submission, file_path=new_path)
        import os

        os.remove(new_path)
        
        if not submission_response:
            await message.answer("Failed to submit your work. Please try again.")
            return
        await message.answer("Your audio submission has been received and recorded successfully. Thank you!")

        redo_task = user_data.get("redo_task", False)
        if redo_task:
            await message.answer("Begin the next task.", reply_markup=next_task_inline_kb(user_type="agent", task_type='redo'))
        else:
            await message.answer("Begin the next task.", reply_markup=next_task_inline_kb(user_type="agent", task_type='task'))
    except Exception as e:
        logger.error(f"Error in handle_audio_task_submission: {str(e)}")
        await message.answer("Error occurred, please try again.")
    return
