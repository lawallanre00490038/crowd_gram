from typing import List
from aiogram import Bot
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.handlers.auth_handlers.auth_handlers import route_user
from src.handlers.onboarding_handlers.category_onboarding_handler import handle_multi_selection, handle_single_selection, handle_text_input
from src.keyboards.onboarding_keyboard import list_category_kb, load_languages_kb
from src.models.auth_models import UserData
from src.models.onboarding_models import SignUpResponseModel
from src.states.onboarding import Onboarding, Tutorial
from src.states.authentication import Authentication
from src.keyboards.reply import industry_kb, education_kb, age_kb, writing_ability_kb, phone_quality_kb, favourite_speaker_kb, task_type_kb 
from src.keyboards.dynamic import create_region_keyboard_api, create_states_keyboard_api
from src.keyboards.inline import retry_keyboard, g0_to_tutorials_kb, user_type_kb, ready_kb, tutorial_choice_kb, yes_no_inline_keyboard,tutorial_nav_kb
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from src.routes.onboarding_routes.quiz import start_quiz

from src.handlers.onboarding_handlers.onboarding import get_full_user_data, get_languages, get_saved_languages, get_selected_languages, init_age_section, init_onboarding_section, show_user_type_selection, send_tutorial
 
from src.data.video_tutorials import tutorial_videos
from src.utils.auth_utils import split_callback_response
from src.utils.dialect_format import format_dialects
from src.responses.onboarding_response import (LOCATION_MSG, QUIZ_MSG, WELCOME_MESSAGE, TUTORIAL_MSG, USER_TYPE_MSG, 
                                              PERSONAL_MSG, LANGUAGE_MSG,TASK_TYPE_MSG, ABILITY_MSG, REFERRAL_MSG, 
                                              COMPLETION_MSG)

from src.responses.auth_response import ONBOARDING_MSG
from src.services.server.getters_api import get_countries_from_api, get_languages_from_api, get_region_from_api, get_signup_list, get_states_from_api
from src.services.language_selection import DialectSelectionService, handle_language_keyboard_callback, handle_language_selection, init_language_selection
from src.services.location_service import LocationService
from src.services.task_type_service import TaskTypeService


import logging

router = Router()

logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"🔍 [DEBUG] /start command received from user {message.from_user.id}")

    await message.answer(WELCOME_MESSAGE)
    full_user_data = await get_full_user_data(state)
    if full_user_data:
        await route_user(message=message,
                         state=state)
        return

    await message.answer(USER_TYPE_MSG["option"], reply_markup=user_type_kb)
    await state.set_state(Authentication.collector_check)

@router.callback_query(Tutorial.ready_to_start, F.data.in_(["tutorial_yes", "skip_tutorials"]))
async def handle_tutorial_choice(callback: CallbackQuery, state: FSMContext):
    logger.info(f"🔍 [DEBUG] Tutorial choice: {callback.data}")
    await callback.answer()
    
    if callback.data == "tutorial_yes":
        await callback.message.answer(TUTORIAL_MSG["intro"])
        await state.set_state(Tutorial.watching)
        await send_tutorial(callback.message, state, index=0)
     
    elif callback.data == "skip_tutorials":
        await callback.message.answer("Ok, Let's beggin your onboarding !")
        await callback.message.answer(ONBOARDING_MSG["organization"],reply_markup=yes_no_inline_keyboard())
        await state.set_state(Authentication.organization_check)

# --- Handle navigation (next/back/ready) ---
@router.callback_query(Tutorial.watching, F.data.in_(["next", "prev", "ready", "skip_videos"]))
async def tutorial_navigation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    index = data.get("tutorial_index", 0)
    if callback.data == "skip_videos":
        await callback.message.answer(QUIZ_MSG["skip_ready"], reply_markup=ready_kb)
    elif callback.data == "next" and index < len(tutorial_videos) - 1:
        index += 1
        await send_tutorial(callback.message, state, index)
    elif callback.data == "prev" and index > 0:
        index -= 1
        await send_tutorial(callback.message, state, index)
   
  
@router.callback_query(Tutorial.watching, F.data == "skip_quiz")
async def handle_skip_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer()
    await show_user_type_selection(callback.message)

