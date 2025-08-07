from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json

router = Router()

# États pour Test Your Knowledge
class TestKnowledge(StatesGroup):
    ready_to_start = State()
    language_selection = State()
    translation_task = State()
    validation_pending = State()

# Textes samples pour traduction (seulement English source)
SAMPLE_TEXTS = {
    "english_to_french": {
        "source_lang": "English", 
        "target_lang": "French",
        "text": "Artificial intelligence is transforming the way we work. It's important to learn and adapt."
    },
    "english_to_hausa": {
        "source_lang": "English", 
        "target_lang": "Hausa",
        "text": "Education opens the door to a better future. Keep learning and growing."
    },
    "english_to_swahili": {
        "source_lang": "English", 
        "target_lang": "Swahili",
        "text": "Climate change is a global issue. We must all act to protect the environment."
    },
    "english_to_yoruba": {
        "source_lang": "English", 
        "target_lang": "Yoruba",
        "text": "Technology is changing the world rapidly. We must adapt to these changes to succeed in the future."
    },
    "english_to_igbo": {
        "source_lang": "English", 
        "target_lang": "Igbo",
        "text": "Health is wealth. Eating well and staying active keeps the mind and body strong."
    },
    "english_to_pidgin": {
        "source_lang": "English", 
        "target_lang": "Pidgin",
        "text": "Make sure you understand the task before you start. Take your time and do your best."
    },
    "english_to_default": {  
        "source_lang": "English", 
        "target_lang": "Default",
        "text": "Welcome to our translation platform. Your skills help us build better AI systems."
    }
}

# Langues disponibles pour la traduction
AVAILABLE_LANGUAGES = [
    ("English", "english"),
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
     #add more languages later --> these corespond to the ones on the equalyz paltform 
]

def create_ready_button():
    """Bouton Ready to start"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yes I'm ready!", callback_data="ready_start")]
        ]
    )

def create_language_selection_keyboard():
    """Clavier pour sélection de langue"""
    buttons = []
    for lang_name, lang_code in AVAILABLE_LANGUAGES:
        buttons.append([InlineKeyboardButton(text=f"🌍 {lang_name}", callback_data=f"lang_{lang_code}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_task_ready_keyboard():
    """Bouton pour commencer la tâche de traduction"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ I understand, let's begin!", callback_data="begin_translation")]
        ]
    )

@router.message(F.text == "/start_test_knowledge")
async def start_knowledge_test(message: Message, state: FSMContext):
    """Point d'entrée pour Test Your Knowledge"""
    await handle_start_knowledge_assessment(message, state)

async def handle_start_knowledge_assessment(message: Message, state: FSMContext):
    """Fonction appelée depuis onboarding pour démarrer l'assessment"""
    
    welcome_text = (
        " Next Step: Knowledge Assessment\n\n"
        "Before you start earning, we'll test your knowledge with a few practical tasks:\n"
        "• 📝 Text annotation\n"
        "• 🎵 Audio transcription\n" 
        "• 🖼️ Image classification\n"
        "• 🎥 Video analysis\n\n"
        "This helps us assign you the right tasks for your skill level!\n\n"
         "🚀 Ready to take the test?\n"
    )
    await message.answer(welcome_text, reply_markup=create_ready_button())
    await state.set_state(TestKnowledge.ready_to_start)

@router.callback_query(TestKnowledge.ready_to_start, F.data == "ready_start")
async def handle_ready_start(callback: CallbackQuery, state: FSMContext):
    """Utilisateur a cliqué Ready to start"""
    await callback.answer()
    
    instructions_text = (
        "Awesome!\n"
        "Let's start with the text translation task!\n\n"  
        " 📋 Instructions:\n"
        "• You'll receive a short text\n"
        "• Translate it accurately to your chosen target language\n"
        "• Write your translation as a text message\n"
        "• Focus on accuracy and natural flow\n\n"
        "🌍 Please select the language you would like to do the task:"
    )
      
    await callback.message.answer(instructions_text, reply_markup=create_language_selection_keyboard())
    await state.set_state(TestKnowledge.language_selection)

@router.callback_query(TestKnowledge.language_selection, F.data.startswith("lang_"))
async def handle_language_selection(callback: CallbackQuery, state: FSMContext):
    """Gestion de la sélection de langue"""
    await callback.answer()
    
    selected_lang_code = callback.data.replace("lang_", "")
    
    # Trouver le nom complet de la langue
    selected_lang_name = None
    for lang_name, lang_code in AVAILABLE_LANGUAGES:
        if lang_code == selected_lang_code:
            selected_lang_name = lang_name
            break
    
    if not selected_lang_name:
        await callback.message.answer(" ❌ Language selection error. Please try again.")
        return
    
    # Sauvegarder la langue sélectionnée
    await state.update_data(target_language=selected_lang_name, target_lang_code=selected_lang_code)
    
    # Sélectionner un texte sample approprié
    sample_key = select_sample_text(selected_lang_code)
    sample_data = SAMPLE_TEXTS[sample_key]
    
    await state.update_data(
        sample_key=sample_key,
        source_language=sample_data["source_lang"],
        sample_text=sample_data["text"]
    )
    
    task_preview_text = (
        f"Great! You selected: {selected_lang_name}\n\n"
        f"📝 Your task:\n"
        f" Translate the following {sample_data['source_lang']} text to {selected_lang_name} and submit it as a message.\n\n"
        f" Make sure the translation is accurate and natural!\n\n"
        f"Ready to see the text?"
    )
    
    await callback.message.answer(task_preview_text, reply_markup=create_task_ready_keyboard())

