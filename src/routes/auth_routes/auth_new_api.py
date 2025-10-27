from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.responses.auth_response import EXIT, LOGIN_MSG, LOGOUT
from src.responses.onboarding_response import WELCOME_MESSAGE
from src.services.server.api2_server.auth import user_login
from src.services.server.api2_server.projects import get_projects_details
from src.models.api2_models.telegram import LoginModel
from src.states.authentication import Authentication
from src.keyboards.inline import project_selection_kb, new_api_login_type_inline

router = Router()


@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext):
    """Send welcome message and prompt login/signup"""
    await message.answer(WELCOME_MESSAGE)
    await message.answer(LOGIN_MSG["welcome_back"], reply_markup=new_api_login_type_inline)
    await state.set_state(Authentication.set_login_type)


@router.message(Command("logout"))
async def handle_logout(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(LOGOUT["logout"])


@router.message(Command("exit"))
async def handle_exit(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(EXIT["exit"])


@router.callback_query(Authentication.set_login_type, F.data.in_(["login", "register"]))
async def handle_login_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "login":
        await callback.message.answer(LOGIN_MSG["enter_email"])
        await state.set_state(Authentication.api_login_email)
    elif callback.data == "register":
        await callback.message.answer(LOGIN_MSG["register"])
        await state.set_state(Authentication.api_register_type)


@router.message(Authentication.api_login_email)
async def handle_login_email(message: Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(login_identifier=email)
    await message.answer("🔒 Please enter your password:")
    await state.set_state(Authentication.api_login_password)


@router.message(Authentication.api_login_password)
async def handle_login_password(message: Message, state: FSMContext):
    password = message.text.strip()
    user_data = await state.get_data()
    email = user_data.get("login_identifier")

    user_input = LoginModel(email=email, password=password)
    response = await user_login(user_data=user_input)

    if response.get("success"):
        name = getattr(response['base_info'], 'name', 'User')
        role = getattr(response['base_info'], 'role', 'User')
        telegram_id = getattr(response['base_info'], 'telegram_id', 'N/A')
        await message.answer(LOGIN_MSG["success_2"].format(name=name))

        # Save data - check for None before calling model_dump()
        await state.clear()

        await state.set_data({'user_email': email, "name": name, "role": role.lower(), "telegram_id": telegram_id})

        await handle_user_projects(message, state)
    else:
        await state.clear()
        await message.answer(LOGIN_MSG["fail"], reply_markup=new_api_login_type_inline)
        await state.set_state(Authentication.set_login_type)


async def handle_user_projects(message: Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data.get("user_email")

    projects_details = await get_projects_details(user_email=email)
    if not projects_details:
        await message.answer("No projects found for your account.")
        return

    await state.update_data({"projects_details": projects_details})
    await message.answer(
        "Please select a project to continue:",
        reply_markup=project_selection_kb(
            [proj["name"] for proj in projects_details])
    )
