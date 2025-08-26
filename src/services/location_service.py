from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.keyboards.dynamic import (create_countries_keyboard_reply_api, create_states_keyboard_api)
from src.services.server.getters_api import get_countries_from_api, get_states_from_api
from src.responses.onboarding_response import (LOCATION_MSG,PERSONAL_MSG)
from src.states.onboarding import Onboarding
from src.keyboards.reply import gender_kb

class LocationService:

    @staticmethod
    async def initialize_country_selection(message: Message, state: FSMContext):
        """Initialize the country selection process"""
        await state.update_data(country_selection_started=True, country_page=0)
        await message.answer(
            LOCATION_MSG["country_prompt"],
            reply_markup=await create_countries_keyboard_reply_api()
        )
     
    @staticmethod
    async def handle_country_selection(message: Message, state: FSMContext):
        """
        Handle country selection
        Returns: True if valid country selected, False otherwise
        """
        countries_from_api = await get_countries_from_api()
        
        if message.text not in countries_from_api:
            return False
            
        selected_country = message.text.strip()
        await state.update_data(location=selected_country)
        await message.answer(f"✅ Nationality selected: {selected_country}")
        
        await message.answer(
            LOCATION_MSG["state_prompt"].format(country=selected_country), 
            reply_markup=await create_states_keyboard_api(selected_country)
        )
        await state.set_state(Onboarding.state_residence)
        return True
    
    @staticmethod
    async def handle_pagination_next(message: Message, state: FSMContext):
        user_data = await state.get_data()
        current_page = user_data.get("country_page", 0)
        new_page = current_page + 1
        await state.update_data(country_page=new_page)
        await message.answer(
            "...",reply_markup= await create_countries_keyboard_reply_api(page=new_page)
         )
      
    
    @staticmethod
    async def handle_location_previous(message: Message, state: FSMContext):
        user_data = await state.get_data()
        current_page = user_data.get("country_page", 0)
        new_page = max(0, current_page - 1)
        await state.update_data(country_page=new_page)
        await message.answer(
            "...",
            reply_markup= await create_countries_keyboard_reply_api(page=new_page)
        )
     
    @staticmethod
    async def handle_state_selection(message: Message, state: FSMContext):
        """
        Handle state/province selection
        Returns: True if valid state or no states available, False if invalid
        """
        
        user_data = await state.get_data()
        selected_country = user_data.get("location", "")
        states_from_api = await get_states_from_api(selected_country)
    
        if message.text in states_from_api or not states_from_api:
            state_residence = message.text.strip() if states_from_api else selected_country
            await state.update_data(state_residence=state_residence)
            await message.answer(f"State of residence: {state_residence}")
            
            # Move to next step (gender)
            await message.answer(PERSONAL_MSG["gender"], reply_markup=gender_kb)
            await state.set_state(Onboarding.gender)
            return True
        
        # Invalid state selected
        return False
    
    


