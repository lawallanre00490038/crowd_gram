import logging

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.utils.parameters import UserParams
from src.utils.downloader import download_telegram
from src.handlers.task_routes.task_formaters import (TEXT_TASK_PROMPT, SELECT_TASK_TO_PERFORM,
    APPROVED_TASK_MESSAGE, ERROR_MESSAGE, SUBMISSION_RECIEVED_MESSAGE)
from src.states.tasks import TaskState, TextTaskSubmission, ImageTaskSubmission

from src.services.quality_assurance.text_validation import validate_text_input
from src.services.quality_assurance.image_validation import validate_image_input
from src.services.quality_assurance.audio_parameter_check import check_audio_parameter, TaskParameterModel
from src.services.task_distributor import assign_task, get_full_task_detail, TranslationTask

from src.states.tasks import TaskState, TextTaskSubmission, ImageTaskSubmission, AudioTaskSubmission, VideoTaskSubmission

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "/welcome")
async def cmd_welcome(message: Message):
    await message.answer("Welcome to the task portal!")

@router.message(F.text == "/status")
async def cmd_status(message: Message):
    # Fetch and display agent's status
    await message.answer("Your task status: ...")

@router.message(F.text == "/start_task")
async def cmd_start_task(message: Message, state: FSMContext):
    await message.answer(SELECT_TASK_TO_PERFORM)
    await state.set_state(TaskState.waiting_for_task)

@router.message(TaskState.waiting_for_task, F.text == "/text_task")
async def cmd_start_task(message: Message, state: FSMContext):
    # Start a new task
    login_identifier = await state.get_value(UserParams.LOGIN_IDENTIFIER.value)
    assigned_task = await assign_task(login_identifier)

    user_message = TEXT_TASK_PROMPT.format(**assigned_task.model_dump())
    await message.answer(user_message)
    await state.set_state(TextTaskSubmission.waiting_for_text)
    await state.set_data({UserParams.TASK_INFO.value: assigned_task.model_dump()})

    logger.info(f"User {message.from_user.id} with {login_identifier} started a new task: {assigned_task.category}")

@router.message(TaskState.waiting_for_task, F.text == "/audio_task")
async def cmd_start_task(message: Message, state: FSMContext):
    await message.answer("Sample Audio task")
    assigned_task = await assign_task("aha")
    await state.set_data({UserParams.TASK_INFO.value: assigned_task.model_dump()})
    await state.set_state(AudioTaskSubmission.waiting_for_audio)

@router.message(TaskState.waiting_for_task, F.text == "/image_task")
async def cmd_start_task(message: Message, state: FSMContext):
    await message.answer("Sample Image task")
    await state.set_state(ImageTaskSubmission.waiting_for_image)

@router.message(TaskState.waiting_for_task, F.text == "/video_task")
async def cmd_start_task(message: Message, state: FSMContext):
    await message.answer("Sample Video task")
    await state.set_state(VideoTaskSubmission.waiting_for_video)

@router.message(F.text == "/exit")
async def cmd_exit(message: Message, state: FSMContext):
    await message.answer("Exiting task selection. Type /start_task to begin again.")
    await state.clear()

@router.message(AudioTaskSubmission.waiting_for_audio)
async def handle_audio_input(message: Message, state: FSMContext, bot: Bot):
    task_info = await state.get_value(UserParams.TASK_INFO.value)

    task_info = TranslationTask(**task_info) 
    
    task_full_details = await get_full_task_detail(task_info.task_id)

    login_identifier = await state.get_value(UserParams.LOGIN_IDENTIFIER.value)
    logger.info(f"User {message.from_user.id} with {login_identifier} submitted task: {task_info.task_id}")

    if message.voice:
        await message.answer(SUBMISSION_RECIEVED_MESSAGE)
        file_path = await download_telegram(message.voice.file_id, bot=bot)
        parameters = TaskParameterModel(min_duration= task_full_details.min_duration.total_seconds(), 
                      max_duration = task_full_details.max_duration.total_seconds(),
                      language = task_full_details.required_language, 
                      expected_format = "oga",
                      sample_rate = 48000,
                      bit_depth = 32)
        
        response = check_audio_parameter(file_path, parameters)
        logger.info(f"Audio check result for user {message.from_user.id}: {response.is_valid}, errors: {response.errors}")

        if response.is_valid:
            await message.answer(APPROVED_TASK_MESSAGE)
            await state.clear()

        else:
            errors = "\n".join(response.errors)
            errors = ERROR_MESSAGE.format(errors=errors)

            logger.info(f"Audio submission failed for user {message.from_user.id}: {errors}")

            await message.answer(errors)
    
    else:
        await message.answer("Please. Record a audio")


@router.message(TextTaskSubmission.waiting_for_text)
async def handle_text_input(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()

    task_id = data.get("task_id")
    task_lang = data.get("task_lang", "en")
    task_script = data.get("task_script", "LATIN").upper()
    user_id = message.from_user.id

    result = validate_text_input(text, task_lang=task_lang,exp_task_script=task_script)

    if result["success"]:
        await message.answer(APPROVED_TASK_MESSAGE)        
       
        await state.clear()
    else:
        errors = "\n".join(result["fail_reasons"])
        errors = ERROR_MESSAGE.format(errors=errors)
        await message.answer(errors)


@router.message(ImageTaskSubmission.waiting_for_image)
async def handle_image_input(message: Message, state: FSMContext):
    image_file = None

    # If sent as a photo (Telegram auto-compressed image)
    if message.photo:
        image_file = message.photo[-1]  # Highest resolution

    # If sent as a document with mime type = image/*
    elif message.document and message.document.mime_type.startswith("image/"):
        image_file = message.document

    # Not a supported image
    else:
        await message.answer("⚠️ Please upload a valid image (JPG, PNG, or WEBP).")
        return
    
    # Download the image to a temporary file
    local_path = await download_telegram(image_file.file_id, bot=message.bot)
    # Continue with validation
    result = validate_image_input(local_path)

    if result["success"]:
        await message.answer(APPROVED_TASK_MESSAGE)
        
        await state.clear()
    else:
        await message.answer(
            "Image failed the quality check:\n\n" +
            "\n".join(f"• {reason}" for reason in result["fail_reasons"])
        )
