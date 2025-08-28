from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from src.states.test_knowledge import TestKnowledge
from src.utils.test_knowledge import create_ready_button, load_json_file, extract_option
from src.handlers.task_handlers.image_handlers.image_task_output_handler import handle_image_task
import random
import asyncio
from pathlib import Path


router = Router()


# Load image quiz data
quiz_data = load_json_file(Path("src/data/test_knowledge_quiz.json"))

selected_quizzes = random.sample(quiz_data, 6)

def select_sample_text(target_lang_code):
    sample_map = {
        "français": "english_to_french",
        "yoruba": "english_to_yoruba", 
        "hausa": "english_to_hausa",
        "swahili": "english_to_swahili",
        "igbo": "english_to_igbo",
        "pidgin": "english_to_pidgin",       
    }

    
    return sample_map.get(target_lang_code, "english_to_default")



@router.message(F.text == "/start_test_knowledge")
async def start_knowledge_test(message: Message, state: FSMContext):
    await handle_start_knowledge_assessment(message, state)
    
async def handle_start_knowledge_assessment(message: Message, state: FSMContext):
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
    await state.update_data(
        num_q = 1,
        q_index = 0
    )
    
    await state.set_state(TestKnowledge.ready_to_start)
    

    
@router.callback_query(TestKnowledge.ready_to_start, F.data == "ready_start")
async def handle_task_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = state.get_data()
    q_index = data.get('q_index')
    num_q = data.get('num_q')
    
    if num_q <= len(selected_quizzes):
    
        task = selected_quizzes[q_index]
        
        if task['category_type'] == 'text':
            await handle_begin_translation(callback, state)
        elif task['category_type'] == 'image':
            await handle_image_task(callback, task)
        elif task['category_type'] == 'video':
            pass
        
        await state.update_data(
            num_q = 1,
            q_index = 0
        )
    else:
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

async def handle_begin_translation(message: Message, state: FSMContext):
    #display text for task
    data = await state.get_data()
    q_index = data.get('q_index')
    

    sample_text = selected_quizzes[q_index]["text"]
    
    translation_text = (
        f"Here is the text to translate from English to Yoruba:\n\n"
        f"---\n"
        f'"{sample_text}"\n'
        f"---\n\n"
        f" Make sure the translation is accurate and natural!\n"
        f"Type your translation below ⬇️"
        )
    
    await message.answer(translation_text)
    await state.set_state(TestKnowledge.translation_task)

@router.message(TestKnowledge.translation_task)
async def handle_translation_submission(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data.get('q_index')
    
    if not message.text:
        await message.answer(" ❌ Please send your translation as text.")
        return
        
    user_translation = message.text.strip()
    await state.update_data(user_translation=user_translation)
    
    sample_text = selected_quizzes[q_index]["text"]
    

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
        
    