def select_sample_text(target_lang_code):
    """Sélectionne le texte sample approprié selon la langue cible"""
    sample_map = {
        "français": "english_to_french",
        "yoruba": "english_to_yoruba", 
        "hausa": "english_to_hausa",
        "swahili": "english_to_swahili",
        "igbo": "english_to_igbo",
        "pidgin": "english_to_pidgin",       
    }


    
    return sample_map.get(target_lang_code, "english_to_default")  # Par défaut si langue non trouvée

@router.callback_query(TestKnowledge.language_selection, F.data == "begin_translation")
async def handle_begin_translation(callback: CallbackQuery, state: FSMContext):
    """Affichage du texte à traduire"""
    await callback.answer()
    
    data = await state.get_data()
    target_language = data.get("target_language")
    source_language = data.get("source_language") 
    sample_text = data.get("sample_text")
    
    translation_text = (
        f"Great! Here is the text to translate from {source_language} to {target_language}:\n\n"
        f"---\n"
        f'"{sample_text}"\n'
        f"---\n\n"
        f"Your {target_language} translation:\n"
        f"Type your translation below ⬇️"
    )
    
    await callback.message.answer(translation_text)
    await state.set_state(TestKnowledge.translation_task)

@router.message(TestKnowledge.translation_task)
async def handle_translation_submission(message: Message, state: FSMContext):
    """Gestion de la soumission de traduction"""
    
    if not message.text:
        await message.answer(" ❌ Please send your translation as text.")
        return
        
    user_translation = message.text.strip()
    data = await state.get_data()
    
    # Sauvegarder la traduction
    await state.update_data(user_translation=user_translation)
    
    target_language = data.get("target_language")
    source_language = data.get("source_language")
    sample_text = data.get("sample_text")
    
    # Confirmation de soumission
    confirmation_text = (
        "✅ Translation Received!\n\n"  
        f"Original ({source_language}):\n"
        f'"{sample_text}"\n\n'
        f"Your {target_language} translation:\n"  
        f'"{user_translation}"\n\n'
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )
    
    await message.answer(confirmation_text)
    
    # Simulation de validation (2-3 secondes)
    await simulate_validation(message, state)

async def simulate_validation(message: Message, state: FSMContext):
    """Simulation du processus de validation"""
    import asyncio
    
    # Attendre 3 secondes pour simuler la validation
    await asyncio.sleep(3)
    
    data = await state.get_data()
    user_data = await state.get_data()
    
    # Pour l'instant, on approuve automatiquement
    validation_result = True  # TODO: Logique de validation réelle
    
    if validation_result:


        await message.answer(
            "(simulation) Good job! You have successfully completed the task ✅ " \
            "Your task has been approved!\n" 
            "Now, let's continue with the next task... [audio, image, video...)]")
        
        await asyncio.sleep(3)

        success_text = (
            "🎉 (simulation) Congratulations! Test Passed!\n"  
            "You're now eligible for real tasks!\n\n" \
            "Ready to start earning?"
        )
        
        await message.answer(success_text)
        
        # Bouton pour accéder aux tâches réelles
        start_tasks_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Start Real Tasks", callback_data="start_real_tasks")],
                [InlineKeyboardButton(text="View Commands", callback_data="view_commands")]
            ]
        )
        
        await message.answer(
            "Click below to access the task portal:",
            reply_markup=start_tasks_kb
        )

        

        #add task for audio, image (...)
        # Log pour l'admin
        print(f"✅ ASSESSMENT PASSED - User {message.from_user.id}")
        print(f"Translation: {data.get('user_translation')}")
        
    else:
        failure_text = (
            "Assessment needs improvement\n\n"
            "Feedback: Your translation needs some work\n"
            "Next step: Please try the assessment again\n"
            "Tip: Review translation guidelines and try again"
        )
        
        await message.answer(failure_text)
    
    await state.clear()

@router.callback_query(F.data == "start_real_tasks")
async def handle_start_real_tasks(callback: CallbackQuery, state: FSMContext):
    """Redirection vers les tâches réelles"""
    await callback.answer()
    
    # Import local pour éviter circular imports
    from src.handlers.task_routes.tasks import cmd_welcome
    
    redirect_text = (
        "🎉 Redirecting to Task Portal...\n\n"  
        "Time to start earning with real tasks!\n"
        "Use /welcome anytime to access the task portal."
    )
    
    await callback.message.answer(redirect_text)
    
    # Appeler directement la fonction welcome du module tasks
    await cmd_welcome(callback.message)  

@router.callback_query(F.data == "view_commands")
async def handle_view_commands(callback: CallbackQuery, state: FSMContext):
    """Afficher les commandes disponibles"""
    await callback.answer()
    
    commands_text = (
        "Menu :\n"
        "/welcome - Access task portal\n"
        "/status - Check your progress\n"
        "/leaderboard\n"
        "/payment\n"
        "/support\n" 
        "💡 Quick tip: Use /welcome to start your first real task!"
    )
    
    start_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Go to Tasks", callback_data="start_real_tasks")]
        ]
    )
    
    await callback.message.answer(commands_text, reply_markup=start_kb)

# Fonction pour intégrer dans onboarding
async def start_knowledge_assessment(message: Message, state: FSMContext):
    """Fonction appelée depuis onboarding_routes pour démarrer l'assessment"""
    await handle_start_knowledge_assessment(message, state)