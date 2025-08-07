from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.states.tasks import TaskState
import random

router = Router()


TASK_SAMPLES = [
    {
        "id": 1,
        "text": "The internet has revolutionized how we communicate and share information globally.",
        "category": "technology",
        "difficulty": "easy"
    },
    {
        "id": 2, 
        "text": "Sustainable agriculture practices help protect the environment while feeding growing populations.",
        "category": "environment",
        "difficulty": "medium"
    },
    {
        "id": 3,
        "text": "Financial literacy is essential for making informed decisions about saving and investing money.",
        "category": "finance",
        "difficulty": "medium"
    },
    {
        "id": 4,
        "text": "Regular exercise and a balanced diet contribute significantly to overall health and well-being.",
        "category": "health",
        "difficulty": "easy"
    },
    {
        "id": 5,
        "text": "Artificial intelligence and machine learning are transforming industries across the globe.",
        "category": "technology", 
        "difficulty": "hard"
    },
    {
        "id": 6,
        "text": "Education opens doors to opportunities and helps build stronger communities.",
        "category": "education",
        "difficulty": "easy"
    },
    {
        "id": 7,
        "text": "Climate change requires immediate action from governments, businesses, and individuals worldwide.",
        "category": "environment",
        "difficulty": "hard"
    },
    {
        "id": 8,
        "text": "Small businesses play a crucial role in local economic development and job creation.",
        "category": "business",
        "difficulty": "medium"
    },
    {
        "id": 9,
        "text": "Cultural diversity enriches societies and promotes understanding between different communities.",
        "category": "culture",
        "difficulty": "medium"
    },
    {
        "id": 10,
        "text": "Innovation in renewable energy sources is key to achieving sustainable development goals.",
        "category": "energy",
        "difficulty": "hard"
    },
   
    {
        "id": 11,
        "text": "Social media platforms connect people across the world but also raise privacy concerns.",
        "category": "technology",
        "difficulty": "medium"
    },
    {
        "id": 12,
        "text": "Clean water access remains a critical challenge in many developing countries.",
        "category": "health",
        "difficulty": "easy"
    },
    {
        "id": 13,
        "text": "Renewable energy investments are essential for reducing global carbon emissions.",
        "category": "environment",
        "difficulty": "medium"
    },
    {
        "id": 14,
        "text": "Digital payment systems are transforming how businesses and consumers handle transactions.",
        "category": "finance",
        "difficulty": "medium"
    },
    {
        "id": 15,
        "text": "Remote work has become more common since the global pandemic changed workplace dynamics.",
        "category": "business",
        "difficulty": "easy"
    }
]

AVAILABLE_LANGUAGES = [
    ("French", "français"), 
    ("Fulani", "fulani"),
    ("Hausa", "hausa"),
    ("Hindi", "hindi"),
    ("Igbo", "igbo"),
    ("Pidgin", "pidgin"),
    ("Punjabi", "punjabi"),
    ("Shona", "shona"),
    ("Swahili", "swahili"),
    ("Yoruba", "yoruba")
]

def create_language_keyboard():
    buttons = []
    for lang_name, lang_code in AVAILABLE_LANGUAGES:
        buttons.append([InlineKeyboardButton(text=f"🌍 {lang_name}", callback_data=f"task_lang_{lang_code}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_task_action_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Start Translation", callback_data="start_translate")],
            [InlineKeyboardButton(text="Get Another Task", callback_data="get_next_task")],
            [InlineKeyboardButton(text="View Progress", callback_data="view_progress")]
        ]
    )

def create_next_task_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Next Task", callback_data="get_next_task")],
            [InlineKeyboardButton(text="View Progress", callback_data="view_progress")],
        ]
    )

def get_unused_sample(user_data):
    """Récupère un sample non utilisé pour éviter les répétitions"""
    used_samples = user_data.get("used_samples", [])
    
    # Si tous les samples ont été utilisés, réinitialiser
    if len(used_samples) >= len(TASK_SAMPLES):
        used_samples = []
    
    # Filtrer les samples non utilisés
    available_samples = [sample for sample in TASK_SAMPLES if sample["id"] not in used_samples]
    
    # Sélectionner aléatoirement parmi les disponibles
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
        "Want to dive into translation tasks? Pick a language below! 👇\n"
        "Or explore other opportunities through the main menu.\n\n"
        "Let's start earning together! 💪"
        )


  
    
    start_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Select Language & Start task", callback_data="select_task_language")],
            [InlineKeyboardButton(text="View Commands", callback_data="view_commands")],
            [InlineKeyboardButton(text="View My Status", callback_data="view_status")]
        ]
    )
    
    await message.answer(welcome_text, reply_markup=start_kb)

