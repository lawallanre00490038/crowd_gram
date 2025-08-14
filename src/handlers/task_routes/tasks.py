from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.states.tasks import TaskState
import random
from src.data.sample_text import TASK_SAMPLES
from src.keyboards.inline import create_task_action_keyboard, create_next_task_keyboard, create_task_ready_keyboard, create_ready_button

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
