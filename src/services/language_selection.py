from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.keyboards.dynamic import create_language_keyboard_api, create_language_keyboard_with_done, create_dialect_keyboard_api
from src.keyboards.reply import task_type_kb 
from src.services.server.getters_api import get_language_names, get_dialects_from_api
from src.responses.onboarding_response import LANGUAGE_MSG, DIALECT_MSG
from src.states.onboarding import Onboarding

class LanguageSelectionService:
    
    @staticmethod
    async def handle_language_selection(message: Message, state: FSMContext) -> bool:
        """
       handle langugage selection
        Returns: True if continue, False if done
        """
        try:
            all_languages = await get_language_names()
        except Exception:
            all_languages = ["Other"]

        if message.text not in all_languages:
            dynamic_kb = await create_language_keyboard_api()
            await message.answer(LANGUAGE_MSG["selection_prompt"], reply_markup=dynamic_kb)
            return True

        user_data = await state.get_data()
        selected_languages = user_data.get("selected_languages", [])

        if message.text in selected_languages:
            selected_languages.remove(message.text)
            await message.answer(f"❌ Removed: {message.text}")
        else:
            if len(selected_languages) >= 2:
                await message.answer(LANGUAGE_MSG["max_reached"])
                return True
            selected_languages.append(message.text)
            await message.answer(f"Added: {message.text}")

        await state.update_data(selected_languages=selected_languages)
        await LanguageSelectionService._update_language_keyboard(message, state, selected_languages)
        
        # Check if we should proceed to dialects
        if len(selected_languages) == 2:
            await LanguageSelectionService._proceed_to_dialects(message, state, selected_languages)
            return False
        
        return True

    @staticmethod
    async def handle_language_selection_done(message: Message, state: FSMContext) -> bool:
        user_data = await state.get_data()
        selected_languages = user_data.get("selected_languages", [])
        
        if len(selected_languages) < 1:
            await message.answer(LANGUAGE_MSG["min_selection"])
            return False
            
        await message.answer(LANGUAGE_MSG["selection_confirmed"])
        await LanguageSelectionService._proceed_to_dialects(message, state, selected_languages)
        return True

    @staticmethod
    async def _proceed_to_dialects(message: Message, state: FSMContext, selected_languages: list):
        await state.update_data(
            languages=", ".join(selected_languages),
            dialect_selection_index=0,
            selected_dialects={}
        )
        await message.answer(f"✅ Two languages selected: {', '.join(selected_languages)}. Proceeding to the next step!")
        await DialectSelectionService.start_dialect_selection(message, state)

    @staticmethod
    async def _update_language_keyboard(message: Message, state: FSMContext, selected_languages: list):
        """Met à jour le keyboard selon le nombre de langues sélectionnées"""
        num_selected = len(selected_languages)
        
        if num_selected == 0:
            dynamic_kb = await create_language_keyboard_api()
            await message.answer(LANGUAGE_MSG["selection_prompt"], reply_markup=dynamic_kb)
        elif num_selected == 1:
            keyboard_with_done = await create_language_keyboard_with_done()
            await message.answer(LANGUAGE_MSG["one_selected"], reply_markup=keyboard_with_done)



class DialectSelectionService:
    
    @staticmethod
    async def start_dialect_selection(message: Message, state: FSMContext):
        user_data = await state.get_data()
        selected_languages = user_data.get("selected_languages", [])
        current_index = user_data.get("dialect_selection_index", 0)
        
        if current_index < len(selected_languages):
            current_language = selected_languages[current_index]
            await DialectSelectionService._ask_dialect_for_language(message, state, current_language)
        else:
            await DialectSelectionService._finish_dialect_selection(message, state)

    @staticmethod
    async def _ask_dialect_for_language(message: Message, state: FSMContext, language: str):
        await message.answer(
            DIALECT_MSG["selection_prompt"].format(language=language),
            reply_markup= await create_dialect_keyboard_api(language)
        )
        await state.set_state(Onboarding.dialect_selection)

    @staticmethod
    async def _finish_dialect_selection(message: Message, state: FSMContext):
        user_data = await state.get_data()
        selected_dialects = user_data.get("selected_dialects", {})
        dialect_summary = [f"{lang}: {dialect}" for lang, dialect in selected_dialects.items()]
        
        await state.update_data(dialects=selected_dialects)
        await message.answer(DIALECT_MSG["summary"].format(dialects="\n".join(dialect_summary)))

        await message.answer("📌 What kind of data do you want to give?", reply_markup=task_type_kb)
        await state.set_state(Onboarding.task_type)
    
        return False
      

    @staticmethod
    async def handle_dialect_selection(message: Message, state: FSMContext) -> bool:
        """handle dialect selecton
        Returns: True if continue, False if done
        """
        user_data = await state.get_data()
        selected_languages = user_data.get("selected_languages", [])
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

        if message.text == "Not listed here":
            await message.answer(DIALECT_MSG["manual_entry"])
            await state.update_data(
                awaiting_manual_dialect=True, 
                current_dialect_language=current_language
            )
            return True
        
        #validation
        valid_dialects = await get_dialects_from_api(current_language)
        
        if message.text not in valid_dialects:
            await message.answer(
                DIALECT_MSG["invalid_selection"].format(language=current_language),
                reply_markup= await create_dialect_keyboard_api(current_language)
            )
            return True

        # valid dialect selected
        selected_dialects[current_language] = message.text.strip()
        await state.update_data(selected_dialects=selected_dialects)
        await message.answer(DIALECT_MSG["selected"].format(
            language=current_language, 
            dialect=message.text
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