@router.message(F.text == "/status")
async def cmd_status(message: Message, state: FSMContext):
    """Status command"""
    user_data = await state.get_data()
    user_name = message.from_user.first_name or "User"
    telegram_id = message.from_user.id

    # Simulation for now 
    completed_tasks = user_data.get("completed_tasks", 0)
    preferred_language = user_data.get("preferred_language", "Not set")
    
    status_text = (
        f"Status for {user_name}\n\n"
        f"Telegram ID: {telegram_id}\n"
        f"Account Status: Active\n"
        f"Preferred Language: {preferred_language}\n"
        f"Tasks Completed: {completed_tasks}/∞\n\n"
        f"Ready for your next task?"
    )
    
    await message.answer(status_text, reply_markup=create_task_action_keyboard())

@router.callback_query(F.data == "select_task_language")
async def handle_language_selection_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    lang_text = (
        "Choose Your Translation Language\n\n"
        "Select the language you want to translate the texts to:\n\n"
        "💡 Tip: Choose the language you're most fluent in!"
    )
    
    await callback.message.answer(lang_text, reply_markup=create_language_keyboard())
    await state.set_state(TaskState.language_selection)

@router.callback_query(TaskState.language_selection, F.data.startswith("task_lang_"))
async def handle_task_language_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    selected_lang_code = callback.data.replace("task_lang_", "")
    
    # Trouver le nom de la langue
    selected_lang_name = None
    for lang_name, lang_code in AVAILABLE_LANGUAGES:
        if lang_code == selected_lang_code:
            selected_lang_name = lang_name
            break
    
    if not selected_lang_name:
        await callback.message.answer("Language selection error. Please try again.")
        return
    
    # Sauvegarder la préférence
    await state.update_data(preferred_language=selected_lang_name, preferred_lang_code=selected_lang_code)
    
    confirmation_text = (
        f"✅ Language Selected: {selected_lang_name}\n\n"
        f"You'll be translating English texts to {selected_lang_name}\n\n"
        f"Ready for your first task?"
    )
    
    await callback.message.answer(confirmation_text, reply_markup=create_task_action_keyboard())

@router.callback_query(F.data == "start_translate")
async def handle_start_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    user_data = await state.get_data()
    preferred_language = user_data.get("preferred_language")
    
    if not preferred_language:
        await callback.message.answer(
            "Please select a language first!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="🌍 Select Language", callback_data="select_task_language")]]
            )
        )
        return
    
   
    current_task, used_samples = get_unused_sample(user_data)
    task_number = user_data.get("completed_tasks", 0) + 1
    
    # Marquer ce sample comme utilisé
    used_samples.append(current_task["id"])
    
    # Sauvegarder la tâche courante et les samples utilisés
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
            [InlineKeyboardButton(text="View Progress", callback_data="view_progress")]
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
    
    # Mettre à jour stats utilisateur
    completed_tasks = user_data.get("completed_tasks", 0) + 1

    await state.update_data(
        completed_tasks=completed_tasks,
        last_translation=user_translation
    )
    
    # Confirmation de soumission
    confirmation_text = (
        f"✅ Task #{task_number} Completed!\n\n"
        f"Original (English):\n"
        f'"{current_task["text"]}"\n\n'
        f"Your {preferred_language} translation:\n"
        f'"{user_translation}"\n\n'
        f"Status: Submitted for validation"
    )
    
    await message.answer(confirmation_text)
    
    # Simulation validation rapide
    await simulate_task_validation(message, state)

async def simulate_task_validation(message: Message, state: FSMContext):
    """Validation simulation"""
    import asyncio
    
    await asyncio.sleep(2)  # Validation rapide pour les tâches
    
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
                [InlineKeyboardButton(text="Start Translation", callback_data="start_translate")],
                [InlineKeyboardButton(text="View Progress", callback_data="view_progress")],
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
                [InlineKeyboardButton(text="View Progress", callback_data="view_progress")]
            ]
        )
        
        await message.answer(failure_text, reply_markup=retry_kb)
    
    await state.set_state(TaskState.task_completed)

@router.callback_query(F.data.in_(["view_progress", "view_status"]))
async def handle_view_progress(callback: CallbackQuery, state: FSMContext):
    """Afficher progression utilisateur"""
    await callback.answer()
    
    user_data = await state.get_data()
    completed_tasks = user_data.get("completed_tasks", 0)
    preferred_language = user_data.get("preferred_language", "Not set")
    used_samples = user_data.get("used_samples", [])
    
    progress_text = (
        f"Your Progress Report:\n\n"
        f"Tasks Completed: {completed_tasks}\n"
        f"Active Language: {preferred_language}\n"
        f"Unique texts seen: {len(used_samples)}/{len(TASK_SAMPLES)}\n\n"
        f"Keep up the great work!"
    )
    
    await callback.message.answer(progress_text, reply_markup=create_task_action_keyboard())

@router.message(TaskState.waiting_for_submission)
async def handle_submission(message: Message, state: FSMContext):
    """Legacy handler"""
    await message.answer("Please use /welcome to start tasks properly.")
    await state.clear()