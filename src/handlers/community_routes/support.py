import asyncio
import json
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Bold, Text

from src.config import ADMIN_IDS
from src.keyboards.inline import accept_support_request
from src.loader import bot

router = Router()

@router.message(Command("support"))
async def send_support(message: Message):
    """Send support request to admin"""
    start_message = Text("Hello ",Bold(message.from_user.full_name), " 👋," ," I will try and connect you to an available agent to support you!")  # noqa: E501
    await bot.send_message(**start_message.as_kwargs(), chat_id=message.from_user.id)
    all_messages = [bot.send_message(chat_id=admin_id, reply_markup=accept_support_request(message.from_user.id), text=f"{message.from_user.username or message.from_user.full_name} is requesting support from an agent!") for admin_id in ADMIN_IDS]  # noqa: E501
    await asyncio.gather(*all_messages)

@router.callback_query()
async def accept_user_request(callback: CallbackQuery):
    """Accept support request from user"""
    await callback.answer()
    try:
        callback_data = json.loads(callback.data)
    except Exception as e:
        logging.error(f"Community Support Error in accept_user_request() when parsing json. Details: {e} ")  # noqa: E501
    try:
        if callback_data['text']:
            await bot.send_message(chat_id=callback_data['chat_id'], text=f"{callback.from_user.full_name} has accepted your request and will reach out to you shortly!")  # noqa: E501

    except Exception as e:
        logging.error(f"Community Support Error Details: {e}")