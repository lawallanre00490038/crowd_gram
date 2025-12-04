
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import psutil


class AdminAuthentication(StatesGroup):
    admin_login = State()


router = Router()

@router.message(Command("report"))
async def handle_report(message: Message, state: FSMContext):
    isadmin = await state.get_value("isadmin", None)
    if isadmin is not   None:
        await message.answer("What do you want to know ?", reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Server Performance', callback_data='admin_performance')],
                [InlineKeyboardButton(text='Server Trace', callback_data='admin_trace')],
                [InlineKeyboardButton(text='Server Logs', callback_data='admin_logs')]
            ]
        ))
        return
    await message.answer("What do you want to report? Please provide details.")

@router.callback_query(F.data.in_(['admin_performance']))
async def handle_admin_performance(callback: CallbackQuery, state: FSMContext):
    isadmin = await state.get_value("isadmin", None)
    if isadmin is None:
        await callback.message.answer("Access denied. Please login as admin using /adminlogin.")
        return
    process = psutil.Process()
    cpu = process.cpu_percent()
    mem = process.memory_info().rss / (1024 ** 2)
    await callback.message.answer(f"[Resources] CPU: {cpu:.2f}% | Memory: {mem:.2f} MB")
    # Here you would typically fetch and display server performance metrics

@router.callback_query(F.data.in_(['admin_trace', 'admin_logs']))
async def handle_admin_performance(callback: CallbackQuery, state: FSMContext):
    import os
    BASE_DIR = os.getcwd()


    isadmin = await state.get_value("isadmin", None)
    if isadmin is None:
        await callback.message.answer("Access denied. Please login as admin using /adminlogin.")
        return

    if callback.data == 'admin_trace':
        file_path = os.path.join(BASE_DIR, "log", "trace.log")

    elif callback.data == 'admin_logs':
        file_path = os.path.join(BASE_DIR,"log", "bot_logs.log")

    if os.path.exists(file_path):
        file = FSInputFile(file_path, filename=os.path.basename(file_path))
        await callback.message.answer_document(file)
    else:
        print(file_path)
        await callback.message.answer("Log file not found.")


@router.message(Command("adminlogin"))
async def handle_report(message: Message, state: FSMContext):
    
    await message.answer("Please input your login details to access admin features.")

    await state.set_state(AdminAuthentication.admin_login)

@router.message(AdminAuthentication.admin_login)
async def handle_admin_login(message: Message, state: FSMContext):
    login_details = message.text.strip()
    if not login_details:
        await message.answer("Login details cannot be empty. Please try again.")
        return

    # Here you would typically validate the login details
    # For simplicity, we assume the login is successful
    if login_details == "LoladeAdmin":  # Example validation
        await message.answer("Login successful! You are now an admin.")
    else:
        await message.answer("Invalid login details. Please try again.")
        return
    
    await state.set_data({"isadmin": True})
    await message.answer("You are now logged in as an admin. You can use /report to report issues.")