from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold
from src.keyboards.inline import quiz_options_kb
from src.states.test_knowledge import TestKnowledge
from src.utils.test_knowledge import create_language_selection_keyboard, create_ready_button, create_task_ready_keyboard
from src.constant.test_knowledge_constant import AVAILABLE_LANGUAGES, SAMPLE_TEXTS
import json
import random
import asyncio

router = Router()

# Load image quiz data
with open("src/data/image_quiz.json", 'r') as f:
    image_quiz_data = json.load(f)

# Pick 2 images task @random
image_tasks = random.sample(image_quiz_data, 2)


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
        
        
        # Start image assessment
        await asyncio.sleep(3)
        
        # Image assessment instructions
        image_instructions_text = (
            "Great!\n"
            "Let's move to Image Annotation task!\n\n"
            "📋 Instructions:\n"
            "• You'll receive an image with description options\n"
            "• Select the best option that best describes the image\n\n"
            "Ready to begin the image test?"
        )
        
        image_ready_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🖼️ Start Image Test", callback_data="start_image_test")]
            ]
        )
        
        await message.answer(image_instructions_text, reply_markup=image_ready_kb)
        await state.set_state(TestKnowledge.image_instructions)
        
        # Log pour l'admin
        print(f"✅ TRANSLATION PASSED - User {message.from_user.id}")
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

# Image Assessment Handlers
@router.callback_query(TestKnowledge.image_instructions, F.data == "start_image_test")
async def handle_start_image_test(callback: CallbackQuery, state: FSMContext):
    """Start the image assessment"""
    await callback.answer()
    
    # Initialize image quiz data
    await state.update_data(current_q=0, num_q=2)
    await state.set_state(TestKnowledge.image_quiz)
    
    # Send first image question
    await send_image_question(callback.message, state)

async def send_image_question(message: Message, state: FSMContext):
    """Send an image quiz question"""
    data = await state.get_data()
    q_index = data["current_q"]
    
    if not image_quiz_data:
        await message.answer("❌ No quiz data available")
        return
    
    if q_index >= len(image_quiz_data):
        await message.answer("❌ Question index out of range")
        return
    
    selected_question = image_tasks[q_index]
    print(f"📝 Selected question: {selected_question}")
    
    try:
        # Use FSInputFile for local image files
        image_file = FSInputFile(selected_question['image'])
        await message.answer_photo(
            photo=image_file,
            caption=f"❓{hbold(selected_question['question'])}",
            reply_markup=quiz_options_kb(selected_question['options'])
        )
        print("✅ Image sent successfully")
        await state.set_state(TestKnowledge.image_quiz_feedback)
    except Exception as e:
        print(f"❌ Error sending image: {e}")
        await message.answer(f"❌ Error loading image: {e}")
        # Try without image for debugging
        await message.answer(
            f"❓{hbold(selected_question['question'])}",
            reply_markup=quiz_options_kb(selected_question['options'])
        )
        await state.set_state(TestKnowledge.image_quiz_feedback)

@router.callback_query(TestKnowledge.image_quiz_feedback)
async def handle_image_answer(callback: CallbackQuery, state: FSMContext):
    """Handle image quiz answers"""
    await callback.answer()

    data = await state.get_data()
    q_index = data['current_q']
    num_q = data.get('num_q', 0)

    # Extract option index from callback data (format: "opt_0", "opt_1", etc.)
    if not callback.data.startswith("opt_"):
        await callback.message.answer("❌ Invalid answer format")
        return
    
    try:
        option_index = int(callback.data.replace("opt_", ""))
        selected_question = image_tasks[q_index]
        
        # Get the actual answer text from the option index
        if option_index >= len(selected_question['options']):
            await callback.message.answer("❌ Invalid option selected")
            return
            
        user_answer = selected_question['options'][option_index]
        correct_answer = selected_question['answer']

        if user_answer == correct_answer:
            await callback.message.answer("✅ Correct!")
            
            num_q -= 1

            if num_q > 0:
                await state.update_data(num_q=num_q, current_q=1)
                await send_image_question(callback.message, state)
            else:
                # Image assessment completed!
                await callback.message.answer("🎉 Image annotation test completed!")

                await asyncio.sleep(3)

                success_text = (
                    "🎉 (simulation) Congratulations! Test Passed!\n"  
                    "You're now eligible for real tasks!\n\n" \
                    "Ready to start earning?"
                )
        

            
                await callback.message.answer(success_text)

                # Clear state
                await state.clear()
                
                # Show final completion buttons
                start_tasks_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Start Real Tasks", callback_data="start_real_tasks")],
                        [InlineKeyboardButton(text="View Commands", callback_data="view_commands")]
                    ]
                )
                
                await callback.message.answer(
                    "🎉 All assessments completed!\n\nClick below to access the task portal:",
                    reply_markup=start_tasks_kb
                )
                
        else:
            await callback.message.answer("❌ Incorrect.")
            await callback.message.answer("Let's try again one more time.")
            # await state.update_data(num_q=num_q, current_q=q_index)
            await send_image_question(callback.message, state)
            
    except ValueError:
        await callback.message.answer("❌ Invalid answer format")
        await send_image_question(callback.message, state)
        
    

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