from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.models.api2_models.agent import SubmissionModel
from src.keyboards.inline import next_task_inline_kb
from src.routes.task_routes.task_formaters import ERROR_MESSAGE
from src.services.quality_assurance.text_validation import validate_text_input
from src.states.tasks import TaskState
from src.services.server.api2_server.agent_submission import create_submission
from src.handlers.task_handlers.audio_task_handler import handle_api2_audio_submission
from src.handlers.task_handlers.utils import extract_project_info, fetch_user_tasks, get_first_task, build_task_message, set_task_state_by_type, update_state_with_task
from src.responses.task_formaters import SUBMISSION_RECIEVED_MESSAGE


router = Router()


@router.callback_query(F.data == "start_agent_task")
async def start_task(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        project_info = extract_project_info(user_data)
        if not project_info:
            await callback.message.answer("Please select a project first using /projects.")
            return

        allocations = await fetch_user_tasks(project_info)
        if allocations and getattr(allocations, "tasks", None):
            await callback.message.answer("No tasks available at the moment. Please check back later.")
            return

        first_task = get_first_task(allocations)
        if not first_task:
            await callback.message.answer("No tasks available at the moment. Please check back later.")
            return

        task_msg, task_type = build_task_message(
            first_task, project_info["instruction"], project_info["return_type"])
        await callback.message.answer(task_msg)

        await update_state_with_task(state, project_info, first_task, task_type, task_msg)
        await set_task_state_by_type(callback.message, state)

    except Exception as e:
        logger.error(f"Error in start_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")

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
        await message.answer("Begin the next task.", reply_markup=next_task_inline_kb(user_type="agent", task_type='task'))
    else:
        errors = "\n".join(result["fail_reasons"])
        errors = ERROR_MESSAGE.format(errors=errors)
        await message.answer(errors)

    return


@router.message(TaskState.waiting_for_audio)
async def handle_audio_task_submission(message: Message, state: FSMContext):
    try:
        if not message.voice and not message.audio:
            await message.answer("Please submit an audio file or voice message.")
            return
        await message.answer(SUBMISSION_RECIEVED_MESSAGE)

        user_data = await state.get_data()
        
        # REWRITE TO GET THE TASK INFO FROM STATE DATA LIKE AUDIO FILE FORMAT
        response, new_path, out_message = await handle_api2_audio_submission(task_info={}, file_id=message.voice.file_id if message.voice else message.audio.file_id, user_id=message.from_user.id, bot=message.bot)
        if not response:
            await message.answer(out_message or "Failed to process audio submission. Please try again.")
            # task_msg = user_data.get("task", "")
            # await message.answer(task_msg)
            logger.info("Audio submission failed")
            return
        
        try:
            submission = SubmissionModel.model_validate(user_data)
            submission.type = "audio"
        except:
            await message.answer("Session data missing. Please restart the task using /start.")
            return


        submission_response = await create_submission(submission, file_path=new_path)
        if not submission_response:
            await message.answer("Failed to submit your work. Please try again.")
            return
        await message.answer("Your audio submission has been received and recorded successfully. Thank you!")
        await message.answer("Begin the next task.", reply_markup=next_task_inline_kb(user_type="agent", task_type='task'))
    except Exception as e:
        logger.error(f"Error in handle_audio_task_submission: {str(e)}")
        await message.answer("Error occurred, please try again.")

    return
