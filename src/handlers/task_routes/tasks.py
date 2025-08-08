import logging

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.states.tasks import TaskState
from src.utils.parameters import UserParams
from src.utils.downloader import download_telegram
from src.services.task_distributor import assign_task, get_full_task_detail, TranslationTask
from src.services.quality_assurance.audio_parameter_check import check_audio_parameter, TaskParameterModel
from src.handlers.task_routes.task_formaters import TEXT_TASK_PROMPT

logger = logging.getLogger(__name__)

from src.states.tasks import TaskState, TextTaskSubmission, ImageTaskSubmission
from ...services.quality_assurance.text_validation import validate_text_input
from ...services.quality_assurance.image_validation import validate_image_input

from src.states.tasks import TaskState, TextTaskSubmission, ImageTaskSubmission
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
    # Start a new task
    login_identifier = await state.get_value(UserParams.LOGIN_IDENTIFIER.value)
    assigned_task = await assign_task(login_identifier)

    user_message = TEXT_TASK_PROMPT.format(**assigned_task.model_dump())
    await message.answer(user_message)
    await state.set_state(TaskState.waiting_for_submission)
    await state.set_data({UserParams.TASK_INFO.value: assigned_task.model_dump()})

    logger.info(f"User {message.from_user.id} with {login_identifier} started a new task: {assigned_task.category}")

@router.message(TaskState.waiting_for_submission)
async def handle_submission(message: Message, state: FSMContext, bot: Bot):
    task_info = await state.get_value(UserParams.TASK_INFO.value)

    task_info = TranslationTask(**task_info) 
    
    task_full_details = await get_full_task_detail(task_info.task_id)

    login_identifier = await state.get_value(UserParams.LOGIN_IDENTIFIER.value)
    logger.info(f"User {message.from_user.id} with {login_identifier} submitted task: {task_info.task_id}")

    if message.voice:
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
            await message.answer("Your Audio is approved")
            await state.clear()

        else:
            errors = "\n".join(response.errors)
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
        await message.answer("Submission Passed.\n\nTo get the next task, type /next.")        
       
        await state.clear()
    else:
        await message.answer(
            "Your submission has some issues:\n\n" +
            "\n".join(f"• {reason}" for reason in result["fail_reasons"])
        )


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

    # Download the image
    file_info = await message.bot.get_file(image_file.file_id)
    file_path = file_info.file_path
    local_path = f"media/images/{image_file.file_id}.jpg"  # You can preserve original ext if needed

    await message.bot.download_file(file_path, destination=local_path)

    # Continue with validation
    result = validate_image_input(local_path)

    if result["success"]:
        await message.answer("Image submitted successfully.\n\nTo get the next task, type /next.")
        
        await state.clear()
    else:
        await message.answer(
            "Image failed the quality check:\n\n" +
            "\n".join(f"• {reason}" for reason in result["fail_reasons"])
        )
