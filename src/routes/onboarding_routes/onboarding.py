from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states.onboarding import Onboarding, Tutorial
from src.states.authentication import Authentication
from src.keyboards.reply import industry_kb, education_kb, age_kb, writing_ability_kb, phone_quality_kb, favourite_speaker_kb, task_type_kb 
from src.keyboards.dynamic import (create_countries_keyboard_reply_api, create_states_keyboard_api, create_language_keyboard_api)
from src.keyboards.inline import retry_keyboard, g0_to_tutorials_kb, user_type_kb, ready_kb, tutorial_choice_kb, yes_no_inline_keyboard,tutorial_nav_kb
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from src.routes.onboarding_routes.quiz import start_quiz
 
from src.data.video_tutorials import tutorial_videos
from src.utils.dialect_format import format_dialects
from src.responses.onboarding_response import (WELCOME_MESSAGE, TUTORIAL_MSG, USER_TYPE_MSG, 
                                              PERSONAL_MSG, LANGUAGE_MSG,TASK_TYPE_MSG, ABILITY_MSG, REFERRAL_MSG, 
                                              COMPLETION_MSG)

from src.responses.auth_response import ONBOARDING_MSG
from src.services.server.getters_api import get_countries_from_api
from src.services.language_selection import LanguageSelectionService, DialectSelectionService
from src.services.location_service import LocationService
from src.services.task_type_service import TaskTypeService
from src.services.server.api_registration import register_user

import re

from pathlib import Path
from aiogram.types import InputFile
from aiogram.types import FSInputFile


router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    print(f"🔍 [DEBUG] /start command received from user {message.from_user.id}")
    await message.answer(WELCOME_MESSAGE)
    await show_user_type_selection(message, state)
    await state.set_state(Authentication.collector_check)

    

