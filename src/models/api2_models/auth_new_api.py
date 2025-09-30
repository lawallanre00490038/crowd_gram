from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
import logging

from src.handlers.auth_handlers.auth_handlers import route_user, user_signup, user_verify_otp
from src.handlers.onboarding_handlers.onboarding import get_full_user_data, get_country
from src.models.auth_models import UserData
from src.responses.auth_response import EXIT, LOGIN_MSG, LOGOUT, ONBOARDING_MSG, EMAIL_MSG, PHONE_MSG, PASSWORD_MSG
from src.responses.onboarding_response import TUTORIAL_MSG
from src.services.server.auth import user_login
from src.utils.auth_utils import validate_email, validate_password, validate_phone_format, format_phone
from src.states.authentication import Authentication
from src.states.onboarding import Onboarding, Tutorial
from src.keyboards.inline import yes_no_inline_keyboard, set_signup_type_inline, tutorial_choice_kb
from src.keyboards.auth_keyboard import company_kb

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext):
    """Send welcome message and prompt login/signup"""
    await message.answer("👋 Welcomme to Equalyz Crowd!\n\nWe're building the future of AI by collecting multilingual data across Africa.\n\nAs a contributor/agent, you'll help train AI models and earn money for quality work.\n\nLet's begin! 🚀.\n\nPlease log in to continue.")
    await message.answer(LOGIN_MSG["welcome_back"], reply_markup=set_signup_type_inline)
    await state.set_state(Authentication.set_login_type)


@router.message(Command("logout"))
async def handle_logout(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(LOGOUT["logout"])


@router.message(Command("exit"))
async def handle_exit(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(EXIT["exit"])


@router.callback_query(Authentication.set_login_type, F.data.in_(["email", "phone_number"]))
async def handle_login_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "email":
        await callback.message.answer(LOGIN_MSG["enter_email"])
        await state.set_state(Authentication.login_email)
    elif callback.data == "phone_number":
        await callback.message.answer(LOGIN_MSG["enter_phone"])
        await state.set_state(Authentication.login_phone)


@router.message(Authentication.login_email)
async def handle_login_email(message: Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(login_identifier=email)
    await message.answer("🔒 Please enter your password:")
    await state.set_state(Authentication.login_password)


@router.message(Authentication.login_password)
async def handle_login_password(message: Message, state: FSMContext):
    password = message.text.strip()
    user_data = await state.get_data()
    email = user_data.get("login_identifier")

    response = await user_login(email, password)

    if not response.get("success"):
        await message.answer(LOGIN_MSG["fail"])
        await state.clear()
        return

    # Friendly login success message
    await message.answer(
        f"{response['message']}\n\n"
        f"Role: {response['user_role']}\n"
        f"Languages: {', '.join(response['user_languages'])}\n"
        f"Dialects: {', '.join(response['user_dialects'])}"
    )

    # Save data + route to tasks
    await state.clear()
    await state.set_data({"user_data": response})
    await route_user(
        full_user_data=UserData.model_validate(response),
        message=message,
        state=state,
    )


@router.message(Command("signup"))
async def handle_signup(message: Message, state: FSMContext):
    await message.answer("Ok, Let's begin your onboarding !")
    await message.answer(ONBOARDING_MSG["organization"], reply_markup=yes_no_inline_keyboard())
    await state.set_state(Authentication.organization_check)


@router.callback_query(Authentication.collector_check, F.data.in_(["registered_yes", "new_user"]))
async def handle_user_type_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "registered_yes":
        await callback.message.answer(LOGIN_MSG["welcome_back"])
        await state.set_state(Authentication.login_email)
    elif callback.data == "new_user":
        await callback.message.answer(ONBOARDING_MSG["welcome"])
        await callback.message.answer(TUTORIAL_MSG["intro"], reply_markup=tutorial_choice_kb())
        await state.set_state(Tutorial.ready_to_start)

