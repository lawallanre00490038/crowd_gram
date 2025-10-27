from typing import Dict, List, Optional
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from src.handlers.onboarding_handlers.onboarding import get_languages, get_saved_languages, get_selected_languages, update_selected_languages
from src.keyboards.onboarding_keyboard import load_inline_keyboard, load_languages_kb
from src.keyboards.reply import task_type_kb
from src.models.onboarding_models import BaseLanguage, Language
from src.services.server.getters_api import get_languages_from_api
from src.responses.onboarding_response import LANGUAGE_MSG, DIALECT_MSG
from src.services.task_type_service import TaskTypeService
from src.states.onboarding import Onboarding


async def init_language_selection(message: Message, state: FSMContext):
    languages = await get_languages(state)
    dynamic_kb = load_languages_kb(languages, 0)
    await message.answer(LANGUAGE_MSG["selection_prompt"], reply_markup=dynamic_kb)
    await state.set_state(Onboarding.languages)


async def handle_language_keyboard_callback(data: str, state: FSMContext):
    logger.trace(data)
    action, *params = data.split(":")
    user_data = await state.get_data()

    languages = await get_saved_languages(user_data=user_data)
    selected_languages = await get_selected_languages(user_data=user_data)
    show_done = len(selected_languages) > 0

    logger.trace(show_done)

    if action == "page":
        page_num = int(params[0])
        dynamic_kb = load_languages_kb(
            languages, page_num, show_done=show_done)
        return "", dynamic_kb

    if action == "select":
        lang_code = params[0]
        page_num = int(params[1])
        message, status = await handle_language_selection(state, lang_code, selected_languages)
        dynamic_kb = None if status else load_languages_kb(
            languages, page_num, show_done=show_done)
        return message, dynamic_kb

    if action == "✅ Done":
        return "", None

    # Optional: handle unexpected actions
    return None, None


async def handle_language_selection(state: FSMContext, lang_index, selected_languages: List,
                                    user_data: Optional[Dict] = None):
    if user_data == None:
        user_data = await state.get_data()

    language = await get_full_lang_detail(user_data, lang_index)

    if language in selected_languages:
        selected_languages.remove(language)
        await update_selected_languages(state, selected_languages)
        return f"❌ Removed: {language.name}", True
    else:
        if len(selected_languages) >= 2:
            return LANGUAGE_MSG["max_reached"], False
        else:
            selected_languages.append(language)
            await update_selected_languages(state, selected_languages)
            return f"Added: {language.name}", True


async def get_full_lang_detail(user_data: Dict, lang_index):
    saved_languages = await get_saved_languages(user_data=user_data)
    return saved_languages.data[int(lang_index)]


class DialectSelectionService:

    @staticmethod
    async def start_dialect_selection(message: Message, state: FSMContext):
        user_data = await state.get_data()
        selected_languages = await get_selected_languages(user_data=user_data)
        current_index = user_data.get("dialect_selection_index", 0)

        if current_index < len(selected_languages):
            current_language = selected_languages[current_index]
            await DialectSelectionService._ask_dialect_for_language(message, state, current_language)
        else:
            await DialectSelectionService._finish_dialect_selection(message, state)

        await state.set_state(Onboarding.dialect_selection)

    @staticmethod
    async def _ask_dialect_for_language(message: Message, state: FSMContext, language: Language):
        await message.answer(
            DIALECT_MSG["selection_prompt"].format(language=language.name),
            reply_markup=load_inline_keyboard(items=language.dialects)
        )
        await state.set_state(Onboarding.dialect_selection)

    @staticmethod
    async def _finish_dialect_selection(message: Message, state: FSMContext):
        user_data = await state.get_data()
        selected_dialects = user_data.get("selected_dialects", {})
        dialect_summary = [f"{lang}: {dialect}" for lang,
                           dialect in selected_dialects.items()]

        await state.update_data(dialects=selected_dialects)
        await message.answer(DIALECT_MSG["summary"].format(dialects="\n".join(dialect_summary)))

        await TaskTypeService.init_data_type_selection_done(message=message, state=state)
        return False

    @staticmethod
    async def handle_dialect_selection(data: str, message: Message, state: FSMContext) -> bool:
        """handle dialect selecton
        Returns: True if continue, False if done
        """
        action, *params = data.split(":")
        user_data = await state.get_data()
        selected_languages = await get_selected_languages(user_data=user_data)
        current_index = user_data.get("dialect_selection_index", 0)
        selected_dialects = user_data.get("selected_dialects", {})

        if current_index >= len(selected_languages):
            await DialectSelectionService._finish_dialect_selection(message, state)
            return False

        current_language = selected_languages[current_index]

        if user_data.get("awaiting_manual_dialect"):
            return await DialectSelectionService._handle_manual_dialect_entry(
                message, state, selected_dialects
            )

        if action == "select":
            lang_code = int(params[0])
            logger.trace(lang_code)
            # page_num = int(params[1])

            dialect = current_language.dialects[lang_code]
            # valid dialect selected
            selected_dialects[current_language.name] = dialect
            await state.update_data(selected_dialects=selected_dialects)
            await message.answer(DIALECT_MSG["selected"].format(
                language=current_language.name,
                dialect=dialect
            ))

            # go to next step
            await DialectSelectionService._proceed_to_next_language(message, state)
            return True

    @staticmethod
    async def _handle_manual_dialect_entry(message: Message, state: FSMContext, selected_dialects: dict) -> bool:
        user_data = await state.get_data()
        dialect = message.text.strip()
        language_for_manual = user_data.get("current_dialect_language")

        selected_dialects[language_for_manual] = dialect

        await state.update_data(
            selected_dialects=selected_dialects,
            awaiting_manual_dialect=False,
            current_dialect_language=None
        )

        await message.answer(DIALECT_MSG["selected"].format(
            language=language_for_manual,
            dialect=dialect
        ))

        await DialectSelectionService._proceed_to_next_language(message, state)
        return True

    @staticmethod
    async def _proceed_to_next_language(message: Message, state: FSMContext):
        user_data = await state.get_data()
        next_index = user_data.get("dialect_selection_index", 0) + 1
        await state.update_data(dialect_selection_index=next_index)
        await DialectSelectionService.start_dialect_selection(message, state)
