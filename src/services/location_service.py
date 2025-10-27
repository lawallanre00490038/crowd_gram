from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.handlers.onboarding_handlers.onboarding import init_onboarding_section
from src.keyboards.dynamic import (
    create_countries_keyboard_reply_api, create_region_keyboard_api, create_states_keyboard_api)
from src.services.server.getters_api import get_countries_from_api, get_region_from_api, get_states_from_api
from src.responses.onboarding_response import (LOCATION_MSG, PERSONAL_MSG)
from src.states.onboarding import Onboarding


class LocationService:
    @staticmethod
    async def initialize_country_selection(message: Message, state: FSMContext):
        """Start country selection with a keyboard prompt."""
        await state.update_data(country_selection_started=True, country_page=0)
        keyboard = await create_countries_keyboard_reply_api()
        await message.answer(
            LOCATION_MSG["country_prompt"],
            reply_markup=keyboard
        )

    @staticmethod
    async def handle_country_selection(message: Message, state: FSMContext):
        """
        Process selected country.
        Returns: True if valid country selected, False otherwise.
        """
        selected_country = message.text.strip()
        countries = await get_countries_from_api()

        logger.trace(selected_country)
        for country in countries:
            if selected_country == country.country:
                logger.trace("Here")
                await state.update_data(location=country.country)
                await state.update_data(location_id=country.country_id)

                await message.answer(f"✅ Nationality selected: {selected_country}")
                await LocationService._send_state_prompt(message, state, selected_country)
                return True

        return False

    @staticmethod
    async def _send_region_prompt(message: Message, state: FSMContext, country_id: str, select_state: str):
        """Prompt user to select a state after country selection."""
        user_data = await state.get_data()

        country_id = user_data.get("location_id")
        select_state_id = user_data.get("state_id")
        state_residence = user_data.get("state_residence")

        # built this in util
        regions = await get_region_from_api(country_code=country_id, state_code=select_state_id)

        if len(regions) > 0:
            keyboard = await create_region_keyboard_api(regions=regions)
            await message.answer(
                LOCATION_MSG["lga_prompt"].format(state=state_residence),
                reply_markup=keyboard
            )
            await state.set_state(Onboarding.local_goverment)
        else:
            # If No region skip
            await init_onboarding_section(
                message=message,
                state=state,
                category="gender",
                section=Onboarding.gender,
                answer="gender"
            )

    @staticmethod
    async def _send_state_prompt(message: Message, state: FSMContext, country: str):
        """Prompt user to select a state after country selection."""
        states = await get_states_from_api(country)  # built this in util

        if len(states) > 0:
            keyboard = await create_states_keyboard_api(states)
            await message.answer(
                LOCATION_MSG["state_prompt"].format(country=country),
                reply_markup=keyboard
            )
            await state.set_state(Onboarding.state_residence)
        else:
            # If  no state skip
            await init_onboarding_section(
                message=message,
                state=state,
                category="gender",
                section=Onboarding.gender,
                answer="gender"
            )

    @staticmethod
    async def handle_pagination_next(message: Message, state: FSMContext):
        user_data = await state.get_data()
        current_page = user_data.get("country_page", 0)
        new_page = current_page + 1
        await state.update_data(country_page=new_page)
        await message.answer(
            "...", reply_markup=await create_countries_keyboard_reply_api(page=new_page)
        )

    @staticmethod
    async def handle_location_previous(message: Message, state: FSMContext):
        user_data = await state.get_data()
        current_page = user_data.get("country_page", 0)
        new_page = max(0, current_page - 1)
        await state.update_data(country_page=new_page)
        await message.answer(
            "...",
            reply_markup=await create_countries_keyboard_reply_api(page=new_page)
        )

    @staticmethod
    async def handle_state_selection(message: Message, state: FSMContext):
        """
        Handle state/province selection
        Returns: True if valid state or no states available, False if invalid
        """

        user_data = await state.get_data()
        selected_country = user_data.get("location", "")
        country_id = user_data.get("location_id", "")
        states_from_api = await get_states_from_api(selected_country)

        for state_from_api in states_from_api:
            if message.text == state_from_api.state:
                state_residence = message.text.strip() if states_from_api else selected_country
                await state.update_data(state_residence=state_residence)
                await state.update_data(state_id=state_from_api.state_id)
                await message.answer(f"State of residence: {state_residence}")
                await LocationService._send_region_prompt(message=message, state=state,
                                                          country_id=country_id, select_state=state_from_api.state_id)
                return True

        # Invalid state selected
        return False

    @staticmethod
    async def handle_region_selection(message: Message, state: FSMContext):
        """
        Handle state/province selection
        Returns: True if valid state or no states available, False if invalid
        """

        user_data = await state.get_data()
        country_id = user_data.get("location_id", "")
        state_id = user_data.get("state_id", "")
        regions_from_api = await get_region_from_api(country_code=country_id,
                                                     state_code=state_id)

        for region in regions_from_api:
            if message.text == region:
                region_residence = message.text.strip() if regions_from_api else region_residence
                await state.update_data(region_residence=region_residence)
                await state.update_data(region_id=region)
                await message.answer(f"LGA: {region_residence}")

                return True

        # Invalid state selected
        return False
