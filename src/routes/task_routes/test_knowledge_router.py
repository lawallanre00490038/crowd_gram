from aiogram import Router,F,Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, Command
from aiogram.utils.markdown import hbold
from src.keyboards.inline import quiz_options_kb
from src.states.test_knowledge import TestKnowledge
from src.utils.test_knowledge import create_ready_button, load_json_file
from src.constant.test_knowledge_constant import AVAILABLE_LANGUAGES, SAMPLE_TEXTS
from src.handlers.task_handlers.image_handlers.image_task_output_handler import handle_image_task
from src.handlers.task_handlers.image_handlers.review_handler import handle_image_task_review
import random
import asyncio
import os
import tempfile
from pathlib import Path
from src.services.quality_assurance.audio_validation import validate_audio_input
from src.services.quality_assurance.audio_parameter_check import TaskParameterModel
from src.handlers.task_handlers.audio_task_handler import send_audio_question_test_knowledge, handle_audio_submission
from src.handlers.task_handlers.video_handlers.video_task_output_handler import handle_video_task
from src.handlers.task_handlers.video_handlers.video_review_handler import handle_video_task_review


router = Router()


# Load image quiz data
quiz_data = load_json_file(Path("src/data/test_knowledge_quiz.json"))
image_items = [i for i in quiz_data if i.get('category_type') == 'image']

if not image_items:
    image_data = []  # or handle the error, e.g., raise Exception("No image items found!")
elif len(image_items) >= 4:
    image_data = random.sample(image_items, 4)
else:
    image_data = image_items 

video_items = [i for i in quiz_data if i.get('category_type') == 'video']

if not video_items:
    video_data = []
elif len(video_items) >= 4:
    video_data = random.sample(video_items, 4)

# Load test_your_knowledge audio quiz data
audio_quiz_data = load_json_file(Path("src/data/audio_quiz.json"))  
audio_tasks = random.sample(audio_quiz_data, 2)




@router.message(F.text == "/start_test_knowledge")
async def start_knowledge_test(message: Message, state: FSMContext):
    """Point d'entrée pour Test Your Knowledge"""
    await handle_start_knowledge_assessment(message, state)

async def handle_start_knowledge_assessment(message: Message, state: FSMContext):
    """Fonction appelée depuis onboarding pour démarrer l'assessment"""
    
    welcome_text = (
        "🧠 Next Step: Knowledge Assessment\n\n"
        "Before you start earning, we'll test your knowledge with a few practical tasks:\n"
        "• 📝 Text Annotation\n"
        "• 🎵 Audio Recording\n" 
        "• 🖼️ Image Annotation\n"
        "• 🎥 Video Annotation\n\n"
        "This helps us assign you the right tasks for your skill level!\n\n"
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
        "• Translate it accurately to Yoruba\n"
        "• Write your translation as a text message\n"
        "• Focus on accuracy and natural flow\n\n"
    )
        
    await callback.message.answer(instructions_text)
    await asyncio.sleep(2)
    await handle_begin_translation(callback, state)



def select_sample_text(target_lang_code):
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
    #display text for task
    await callback.answer()
    

    sample_text = SAMPLE_TEXTS["english_to_yoruba"]["text"]
    
    translation_text = (
        f"Here is the text to translate from English to Yoruba:\n\n"
        f"---\n"
        f'"{sample_text}"\n'
        f"---\n\n"
        f" Make sure the translation is accurate and natural!\n"
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
    await state.update_data(user_translation=user_translation)
    
    sample_text = SAMPLE_TEXTS["english_to_yoruba"]["text"]
    

    confirmation_text = (
        "✅ Translation Received!\n\n"  
        f"Original (English):\n"
        f'"{sample_text}"\n\n'
        f"Your Yoruba translation:\n"  
        f'"{user_translation}"\n\n'
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )
    
    await message.answer(confirmation_text)
    
    # Simulation of validation
    await simulate_validation(message, state)

async def simulate_validation(message: Message, state: FSMContext):
    """Simulation du processus de validation"""

    await asyncio.sleep(3)
    
    data = await state.get_data()
    user_data = await state.get_data()
    
    #to change later
    validation_result = True  
    
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
            "• You'll receive an image.\n"
            "• You would be requested to give a well detail description of the image\n\n"
            "Ready to begin the image test?"
        )
        
        image_ready_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🖼️ Start Image Test", callback_data="start_image_test")]
            ]
        )
        
        await message.answer(image_instructions_text, reply_markup=image_ready_kb)
        await state.set_state(TestKnowledge.image_task)
        

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
@router.callback_query(TestKnowledge.image_task, F.data == "start_image_test")
async def handle_image_test(callback: CallbackQuery, state: FSMContext):
    """Start image assessment"""
    await callback.answer()
    
    await state.update_data(current_q=0, num_q=1, target_lang="Yoruba")
    await handle_start_image_test(callback.message, state)
    

