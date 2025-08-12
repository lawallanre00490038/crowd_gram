from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from src.constant.test_knowledge_constant import SAMPLE_TEXTS, AVAILABLE_LANGUAGES
import random

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

def get_next_unique_question(used_questions: list, total_questions: int) -> int:
    """Get a random question index that hasn't been used yet"""
    available_questions = [i for i in range(total_questions) if i not in used_questions]
    if not available_questions:
        raise ValueError("No more unique questions available")
    return random.choice(available_questions)