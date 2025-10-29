from typing import Dict, Optional
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.handlers.onboarding_handlers.category_onboarding_handler import init_category_section
from src.handlers.onboarding_handlers.onboarding import get_full_user_data, get_saved_categories
from src.keyboards.dynamic import create_data_type_keyboard_with_done
from src.keyboards.reply import writing_ability_kb, phone_quality_kb
from src.keyboards.onboarding_keyboard import task_type_kb
from src.services.server.getters_api import get_category_list
from src.states.onboarding import Onboarding


class TaskTypeService():
    @staticmethod
    async def init_data_type_selection_done(message: Message, state: FSMContext):
        user_data = await get_full_user_data(state=state)
        categories = await get_category_list(company_id=user_data.company_id)
        logger.trace(categories)
        await state.update_data(categories=[i.model_dump() for i in categories])
        dynamic_kb = await task_type_kb(categories=categories)
        if dynamic_kb.inline_keyboard != []:
            await message.answer("📌 What kind of data do you want to give?", reply_markup=dynamic_kb)
            await state.set_state(Onboarding.task_type)
        else:
            await message.answer("No Category Available at the moment")

    @staticmethod
    async def handle_data_type_selection_done(message: Message, state: FSMContext):
        pass

    @staticmethod
    async def handle_data_type_selection(message: Message, state: FSMContext, data: str):
        item, index = data.split(":")

        user_data = await state.get_data()
        selected_data_types = user_data.get("selected_data_types", [])

        if item == "select":
            index = int(index)

            categories = await get_saved_categories(user_data=user_data)
            logger.trace(categories)
            if index in selected_data_types:
                selected_data_types.remove(index)
                await message.answer(f"❌ Removed: {categories[index].name}")
            else:
                selected_data_types.append(index)
                await message.answer(f"✅ Added: {categories[index].name}")

            await state.update_data(selected_data_types=selected_data_types)

            num_selected = len(selected_data_types)
            dynamic_kb = await task_type_kb(categories=categories, show_done=True)
            if num_selected == 0:
                await message.answer("📌 What kind of data do you want to give?\nSelect one or both.", reply_markup=dynamic_kb)
            elif num_selected == 1:
                await message.answer("One data type selected.\nSelect another or press '✅ Done' to continue.", reply_markup=dynamic_kb)
            elif num_selected == 2:
                await message.answer((f"✅ Both selected: {', '.join(categories[i].name for i in selected_data_types)}! \n\n"
                                      "Deselect or press '✅ Done' to continue."), reply_markup=dynamic_kb)

        elif item == "done":
            selected_data_types = user_data.get("selected_data_types", [])
            await message.answer("✅ Data type selection confirmed!")
            await init_category_section(message, state)
