import logging

import librosa
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.states.tasks import TaskState
import random
from src.data.sample_text import TASK_SAMPLES
from src.keyboards.inline import create_task_action_keyboard, create_next_task_keyboard, create_task_ready_keyboard, create_ready_button

from src.utils.parameters import UserParams
from src.utils.downloader import download_telegram
from src.utils.save_audio import save_librosa_audio_as_mp3
from src.routes.task_routes.task_formaters import (TEXT_TASK_PROMPT, SELECT_TASK_TO_PERFORM,
    APPROVED_TASK_MESSAGE, ERROR_MESSAGE, SUBMISSION_RECIEVED_MESSAGE)
from src.states.tasks import TaskState, TextTaskSubmission, ImageTaskSubmission

from src.services.quality_assurance.text_validation import validate_text_input
from src.services.quality_assurance.image_validation import validate_image_input
from src.services.quality_assurance.audio_parameter_check import check_audio_parameter, TaskParameterModel
from src.services.quality_assurance.audio_quality_check import check_audio_quality
from src.services.task_distributor import assign_task, get_full_task_detail, TranslationTask
from src.handlers.audio_assignment import send_audio_question_actual_tasks,run_audio_validation_and_respond

from src.states.tasks import TaskState, TextTaskSubmission, ImageTaskSubmission, AudioTaskSubmission, VideoTaskSubmission

logger = logging.getLogger(__name__)

router = Router()



def get_unused_sample(user_data):
    # to avoid repetition of the same sample
    used_samples = user_data.get("used_samples", [])
    
    if len(used_samples) >= len(TASK_SAMPLES):
        used_samples = []
    
    available_samples = [sample for sample in TASK_SAMPLES if sample["id"] not in used_samples]
    
    #select randomly asample
    return random.choice(available_samples), used_samples

@router.message(F.text == "/welcome")
async def cmd_welcome(message: Message):
    user_name = message.from_user.first_name or "Contributor"
    welcome_text = (
        f"Welcome to EqualyzAI Task Portal, {user_name}!\n\n"
        "This is where the magic happens - find all sorts of tasks to match your skills:\n\n"
        "🔤 Translation tasks\n"
        "📝 Data collection\n" 
        "✅ Content review\n"
        "🎧 Audio work\n"
        "...and much more!\n\n"
        "Want to dive into translation tasks? start right now!\n"
        "Or explore other opportunities through the main menu.\n\n"
        "Let's start earning together! 💪"
        )  
    
    start_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Start task", callback_data="select_task_language")],
            [InlineKeyboardButton(text="Menu", callback_data="view_commands")],
            #[InlineKeyboardButton(text="View My Status", callback_data="view_status")]
        ]
    )
    
    await message.answer(welcome_text, reply_markup=start_kb)

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
    assigned_task = await assign_task("aha")
    if not assigned_task:
        await message.answer("❌ No available audio task right now.")
        await state.clear()
        return
    await send_audio_question_actual_tasks(
        message, state, task=assigned_task,
    )

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
                      sample_rate = 50000,
                      bit_depth = 32)
        
        response = check_audio_parameter(file_path, parameters)

        data, sr = librosa.load(file_path, sr=None)

        new_audio, quality_response = check_audio_quality(data = data, sr = sr)
        
        new_path = file_path.replace(".oga", "_enhanced.oga")
        save_librosa_audio_as_mp3(new_audio, sr, new_path)

        logger.info(f"New audio saved at {new_path}")
        logger.info(f"Audio check result for user {message.from_user.id}: {response.is_valid}, errors: {response.errors}, {quality_response}")

        if response.is_valid and (quality_response["message"] == "Approved"):
            await message.answer(APPROVED_TASK_MESSAGE)
            await state.clear()
        else:
            errors = ""

            if not response.is_valid:
               errors = "\n".join(response.errors)
            if quality_response["message"] != "Approved": 
                errors += f"\nQuality check message: {quality_response['message']}"
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

async def cmd_status(message: Message, state: FSMContext):
    """Status command"""
    user_data = await state.get_data()
    user_name = message.from_user.first_name or "User"
    telegram_id = message.from_user.id

    completed_tasks = user_data.get("completed_tasks", 0)
    
    status_text = (
        f"Name: {user_name}\n\n"
        f"Task Type: \n"
        f"Task Language: Yoruba\n"
        f"Batch: name\n"
        f"Number of tasks assigned: \n"
        f"Tasks Completed: {completed_tasks}\n"
        f"Number of tasks aproved:"
    )
    
    await message.answer(status_text, reply_markup=create_task_action_keyboard())