@router.callback_query(Tutorial.watching, F.data.in_(["quiz_yes", "quiz_no"]))
async def quiz_ready_response(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "quiz_yes":
        await callback.message.answer(QUIZ_MSG["begin_quiz"])
        await state.set_state(Onboarding.intro)
        await start_quiz(callback.message, state)

    elif callback.data == "quiz_no":
        await send_tutorial(callback.message, state, index=0)

@router.callback_query(Authentication.collector_check, F.data == "back_to_tutorials")
async def handle_back_to_tutorials(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(TUTORIAL_MSG["intro"], reply_markup=tutorial_choice_kb())
    await state.set_state(Tutorial.ready_to_start)
     
#FINISH ONBOARDING
@router.message(Onboarding.location)
async def get_country(message: Message, state: FSMContext):
    user_data = await state.get_data()
    
    if not user_data.get("country_selection_started"):
        await LocationService.initialize_country_selection(message, state)
        return
    
    countries_from_api = await get_countries_from_api()
    countries_from_api = [country.country for country in countries_from_api]
    if message.text in countries_from_api:
        await LocationService.handle_country_selection(message,state)
        return
    
    if message.text == "Next ➡️":
        await LocationService.handle_pagination_next(message, state)
        return
    
    if message.text == "⬅️ Previous":
        await LocationService.handle_location_previous(message, state)
        return

    #invalid input
    await message.answer(LOCATION_MSG["select_country"])
    await LocationService.initialize_country_selection(message, state)

@router.message(Onboarding.state_residence)
async def get_state(message: Message, state: FSMContext):
    user_data = await state.get_data()
    selected_country = user_data.get("location", "")

    #starting state selection process 
    if await LocationService.handle_state_selection(message, state):
        return 
    
    states = await get_states_from_api(selected_country) #built this in util 
    
    if len(states) > 0:
        #ivalid state selection
        await message.answer(
            LOCATION_MSG['select_state'].format(selected_country=selected_country),
            reply_markup=await create_states_keyboard_api(states)
        )
    else: 
        await init_onboarding_section(
                message=message,
                state=state,
                category="gender",  
                section=Onboarding.gender,
                answer="gender"
            )


@router.message(Onboarding.local_goverment)
async def get_region(message: Message, state: FSMContext):
    user_data = await state.get_data()
    country_id = user_data.get("location_id", "")


    #starting state selection process 
    if await LocationService.handle_region_selection(message, state):
        fulluserdata = UserData.model_validate(user_data.get("user_data"))
        signuplist = await get_signup_list(fulluserdata.company_id)
        await state.update_data(signuplist=signuplist.model_dump())

        await init_onboarding_section(
                message=message,
                state=state,
                category="gender",
                section=Onboarding.gender,
                answer="gender"
            )
        return 
    
    regions = await get_region_from_api(country_code= country_id, state_code=select_state_id) #built this in util 

    if len(regions) > 0:
        keyboard = await create_region_keyboard_api(regions = regions)
        await message.answer(
            LOCATION_MSG["lga_prompt"].format(select_state=state_residence),
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
  
@router.callback_query(Onboarding.gender)
async def get_gender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    gender = split_callback_response(callback.data)
    await state.update_data(gender=gender[1])
    await state.update_data(genderid=gender[0])
    
    await init_age_section(message = callback.message, state = state)
    
@router.callback_query(Onboarding.age_range)
async def get_age(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    age = split_callback_response(callback.data)
    await state.update_data(age=age[1])
    await state.update_data(ageid=age[0])

    await init_onboarding_section(
        message=callback.message,
        state=state,
        category="education_level",
        section=Onboarding.education,
        answer="education"
    )

@router.callback_query(Onboarding.education)
async def get_education(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    education = split_callback_response(callback.data)
    await state.update_data(education=education[1])
    await state.update_data(educationid=education[0])

    await init_onboarding_section(
        message=callback.message,
        state=state,
        category="industry",
        section=Onboarding.industry,
        answer="Field"
    )

@router.callback_query(Onboarding.industry)
async def get_industry(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    industry = split_callback_response(callback.data)
    await state.update_data(industry=industry[1])
    await state.update_data(industryid=industry[0])

    await init_language_selection(message = callback.message, state = state)

@router.callback_query(Onboarding.languages)
async def handle_language(callback: CallbackQuery, state: FSMContext):
    message, dynamic_kb = await handle_language_keyboard_callback(callback.data, state)
    if message == "":
        saved_languages = await get_selected_languages(state=state)
        if dynamic_kb == None:
            await callback.message.edit_text(text = LANGUAGE_MSG["selection_confirmed"], reply_markup=None)
            await DialectSelectionService.start_dialect_selection(callback.message, state)
        elif len(saved_languages) == 0:  
            await callback.message.edit_text(text = LANGUAGE_MSG["selection_prompt"], reply_markup=dynamic_kb)
        else:
            await callback.message.edit_text(text = LANGUAGE_MSG["selection_another"], reply_markup=dynamic_kb)

    elif message != "": 
        if dynamic_kb == None:
            await callback.message.edit_text(text = LANGUAGE_MSG["selection_prompt"], reply_markup=None)
            await callback.message.answer(text = message)
            message, new_dynamic_kb = await handle_language_keyboard_callback("page:0", state)
            await callback.message.answer(text = LANGUAGE_MSG['selection_another'], 
                                            reply_markup= new_dynamic_kb)
        else:
            await callback.message.edit_text(text = message, reply_markup= dynamic_kb)
        
@router.callback_query(Onboarding.dialect_selection)
async def get_dialect(callback: CallbackQuery, state: FSMContext):
    await DialectSelectionService.handle_dialect_selection(data = callback.data, message = callback.message, state = state)

@router.callback_query(Onboarding.task_type)
async def task_type_selection(callback: CallbackQuery, state: FSMContext):
    await TaskTypeService.handle_data_type_selection(callback.message, state, data = callback.data)

@router.callback_query(Onboarding.category_question)
async def handle_category_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("select|") or callback.data == "confirm_selection":
        await handle_multi_selection(callback=callback, state=state)
    else: 
        await handle_single_selection(callback=callback, state=state)

@router.message(Onboarding.category_question)
async def handle_text(message: Message, state: FSMContext):
    await handle_text_input(message = message, state = state)

@router.message(Onboarding.referrer)
async def get_referrer(message: Message, state: FSMContext):
    await state.update_data(referrer=message.text.strip())
   
    user_data = await state.get_data()
    await message.answer(COMPLETION_MSG ["success"])
    await message.answer("Creating your account...")

    result = await register_user(user_data, message.from_user.id)
    
    if result["success"]:
        await message.answer(f"✅ Account created! User ID: {result['user_id']}")
        from src.routes.task_routes.test_knowledge_router import handle_start_knowledge_assessment
        await handle_start_knowledge_assessment(message, state)

        "📝 Your profile:\n"
        f"Name: {user_data.get('auth_name', 'N/A')}\n"
        f"Phone: {user_data.get('auth_phone', 'N/A')}\n"
        f"Gender: {user_data.get('gender', 'N/A')}\n"
        f"Nationality: {user_data.get('location', 'N/A')}\n"
        f"State of Residence: {user_data.get('state_residence', 'N/A')}\n" 
        f"Languages: {user_data.get('languages', 'N/A')}\n"
        f"Dialects: {format_dialects(user_data.get('dialects', {}))}\n" 
        f"Education: {user_data.get('education', 'N/A')}\n"
        f"Industry: {user_data.get('industry', 'N/A')}\n"
        f"Data Type: {user_data.get('task_type', 'N/A')}\n"
        f"Referrer: {user_data.get('referrer', 'N/A')}"
    

        # from src.routes.task_routes.test_knowledge_router import start_knowledge_assessment
        # await start_knowledge_assessment(message, state)

        from src.routes.task_routes.test_knowledge_router import handle_start_knowledge_assessment
        await handle_start_knowledge_assessment(message, state)


        print(message.from_user.id, "has completed onboarding with data:", user_data)

    else:
        await message.answer(f"❌ Failed: {result['error']}")
        await message.answer("Try again?", reply_markup=retry_keyboard())
        await state.set_state(Onboarding.registration_retry)
    
@router.callback_query(Onboarding.registration_retry, F.data == "retry_reg")
async def retry_registration(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_data = await state.get_data()
    
    result = await register_user(user_data, callback.from_user.id)
    
    if result["success"]:
        await callback.message.answer(f"✅ Success! User ID: {result['user_id']}")
        from src.routes.task_routes.test_knowledge_router import handle_start_knowledge_assessment
        await handle_start_knowledge_assessment(callback.message, state)
    else:
        await callback.message.answer(f"❌ Still failed: {result['error']}")
        await callback.message.answer("Try again?", reply_markup=retry_keyboard())