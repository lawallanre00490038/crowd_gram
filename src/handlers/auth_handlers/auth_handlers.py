from typing import Dict, Optional
from src.handlers.onboarding_handlers.category_onboarding_handler import _ask_next_category_question
from src.handlers.onboarding_handlers.onboarding import get_company_id, get_full_user_data, get_saved_languages, init_onboarding_section
from src.keyboards.onboarding_keyboard import list_category_kb
from src.models.auth_models import LoginResponseDict, UserData, UserRegisterRequest, VerifyPasswordInput
from src.models.onboarding_models import SignUpResponseModel
from src.responses.onboarding_response import LANGUAGE_MSG, PERSONAL_MSG
from src.services.language_selection import DialectSelectionService, handle_language_keyboard_callback, init_language_selection
from src.services.location_service import LocationService
from src.services.server.auth import register_user, verify_otp
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.keyboards.reply import task_type_kb 

from src.services.server.getters_api import get_signup_list
from src.services.task_type_service import TaskTypeService
from src.states.authentication import Authentication
from src.states.onboarding import Onboarding

async def user_signup(user_data) -> LoginResponseDict:
    company = user_data.get('company')
    company_id = await get_company_id(company) 

    if not company_id:
        raise ValueError("Company not found")
    
    auth_phone = user_data.get("auth_phone", "")
    user_info = UserRegisterRequest(country_code=auth_phone[:3], 
                        phone_number=auth_phone[3:],
                        email=user_data.get("email", None),
                        os_type="telegram",
                        company_id=company_id,
                        password=user_data.get("password"),name= user_data.get("auth_name"))
    
    user_response = await register_user(user_info)
    
    return user_response

async def user_verify_otp(user_data, inputed_otp) -> LoginResponseDict:
    auth_phone = user_data.get("auth_phone", "")

    user_info = VerifyPasswordInput(password=user_data.get("password"),
                               otp = inputed_otp, 
                               phone_number=auth_phone[3:],
                        email=user_data.get("email", None))
    
    user_response = await verify_otp(user_info)
    
    return user_response

async def route_user(message: Message, state: FSMContext, full_user_data: Optional[UserData] = None, user_data: Optional[Dict] = None,):
    if user_data == None:
        user_data = await state.get_data()


    if full_user_data == None: 
        full_user_data = await get_full_user_data(user_data=user_data)

    signuplist = user_data.get("signuplist", None)
    if signuplist == None: 
        signuplist = await get_signup_list(full_user_data.company_id)    
        await state.update_data(signuplist=signuplist.model_dump())
    
    loc_service = LocationService()
    if not full_user_data.is_onboarding:
        await message.answer("Complete your Onboarding to continue")

        if user_data.get("location", None) == None: 
            await loc_service.initialize_country_selection(message = message, state=state)
            await state.set_state(Onboarding.location)
        elif user_data.get("state_residence", None) == None: 
            await loc_service._send_state_prompt(message = message, state=state, country = user_data.get("location"))
        elif user_data.get("gender", None) == None: 
            await init_onboarding_section(
                message=message,
                state=state,
                category="gender",
                section=Onboarding.gender,
                answer="gender"
            )
        elif user_data.get("age", None) == None: 
            await init_onboarding_section(
                message=message,
                state=state,
                category="age",
                section=Onboarding.age_range,
                answer="age"
            )
        elif user_data.get("education", None) == None: 
            await init_onboarding_section(
                message=message,
                state=state,
                category="education",
                section=Onboarding.education,
                answer="education"
            )
        elif user_data.get("industry", None) == None: 
            await init_onboarding_section(
                message=message,
                state=state,
                category="industry",
                section=Onboarding.industry,
                answer="industry"
            )
        elif user_data.get("languages", None) == None: 
            await init_language_selection(message=message, state=state)
        elif len((await get_saved_languages(user_data=user_data)).data) < 2:
            _, dynamic_kb = await handle_language_keyboard_callback("page:0", state)
            await message.answer(text = LANGUAGE_MSG["selection_prompt"], reply_markup=dynamic_kb)
            state.set_state(Onboarding.languages)
        elif user_data.get("selected_dialects", None) == None: 
            await DialectSelectionService.start_dialect_selection(message, state)
        elif user_data.get("selected_data_types", None) == None: 
            await TaskTypeService.init_data_type_selection_done(message, state)
        else: 
            await _ask_next_category_question(message=message,state=state)
        
        return