@router.callback_query(F.data == "select_task_language")
async def handle_language_selection_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.update_data(preferred_language="Yoruba", preferred_lang_code="yoruba")
    
    confirmation_text = (
        f"✅ Language: Yoruba\n\n"
        f"You'll be translating English texts to Yoruba\n\n"
        f"Ready for your first task?"
    )
    
    await callback.message.answer(confirmation_text, reply_markup=create_task_action_keyboard())


@router.callback_query(F.data == "start_translate")
async def handle_start_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    

    preferred_language = "Yoruba"
    await state.update_data(preferred_language=preferred_language, preferred_lang_code="yoruba")
    
    user_data = await state.get_data()
    current_task, used_samples = get_unused_sample(user_data)
    task_number = user_data.get("completed_tasks", 0) + 1
    

    used_samples.append(current_task["id"])
    

    await state.update_data(
        current_task=current_task, 
        current_task_number=task_number,
        used_samples=used_samples
    )
    
    task_text = (
        f"Task #{task_number}\n\n"
        f"Category: {current_task['category'].title()}\n"
        f"Translate from English to {preferred_language}:\n\n"
        f"---\n"
        f'"{current_task["text"]}"\n'
        f"---\n\n"
        f"Your {preferred_language} translation:\n"
        f"Type your translation below ⬇️"
    )
    
    await callback.message.answer(task_text)
    await state.set_state(TaskState.task_in_progress)

@router.callback_query(F.data == "get_next_task")
async def handle_get_another_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    development_text = (
        "🚧 Feature in Development\n\n"
        "The 'Get Another Task' feature is currently being develope.\n\n"
        "For now, please use 'Start Translation' to continue with regular tasks.\n\n"
        "Thank you for your patience!"
    )
    
    continue_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Start Translation", callback_data="start_translate")],
            [InlineKeyboardButton(text="Menu", callback_data="view_commands")]
        ]
    )
    
    await callback.message.answer(development_text, reply_markup=continue_kb)

@router.message(TaskState.task_in_progress)
async def handle_task_submission(message: Message, state: FSMContext):
    
    if not message.text:
        await message.answer("Please send your translation as text.")
        return
    
    user_translation = message.text.strip()
    user_data = await state.get_data()
    current_task = user_data.get("current_task")
    task_number = user_data.get("current_task_number", 1)
    preferred_language = user_data.get("preferred_language")
    
    if not current_task:
        await message.answer("No active task found. Please start a new task.")
        return
    
   
    completed_tasks = user_data.get("completed_tasks", 0) + 1

    await state.update_data(
        completed_tasks=completed_tasks,
        last_translation=user_translation
    )
    
    
    confirmation_text = (
        f"✅ Task #{task_number} Completed!\n\n"
        f"Original (English):\n"
        f'"{current_task["text"]}"\n\n'
        f"Your {preferred_language} translation:\n"
        f'"{user_translation}"\n\n'
        f"Status: Submitted for validation"
    )
    
    await message.answer(confirmation_text)
    
    # Simulation 
    await simulate_task_validation(message, state)

async def simulate_task_validation(message: Message, state: FSMContext):
    """Validation simulation"""
    import asyncio
    
    await asyncio.sleep(1)  
    
    user_data = await state.get_data()
    current_task = user_data.get("current_task")
    completed_tasks = user_data.get("completed_tasks", 0)
    

    validation_result = random.random() > 0.1
    
    if validation_result:
        success_text = (
            f"🎉 Task Approved!\n\n"
            f"✅ Great work! Your translation has been accepted.\n"
            f"Tasks completed: {completed_tasks}\n\n"
            f"Ready for your next challenge?"
        )
        
        next_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Next task", callback_data="start_translate")],
                [InlineKeyboardButton(text="Menu", callback_data="view_commands")],
            ]
        )
        
        await message.answer(success_text, reply_markup=next_kb)
        
        # Log admin
        print(f"✅ TASK APPROVED - User {message.from_user.id}, Task #{completed_tasks}")
        print(f"Translation: {user_data.get('last_translation')}")
        
    else:
        failure_text = (
            f"Task needs revision\n\n"
            f"Please review and improve your translation.\n"
            f"💡 Tip: Focus on accuracy and natural flow.\n\n"
            f"Try again?"
        )
        
        retry_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Retry Task", callback_data="start_translate")],
                [InlineKeyboardButton(text="Menu", callback_data="view_commands")]
            ]
        )
        
        await message.answer(failure_text, reply_markup=retry_kb)
    
    await state.set_state(TaskState.task_completed)
