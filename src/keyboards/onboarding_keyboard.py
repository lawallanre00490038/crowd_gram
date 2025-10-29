from typing import List
from loguru import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.models.onboarding_models import Category, LanguageResponseModel, SignUpResponseModel
from src.services.server.getters_api import get_category_list, get_languages_from_api
from src.utils.general_utils import reshape_list

# Simulate 10,000 items
ITEMS = [f"Item {i}" for i in range(1, 10001)]
ITEMS_PER_PAGE = 12


def list_category_kb(signuplist: SignUpResponseModel, category: str):

    keyboard = []
    for variable in signuplist.data.result:
        if variable.id == category:
            for field_data in variable.field_data:
                keyboard.append(InlineKeyboardButton(
                    text=field_data.name, callback_data=f"{field_data.field_id}:{field_data.name}"))

    return InlineKeyboardMarkup(
        inline_keyboard=reshape_list(keyboard, 2)
    )


def age_kb(signuplist: SignUpResponseModel):

    keyboard = []
    for variable in signuplist.data.result:
        if variable.id == "age_range":
            for field_data in variable.field_data:
                keyboard.append(InlineKeyboardButton(
                    text=field_data.name, callback_data=f"{field_data.field_id}:{field_data.name}"))

    return InlineKeyboardMarkup(
        inline_keyboard=reshape_list(keyboard, 2)
    )


def load_languages_kb(languages: LanguageResponseModel, page: int = 0, show_done=False) -> InlineKeyboardMarkup:
    return load_inline_keyboard([item.name for item in languages.data], page, show_done=show_done)


def load_inline_keyboard(items: List[str], page: int = 0, show_done=False) -> InlineKeyboardMarkup:

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    markup = []

    logger.trace(start, end, ITEMS_PER_PAGE, len(items))

    for index, item in enumerate(items[start:end]):
        markup.append(InlineKeyboardButton(
            text=item, callback_data=f"select:{index}:{page}"))

    markup = reshape_list(markup, 3)

    nav_buttons = []

    if show_done:
        nav_buttons.append(InlineKeyboardButton(
            text="✅ Done", callback_data=f"✅ Done"))

    if len(items) > ITEMS_PER_PAGE:

        # Add pagination buttons
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️ Prev", callback_data=f"page:{page - 1}"))

        if end < len(ITEMS):
            nav_buttons.append(InlineKeyboardButton(
                text="Next ➡️", callback_data=f"page:{page + 1}"))

    if nav_buttons:
        markup.append(nav_buttons)

    return InlineKeyboardMarkup(
        inline_keyboard=markup)


async def task_type_kb(categories: List[Category], show_done=False):
    markup = []

    for index, cat in enumerate(categories):
        markup.append([InlineKeyboardButton(
            text=cat.name, callback_data=f"select:{index}")])

    if show_done:
        markup.append([InlineKeyboardButton(
            text="✅ Done", callback_data=f"done:")])

    return InlineKeyboardMarkup(inline_keyboard=markup)


def build_multi_select_keyboard(options: list, selected: list):
    keyboard = []
    for option in options:
        is_selected = "✅ " if option in selected else ""
        keyboard.append([
            InlineKeyboardButton(
                text=f"{is_selected}{option}",
                callback_data=f"select|{option}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(text="✅ Done", callback_data="confirm_selection")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
