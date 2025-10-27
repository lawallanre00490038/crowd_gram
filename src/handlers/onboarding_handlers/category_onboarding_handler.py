from typing import Dict, Optional
from loguru import logger
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.handlers.onboarding_handlers.complete_onboarding import complete_profile
from src.handlers.onboarding_handlers.onboarding import get_saved_categories
from src.keyboards.onboarding_keyboard import build_multi_select_keyboard
from src.states.onboarding import Onboarding


async def init_category_section(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await _ask_next_category_question(message=message, state=state, user_data=user_data)
    await state.set_state(Onboarding.category_question)


async def _ask_next_category_question(message: Message, state: FSMContext, user_data: Optional[Dict] = None):
    if user_data == None:
        user_data = await state.get_data()
    save_categories = await get_saved_categories(user_data=user_data)
    current_category = int(user_data.get("current_category", 0))
    next_question = int(user_data.get("next_question", 0))

    if current_category >= len(save_categories):
        logger.trace(await complete_profile(user_data=user_data))
        await message.answer("✅ You’ve completed all the onboarding questions!")
        return

    category = save_categories[current_category]
    questions = category.categoryQuestions

    if not questions or next_question >= len(questions):
        user_data["current_category"] = current_category + 1
        user_data["next_question"] = 0
        await state.update_data(**user_data)
        return await _ask_next_category_question(message=message, user_data=user_data, state=state)

    question_data = questions[next_question]
    selection_type = question_data.selection
    question_text = question_data.question
    options = question_data.options

    if selection_type == "multiple":
        user_data["multi_selected"] = []
        await state.update_data(**user_data)
        await message.answer(
            question_text,
            reply_markup=build_multi_select_keyboard(options, [])
        )

    elif selection_type == "single":
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=opt, callback_data=opt)] for opt in options
            ]
        )
        await message.answer(question_text, reply_markup=keyboard)

    elif selection_type == "text":
        # Use this flag to know we’re waiting for text
        user_data["awaiting_text"] = True
        await state.update_data(**user_data)
        await message.answer(question_text)


async def handle_multi_selection(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    save_categories = await get_saved_categories(user_data=user_data)
    current_category = int(user_data.get("current_category", 0))
    next_question_index = int(user_data.get("next_question", 0))

    category = save_categories[current_category]
    question_data = category.categoryQuestions[next_question_index]
    options = question_data.options

    selected = user_data.get("multi_selected", [])

    if callback.data.startswith("select|"):
        _, option = callback.data.split("|", 1)
        if option in selected:
            selected.remove(option)
        else:
            selected.append(option)

        user_data["multi_selected"] = selected
        await state.update_data(**user_data)

        await callback.message.edit_reply_markup(
            reply_markup=build_multi_select_keyboard(options, selected)
        )
        await callback.answer()
        return

    if callback.data == "confirm_selection":
        if not selected:
            await callback.answer("Please select at least one option.", show_alert=True)
            return

        logger.trace(question_data)
        answer_record = {
            "category_id": question_data.category_id,
            "question_id": question_data.id,
            "question": question_data.question,
            "selection": "multiple",
            "answer": selected
        }

        answers = user_data.get("answers", [])
        answers.append(answer_record)

        user_data["answers"] = answers
        user_data["next_question"] = next_question_index + 1
        user_data["multi_selected"] = []

        await state.update_data(**user_data)

        await callback.message.delete()
        await _ask_next_category_question(message=callback.message, user_data=user_data, state=state)


async def handle_single_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    selected_option = callback.data
    user_data = await state.get_data()

    save_categories = await get_saved_categories(user_data=user_data)
    current_category = int(user_data.get("current_category", 0))
    next_question_index = int(user_data.get("next_question", 0))

    category = save_categories[current_category]
    question_data = category.categoryQuestions[next_question_index]

    answer_record = {
        "category_id": question_data.category_id,
        "ques_id": question_data.id,
        "question": question_data.question,
        "selection": "single",
        "answer": selected_option
    }

    answers = user_data.get("answers", [])
    answers.append(answer_record)

    # Update indices and state
    user_data["answers"] = answers
    user_data["next_question"] = next_question_index + 1
    await state.update_data(**user_data)

    await callback.message.delete()
    await _ask_next_category_question(message=callback.message, user_data=user_data, state=state)


async def handle_text_input(message: Message, state: FSMContext):
    user_data = await state.get_data()

    # Only handle if we're expecting text input
    if not user_data.get("awaiting_text"):
        return

    save_categories = await get_saved_categories(user_data=user_data)
    current_category = int(user_data.get("current_category", 0))
    next_question_index = int(user_data.get("next_question", 0))

    category = save_categories[current_category]
    question_data = category.categoryQuestions[next_question_index]

    answer_record = {
        "category_id": question_data.category_id,
        "question_id": question_data.id,
        "question": question_data.question,
        "selection": "text",
        "answer": message.text
    }

    answers = user_data.get("answers", [])
    answers.append(answer_record)

    # Update state
    user_data["answers"] = answers
    user_data["next_question"] = next_question_index + 1
    user_data["awaiting_text"] = False
    await state.update_data(**user_data)

    await _ask_next_category_question(messge=message, user_data=user_data, state=state)
