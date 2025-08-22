from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import sessionmaker
from src.database.models import Agent 
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from src.responses.auth_response import LOGIN_MSG, ONBOARDING_MSG, EMAIL_MSG, PHONE_MSG, PASSWORD_MSG
from src.responses.onboarding_response import TUTORIAL_MSG, USER_TYPE_MSG
from src.services.server.auth import user_login
from src.utils.auth_utils import validate_email, validate_phone_format, format_phone
from src.states.authentication import Authentication
from src.states.onboarding import Onboarding, Tutorial
from src.keyboards.auth import company_kb
from src.keyboards.inline import yes_no_inline_keyboard, create_account_inline_keyboard, tutorial_choice_kb
from src.utils.password import hash_password, verify_password 
import re
import logging

router = Router()

logger = logging.getLogger(__name__)

#chose user type
@router.callback_query(Authentication.collector_check, F.data.in_(["registered_yes", "new_user"]))
async def handle_user_type_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "registered_yes":
        # existing user --> login
        await callback.message.answer(LOGIN_MSG["welcome_back"])
        await state.set_state(Authentication.login_email)
        
    elif callback.data == "new_user":
        await callback.message.answer(ONBOARDING_MSG["welcome"])
        await callback.message.answer(TUTORIAL_MSG["intro"], reply_markup=tutorial_choice_kb())
        await state.set_state(Tutorial.ready_to_start)


# Handler: Login - Email/Phone input
@router.message(Authentication.login_email)
async def handle_login_identifier(message: Message, state: FSMContext):
    identifier = message.text.strip()
    await state.update_data(login_identifier=identifier)
    await message.answer("🔒 Please enter your password:")
    await state.set_state(Authentication.login_password)

# Handler: Login - Password input
@router.message(Authentication.login_password)
async def handle_login_password(message: Message, state: FSMContext):
    password = message.text.strip()
    user_data = await state.get_data()
    identifier = user_data.get('login_identifier')
    
    response = user_login(identifier, password)

    if not response:
        await message.answer(LOGIN_MSG["fail"])

    await message.answer(LOGIN_MSG["success"].format(name=response.data.name if response else "User"))
    await state.set_data({"user_data":response.data.model_dump()})
    

# Failed login
@router.callback_query(Authentication.login_email, F.data.in_(["create_account", "try_login_again"]))
async def handle_login_failure_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    if callback.data == "create_account":
        #redirect to create an account
        await callback.message.answer( "🌟 Let's create your account!\n\n")
        org_kb = yes_no_inline_keyboard
        await callback.message.answer(LOGIN_MSG["organization"],reply_markup=org_kb)
        await state.set_state(Authentication.organization_check)
        
    elif callback.data == "try_login_again":
        await callback.message.answer(LOGIN_MSG["enter_email/phone"])
        await state.set_state(Authentication.login_email)

# Handler: Are you part of organization?
@router.callback_query(Authentication.organization_check, F.data.in_(["org_yes", "org_no"]))
async def handle_organization_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
       
    if callback.data == "org_yes":
        await state.update_data(has_organization="Yes")
        await callback.message.answer(ONBOARDING_MSG["org_selection"],reply_markup=company_kb())
        await state.set_state(Authentication.company_selection)
    else:
        await state.update_data(has_organization="No", company="Individual")
        await callback.message.answer(ONBOARDING_MSG["name_input"])
        await state.set_state(Authentication.name_input)

# Handler: Company selection
@router.message(Authentication.company_selection)
async def handle_company_selection(message: Message, state: FSMContext):
    company = message.text.strip()
    await state.update_data(company=company)
    await message.answer(ONBOARDING_MSG["name_input"])
    await state.set_state(Authentication.name_input)

# Handler: Name input
@router.message(Authentication.name_input)
async def handle_name_input(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(auth_name=name)
    await message.answer(EMAIL_MSG["prompt"])
    await state.set_state(Authentication.email_input)

# Handler: Email input
@router.message(Authentication.email_input)
async def handle_email_input(message: Message, state: FSMContext):
    email = message.text.strip()

    if not validate_email(email):
        await message.answer(EMAIL_MSG["invalid"])
        return 
    await state.update_data(email=email)
    
    await message.answer(PHONE_MSG["prompt"])
    await state.set_state(Authentication.phone_input)

# Handler: Phone input
@router.message(Authentication.phone_input)
async def handle_phone_input(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not validate_phone_format(phone):
        await message.answer(PHONE_MSG["invalid"])
        return
    
    formatted_phone = format_phone(phone)
    await state.update_data(auth_phone=formatted_phone)
    
    await message.answer(PASSWORD_MSG["prompt"])
    await state.set_state(Authentication.password_input)

# Handler: Password input
@router.message(Authentication.password_input)
async def handle_password_input(message: Message, state: FSMContext):
    password = message.text.strip()

    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        await message.answer(PASSWORD_MSG["weak"])
        return  
    
    await state.update_data(password=password)
    await message.answer(PASSWORD_MSG["confirm"])
    await state.set_state(Authentication.confirm_password)


@router.message(Authentication.confirm_password)
async def handle_confirm_password(message: Message, state: FSMContext):
    print(f"🔍 [DEBUG] Confirm password handler appelé")
    
    confirm_password = message.text.strip()
    user_data = await state.get_data()
    if confirm_password != user_data.get('password'):
        await message.answer(PASSWORD_MSG["mismatch"])
        return
    hashed_password = hash_password(confirm_password)
    await state.update_data(password_hash=hashed_password)
    
    # Passwords match - create account
    await message.answer(ONBOARDING_MSG["account_created"])
    await state.set_state(Onboarding.location)
    print(f"🔍 [DEBUG] État changé vers Onboarding.location")

    from src.routes.onboarding_routes.onboarding import get_country
    await get_country(message, state)

    
   