async def handle_start_image_test(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data.get('current_q')
    target_lang = data.get('target_lang', 'Yoruba')
    quiz = image_data[q_index]
    
    await handle_image_task(message, quiz, target_lang)
    await state.set_state(TestKnowledge.image_submission)
    
    
@router.message(TestKnowledge.image_submission)
async def handle_image_input(message: Message, state: FSMContext):
    data = await state.get_data()
    current_q = data.get('current_q')
    
    selected_q = image_data[current_q]
    await handle_image_task_review(message, state, selected_q)
    await state.set_state(TestKnowledge.image_feedback)
    
@router.callback_query(TestKnowledge.image_submission)
async def handle_image_option_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_q = data.get('current_q')
    selected_q = image_data[current_q]
    await handle_image_task_review(callback, state, selected_q)
    await state.set_state(TestKnowledge.image_feedback)
    
@router.message(TestKnowledge.image_feedback)
async def handle_next_step(message: Message, state: FSMContext):
    data = await state.get_data()
    num_q = data.get('num_q', 1)
    current_q = data.get('current_q')
    
    if num_q < 2:
        await message.answer("🎉 Great!!! Let's move to second image task.")
        num_q += 1
        current_q += 1
        await state.update_data(current_q=current_q, num_q=num_q)
        await handle_start_image_test(message, state)
    else:
        # Video image assessment
        await asyncio.sleep(3)
        
        # Video assessment instructions
        video_instructions_text = (
            "Great!\n"
            "Let's move to Video Annotation task!\n\n"
            "📋 Instructions:\n"
            "• You'll receive a video.\n"
            "• You will be asked to give a well detailed description of the image\n\n"
            "Ready to begin the video test?"
        )
        
        video_ready_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🖼️ Start Video Test", callback_data="start_video_test")]
            ]
        )
        
        await message.answer(video_instructions_text, reply_markup=video_ready_kb)
        await state.set_state(TestKnowledge.video_task)

    


# Video Assessment Handlers
@router.callback_query(TestKnowledge.video_task, F.data == "start_video_test")
async def handle_video_test(callback: CallbackQuery, state: FSMContext):
    """Start video assessment"""
    await callback.answer()
    await state.update_data(current_q=0, num_q=1, target_lang="Yoruba")
    await handle_start_video_test(callback.message, state)

async def handle_start_video_test(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data.get('current_q')
    target_lang = data.get('target_lang', 'Yoruba')
    quiz = video_data[q_index]
    await handle_video_task(message, quiz, target_lang)
    await state.set_state(TestKnowledge.video_submission)

@router.message(TestKnowledge.video_submission)
async def handle_video_input(message: Message, state: FSMContext):
    data = await state.get_data()
    current_q = data.get('current_q')
    selected_q = video_data[current_q]
    await handle_video_task_review(message, state, selected_q)
    await state.set_state(TestKnowledge.video_feedback)

@router.callback_query(TestKnowledge.video_submission)
async def handle_video_option_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_q = data.get('current_q')
    selected_q = video_data[current_q]
    await handle_video_task_review(callback, state, selected_q)
    await state.set_state(TestKnowledge.video_feedback)

@router.message(TestKnowledge.video_feedback)
async def handle_next_video_step(message: Message, state: FSMContext):
    data = await state.get_data()
    num_q = data.get('num_q', 1)
    current_q = data.get('current_q')

    if num_q < 2:
        await message.answer("🎉 Great!!! Let's move to the next video task.")
        num_q += 1
        current_q += 1
        await state.update_data(current_q=current_q, num_q=num_q)
        await handle_start_video_test(message, state)
    else:
        await asyncio.sleep(3)
        success_text = (
                    "🎉 (simulation) Congratulations! Test Passed!\n"  
                    "You're now eligible for real tasks!\n\n" \
                    "Ready to start earning?"
                )
        

            
        await message.answer(success_text)

        # Clear state
        await state.clear()
                
        # Show final completion buttons
        start_tasks_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Start Real Tasks", callback_data="start_real_tasks")],
                [InlineKeyboardButton(text="View Commands", callback_data="view_commands")]
            ]
        )
                
        await message.answer(
            "🎉 All assessments completed!\n\nClick below to access the task portal:",
            reply_markup=start_tasks_kb
        )


@router.callback_query(F.data == "start_real_tasks")
async def handle_start_real_tasks(callback: CallbackQuery, state: FSMContext):
    """Redirection vers les tâches réelles"""
    await callback.answer()
    
    # Import local pour éviter circular imports
    from src.routes.task_routes.tasks import cmd_welcome
    
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
