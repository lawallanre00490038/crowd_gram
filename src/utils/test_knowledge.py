from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from src.constant.test_knowledge_constant import SAMPLE_TEXTS, AVAILABLE_LANGUAGES
import json
from json import JSONDecodeError
from pathlib import Path
import random
import logging
from typing import List

def create_ready_button():
    """Bouton Ready to start"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yes I'm ready!", callback_data="ready_start")]
        ]
    )

def create_language_selection_keyboard():
    """Clavier pour sélection de langue"""
    buttons = [
        [InlineKeyboardButton(text=f"🌍 {lang_name}", callback_data=f"lang_{lang_code}")]
        for lang_name, lang_code in AVAILABLE_LANGUAGES
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_task_ready_keyboard():
    """Bouton pour commencer la tâche de traduction"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ I understand, let's begin!", callback_data="begin_translation")]
        ]
    )

def load_json_file(file: Path) -> List:
    """
    Loads a json file into list.

    Args:
        file (Path): path to the json file.

    Returns:
        List: A List of the information in the json file.
    """
    try:
        with open(Path(file), 'r', encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, JSONDecodeError) as e:
        logging.error(f"Error loading data: {e}")
        return []