from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from loguru import logger
from typing import Union

from src.handlers.onboarding_handlers.onboarding import send_tutorial
from src.responses.auth_response import EXIT, LOGIN_MSG, LOGOUT
from src.responses.onboarding_response import TUTORIAL_MSG, WELCOME_MESSAGE, QUIZ_MSG
from src.states.onboarding import Tutorial
from src.routes.onboarding_routes.quiz import start_quiz
from src.services.server.api2_server.auth import user_login
from src.services.server.api2_server.projects import get_projects_details
from src.models.api2_models.telegram import LoginModel
from src.states.authentication import Authentication
from src.keyboards.inline import project_selection_kb, new_api_login_type_inline

router = Router()


@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext):
    """Send welcome message and prompt login/signup"""
    await state.clear()
    await message.answer(WELCOME_MESSAGE)
    await message.answer(LOGIN_MSG["welcome_back"], reply_markup=new_api_login_type_inline)
    await state.set_state(Authentication.set_login_type)

    return


@router.message(Command("logout"))
async def handle_logout(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(LOGOUT["logout"])

    return


@router.message(Command("exit"))
async def handle_exit(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(EXIT["exit"])

    return


@router.callback_query(Authentication.set_login_type, F.data.in_(["login", "register"]))
async def handle_login_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    logger.trace("Supplying")
    if callback.data == "login":
        await callback.message.answer(LOGIN_MSG["enter_email"])
        await state.set_state(Authentication.api_login_email)
    elif callback.data == "register":
        await callback.message.answer(LOGIN_MSG["register"])
        await state.set_state(Authentication.api_register_type)

    return


@router.message(Authentication.api_login_email)
async def handle_login_email(message: Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(login_identifier=email)
    await message.answer("🔒 Please enter your password:")
    await state.set_state(Authentication.api_login_password)

    return


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

        await state.clear()

        await state.set_data({'user_email': email, "name": name, "role": role.lower(), "telegram_id": telegram_id})

        await handle_user_projects(message, state)
    else:
        await state.clear()
        await message.answer(LOGIN_MSG["fail"], reply_markup=new_api_login_type_inline)
        await state.set_state(Authentication.set_login_type)

    return


@router.message(Command("projects"))
@router.callback_query(F.data.in_(["ready_for_task"]))
async def handle_user_projects(event: Union[Message, CallbackQuery], state: FSMContext):
    # Get the message object
    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message
    else:
        message = event

    user_data = await state.get_data()
    email = user_data.get("user_email")

    if not email:
        await message.answer("You need to log in first. Use /start to log in.")
        return

    projects_details = await get_projects_details(user_email=email)
    logger.trace(f"Fetched projects details: {projects_details}")
    if not projects_details:
        await message.answer("No projects found for your account.")
        return

    await state.update_data({"projects_details": projects_details})
    await message.answer(
        "Please select a project to continue:",
        reply_markup=project_selection_kb(
            [proj["name"] for proj in projects_details])
    )

    return


@router.callback_query(F.data.in_(["tutorial_yes", "skip_tutorials"]))
async def handle_tutorial_choice(callback: CallbackQuery, state: FSMContext):
    logger.info(f"🔍 [DEBUG] Tutorial choice: {callback.data}")
    await callback.answer()

    if callback.data == "tutorial_yes":
        await callback.message.answer(TUTORIAL_MSG["intro"])
        await state.set_state(Tutorial.watching)
        await send_tutorial(callback.message, state, index=0)

    elif callback.data == "skip_tutorials":
        await handle_user_projects(callback, state)

    return

# --- Handle navigation (next/back/ready) ---


@router.callback_query(F.data.in_(["next", "prev", "ready", "skip_videos"]))
async def tutorial_navigation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    index = data.get("tutorial_index", 0)
    if callback.data == "skip_videos":
        await handle_user_projects(callback.message, state)
    elif callback.data == "next":
        index += 1
        await send_tutorial(callback.message, state, index)
    elif callback.data == "prev" and index > 0:
        index -= 1
        await send_tutorial(callback.message, state, index)

    return
