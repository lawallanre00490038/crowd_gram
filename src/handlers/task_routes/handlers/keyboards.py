from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_selector_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Submit Quote", callback_data="text:quote")],
        [InlineKeyboardButton(text="📸 Upload Street Photo", callback_data="img:street")],
    ])