@router.callback_query(Tutorial.ready_to_start, F.data.in_(["tutorial_yes", "skip_tutorials"]))
async def handle_tutorial_choice(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Tutorial choice: {callback.data}")
    await callback.answer()
    
    if callback.data == "tutorial_yes":
        await callback.message.answer(TUTORIAL_MSG["intro"])
        await state.update_data(tutorial_index=0)
        await state.set_state(Tutorial.watching)
        await send_tutorial(callback.message, state)
     
    elif callback.data == "skip_tutorials":
        await callback.message.answer("Ok, Let's beggin your onboarding !")
        await callback.message.answer(ONBOARDING_MSG["organization"],reply_markup=yes_no_inline_keyboard())
        await state.set_state(Authentication.organization_check)



async def show_user_type_selection(message: Message, state: FSMContext):
    await message.answer(USER_TYPE_MSG["selection"])
    await message.answer(USER_TYPE_MSG["option"], reply_markup=user_type_kb
    )
    await state.set_state(Authentication.collector_check)


async def send_tutorial(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data.get("tutorial_index", 0)
    await message.answer(tutorial_videos[index], reply_markup=tutorial_nav_kb(index))

# --- Handle navigation (next/back/ready) ---

@router.callback_query(Tutorial.watching, F.data.in_(["next", "prev", "ready", "skip_videos"]))
async def tutorial_navigation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    index = data.get("tutorial_index", 0)

    if callback.data == "next" and index < len(tutorial_videos) - 1:
        index += 1
        await state.update_data(tutorial_index=index)
        await send_tutorial(callback.message, state)

    elif callback.data == "prev" and index > 0:
        index -= 1
        await state.update_data(tutorial_index=index)
        await send_tutorial(callback.message, state)
   
    elif callback.data == "skip_videos":
        await callback.message.answer(TUTORIAL_MSG["skip_ready"], reply_markup=ready_kb)
     
@router.callback_query(Tutorial.watching, F.data == "skip_quiz")
async def handle_skip_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("⏭️ Quiz skipped!")
    await show_user_type_selection(callback.message, state)

@router.callback_query(Tutorial.watching, F.data.in_(["quiz_yes", "quiz_no"]))
async def quiz_ready_response(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "quiz_yes":
        await callback.message.answer("✅ Great! Let's begin the short quiz.")
        await state.set_state(Onboarding.intro)
        await start_quiz(callback.message, state)

    elif callback.data == "quiz_no":
        await state.update_data(tutorial_index=0)
        await send_tutorial(callback.message, state)

@router.callback_query(Authentication.collector_check, F.data == "back_to_tutorials")
async def handle_back_to_tutorials(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(TUTORIAL_MSG["intro"], reply_markup=tutorial_choice_kb())
    await state.set_state(Tutorial.ready_to_start)

#END TUTO AND QUIZ DISPLAY


     
#FINISH ONBOARDING

@router.message(Onboarding.location)
async def get_country(message: Message, state: FSMContext):
    user_data = await state.get_data()
    
    if not user_data.get("country_selection_started"):
        await LocationService.initialize_country_selection(message, state)
        return
    
    countries_from_api= await get_countries_from_api()
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
    await message.answer("Please select a valid country from the list.")
    await LocationService.initialize_country_selection(message, state)

@router.message(Onboarding.state_residence)
async def get_state(message: Message, state: FSMContext):
    user_data = await state.get_data()
    selected_country = user_data.get("location", "")

    #starting state selection process 
    if await LocationService.handle_state_selection(message, state):
        return 
    
    #ivalid state selection
    await message.answer(
        f"Please select a valid state for {selected_country}:",
        reply_markup=await create_states_keyboard_api(selected_country)
    )
  
@router.message(Onboarding.gender)
async def get_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text.strip())
    await message.answer(PERSONAL_MSG["age"], reply_markup=age_kb)
    await state.set_state(Onboarding.age_range)

@router.message(Onboarding.age_range)
async def get_age(message: Message, state: FSMContext):
    await state.update_data(age_range=message.text.strip())
    await state.update_data(selected_languages=[])
    await message.answer(PERSONAL_MSG["education"], reply_markup=education_kb)
    await state.set_state(Onboarding.education)


@router.message(Onboarding.education)
async def get_education(message: Message, state: FSMContext):
    
    valid_options = ["High School Diploma", "Bachelor's Degree", "Master's Degree", "Doctorate Degree", "SSCE/WAEC", "Other"]
    if message.text in valid_options:
        await state.update_data(education=message.text.strip())
        await message.answer(f"✅ Education level selected: {message.text}")
        await message.answer("💼 What field do you work in?", reply_markup=industry_kb)
        await state.set_state(Onboarding.industry)
    else:
        await message.answer(PERSONAL_MSG["education_invalid"],reply_markup=education_kb)

@router.message(Onboarding.industry)
async def get_industry(message: Message, state: FSMContext):
    await state.update_data(industry=message.text.strip())
    dynamic_kb = await create_language_keyboard_api()
    await message.answer(LANGUAGE_MSG["selection_prompt"],reply_markup=dynamic_kb)  
    await state.set_state(Onboarding.languages) 


@router.message(Onboarding.languages)
async def get_language(message: Message, state: FSMContext):
    await LanguageSelectionService.handle_language_selection(message, state)

@router.message(Onboarding.languages, F.text == "✅ Done")
async def language_selection_done(message: Message, state: FSMContext):
    success = await LanguageSelectionService.handle_language_selection_done(message, state)
    if success:   
        pass

@router.message(Onboarding.dialect_selection)
async def get_dialect(message: Message, state: FSMContext):
    is_complete = await DialectSelectionService.handle_dialect_selection(message, state)
    if not is_complete:
        #go to task_type selection-- handled by language_selection_service
        pass


@router.message(Onboarding.task_type, F.text == "✅ Done")
async def task_type_selection_done(message: Message, state: FSMContext):
    user_data = await state.get_data()
    selected_data_types = user_data.get("selected_data_types", [])
    if len(selected_data_types) >= 1:
        await TaskTypeService.handle_data_type_selection_done(message, state)
    else: 
        await message.answer(TASK_TYPE_MSG["min_selection"])

@router.message(Onboarding.task_type)
async def get_task_type(message: Message, state: FSMContext):
    all_data_types = ["📝Text", "🎤Audio"]

    if message.text not in all_data_types:
        await state.update_data(selected_data_types=[])
        await message.answer("📌 What kind of data do you want to give?\nSelect one or both.", reply_markup=task_type_kb)
        return
    
    await TaskTypeService.handle_data_type_selection(message, state)
    

@router.message(Onboarding.text_writing_ability)
async def handle_text_writing_ability(message: Message, state: FSMContext):
    await state.update_data(text_writing_ability=message.text.strip())
    await message.answer(f"✅ Writing ability: {message.text}")
    
    user_data = await state.get_data()
    selected_data_types = user_data.get("selected_data_types", [])

    if "🎤Audio" in selected_data_types:
        await message.answer(ABILITY_MSG["phone_quality"],reply_markup=phone_quality_kb)
        await state.set_state(Onboarding.phone_quality)
    else:
        await message.answer(REFERRAL_MSG["prompt"])
        await state.set_state(Onboarding.referrer)

@router.message(Onboarding.phone_quality)
async def handle_phone_quality(message: Message, state: FSMContext):
    await state.update_data(phone_quality=message.text.strip())
    await message.answer(f"Phone quality: {message.text}")
    await message.answer(ABILITY_MSG["favourite_speaker"],reply_markup=favourite_speaker_kb)
    await state.set_state(Onboarding.favourite_speaker)

@router.message(Onboarding.favourite_speaker)
async def handle_favourite_speaker(message: Message, state: FSMContext):
    await state.update_data(favourite_speaker=message.text.strip())
    await message.answer(f"Favourite speaker: {message.text}")
    await message.answer(REFERRAL_MSG["prompt"])
    await state.set_state(Onboarding.referrer)


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
    
  