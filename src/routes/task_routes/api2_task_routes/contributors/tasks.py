from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.models.api2_models.agent import SubmissionModel
from src.keyboards.inline import next_agent_task_inline_kb
from src.routes.task_routes.task_formaters import ERROR_MESSAGE
from src.services.quality_assurance.text_validation import validate_text_input
from src.states.tasks import TaskState
from src.services.server.api2_server.projects import get_project_tasks_assigned_to_user
from src.services.server.api2_server.agent_submission import create_submission
from src.handlers.task_handlers.audio_task_handler import handle_api2_audio_submission
from src.responses.task_formaters import APPROVED_TASK_MESSAGE, SUBMISSION_RECIEVED_MESSAGE, TASK_MSG
from src.models.api2_models.projects import ProjectTaskRequestModel


router = Router()


@router.callback_query(F.data == "start_agent_task")
async def start_task(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        email = user_data.get("user_email")
        project_index = user_data.get("project_index")
        project_id = user_data.get("projects_details")[project_index]['id']
        agent_instruction = user_data.get("projects_details")[project_index].get(
            "agent_instructions", "Please translate carefully.")
        if not email or not project_id:
            await callback.message.answer("Please select a project first using /start.")
            return

        task_details = ProjectTaskRequestModel(
            project_id=project_id, email=email, status="assigned")
        allocations = await get_project_tasks_assigned_to_user(task_details)
        logger.trace(allocations)
        if not allocations:
            logger.trace(allocations)
            await callback.message.answer("No tasks available at the moment. Please check back later.")
            return

        task_list = allocations.tasks if hasattr(allocations, 'tasks') else []

        if task_list:
            ## REWRITE THIS PART TO HANDLE DIFFERENT TASK TYPES (LIKE IMAGE, VIDEO, ETC)
            first_task = task_list[0]
            if allocations.project_name == "TextTask":
                type = "Text"
            elif first_task.prompt.category == "speech":
                type = "Audio"
            else:
                logger.error(f"Unknown task category: {first_task.prompt.category}")

            task_text = first_task.prompt.sentence_text
            first_task_msg = TASK_MSG['intro'].format(
                task_type=type, task_instruction=agent_instruction, task_text=task_text)
            await callback.message.answer(first_task_msg)
            await state.update_data(project_id=project_id, task_id=first_task.task_id, assignment_id=first_task.assignment_id, prompt_id=first_task.prompt.prompt_id, sentence_id=first_task.prompt.sentence_id, task_type=type, task=first_task_msg)
            await state.set_state(TaskState.working_on_task)
            await handle_task_submission(callback.message, state)
        else:
            await callback.message.answer("No tasks available at the moment. Please check back later.")
    except Exception as e:
        logger.error(f"Error in start_task: {str(e)}")
        await callback.message.answer("Error occurred, please try again.")


async def handle_task_submission(message: Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        type = user_data.get("task_type")
        if type.lower() == "audio":
            await state.set_state(TaskState.waiting_for_audio)
        elif type.lower() == "text":
            await state.set_state(TaskState.waiting_for_text)
        elif type.lower() == "image":
            await state.set_state(TaskState.waiting_for_image)
        elif type.lower() == "video":
            await state.set_state(TaskState.waiting_for_video)
        else:
            logger.error(f"Unknown task type: {type}")
            return
    except Exception as e:
        logger.error(f"Error in handle_task_submission: {str(e)}")
        await message.answer("Error occurred, please try again.")


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
        await message.answer("Your audio submission has been received and recorded successfully. Thank you!")
        await message.answer("Begin the next task.", reply_markup=next_agent_task_inline_kb())
    else:
        errors = "\n".join(result["fail_reasons"])
        errors = ERROR_MESSAGE.format(errors=errors)
        await message.answer(errors)

@router.message(TaskState.waiting_for_audio)
async def handle_audio_task_submission(message: Message, state: FSMContext):
    try:
        if not message.voice and not message.audio:
            await message.answer("Please submit an audio file or voice message.")
            return
        await message.answer(SUBMISSION_RECIEVED_MESSAGE)

        user_data = await state.get_data()
        task_id = user_data.get("task_id")
        project_id = user_data.get("project_id")
        assignment_id = user_data.get("assignment_id")
        task_type = user_data.get("task_type").lower()
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        prompt_id = user_data.get("prompt_id")
        sentence_id = user_data.get("sentence_id")
        email = user_data.get("user_email")
        task_msg = user_data.get("task", "")
        
        ## REWRITE TO GET THE TASK INFO FROM STATE DATA
        response, new_path, out_message = await handle_api2_audio_submission(task_info={}, file_id=message.voice.file_id if message.voice else message.audio.file_id, user_id=message.from_user.id, bot=message.bot)
        if not response:
            await message.answer(out_message or "Failed to process audio submission. Please try again.")
            await message.answer(task_msg)
            logger.info("Audio submission failed")
            return

        if not all([task_id, assignment_id, prompt_id, sentence_id, email]):
            await message.answer("Session data missing. Please restart the task using /start.")
            return

        # file_info = await message.bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
        # file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}"

        submission = SubmissionModel(
            project_id=project_id,
            task_id=task_id,
            assignment_id=assignment_id,
            user_email=email,
            type=task_type,
            payload_text="",
            telegram_file_id=file_id,
        )

        submission_response = await create_submission(submission, file_path=new_path)
        if not submission_response:
            await message.answer("Failed to submit your work. Please try again.")
            return
        await message.answer("Your audio submission has been received and recorded successfully. Thank you!")
        await message.answer("Begin the next task.", reply_markup=next_agent_task_inline_kb())
    except Exception as e:
        logger.error(f"Error in handle_audio_task_submission: {str(e)}")
        await message.answer("Error occurred, please try again.")
