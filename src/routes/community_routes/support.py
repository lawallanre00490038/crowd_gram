import asyncio
import json
from loguru import logger

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Bold, Text

from src.config import ADMIN_IDS
from src.keyboards.inline import accept_support_request
from src.loader import bot

router = Router()
active_request = {}


@router.message(Command("support"), F.chat.type.not_in({ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}))  # noqa: E501
async def send_support(message: Message):
    """Send support request to admin"""
    user_id = message.from_user.id
    if active_request.get(user_id):
        await bot.send_message(chat_id=user_id, text="You still have a support request that is being resolved, please try again after you finish getting support.")
        return
    start_message = Text("Hello ", Bold(message.from_user.full_name), " 👋,", " I will try and connect you to an available agent to support you!")  # noqa: E501
    await bot.send_message(**start_message.as_kwargs(), chat_id=message.from_user.id)
    all_messages = [bot.send_message(chat_id=admin_id, reply_markup=accept_support_request(user_id), text=f"{message.from_user.username or message.from_user.full_name} is requesting support from an agent!") for admin_id in ADMIN_IDS]  # noqa: E501
    await asyncio.gather(*all_messages)

# get admins


@router.message(Command("community_support"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))  # noqa: E501
async def perform_community_support(message: Message):
    user_id = message.chat.id
    user_username = message.from_user.username
    user_name = f"@{user_username}" if user_username else message.from_user.full_name

    # Notify all admins
    requests = []
    for admin_id in ADMIN_IDS:
        bot_message = bot.send_message(
            chat_id=admin_id,
            text=f"🚨 <b>Support Request</b>\nUser <b>{user_name}</b> is requesting help.",  # noqa: E501
            reply_markup=accept_support_request(chat_id=user_id),
            parse_mode="HTML"
        )

        requests.append(bot_message)

    await asyncio.gather(*requests)

    await message.reply(
        f"👋 Hi {user_name}, our admin team has been notified. Please hold on while someone attends to you."  # noqa: E501
    )


@router.callback_query()
async def handle_take_request(callback_query: CallbackQuery):

    callback_data = json.loads(callback_query.data)
    user_id = int(callback_data["user_id"])
    admin_id = callback_query.from_user.id

    # check if request is in active request
    if user_id in active_request:
        await callback_query.answer("❌ This request has already been taken.")
        return

    # Assign this admin
    active_request[user_id] = admin_id
    await callback_query.answer("✅ You've taken up the request.")

    # Disable button for other admins
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    # Inform the user
    await bot.send_message(
        chat_id=user_id,
        text=(
            f"✅ An admin has taken up your support request.\n"
            f"You can now message them directly here: "
            f"<a href='tg://user?id={admin_id}'>Contact Admin</a>."
        ),
        parse_mode="HTML"
    )

    # Inform other admins

    requests = []
    for other_admin in ADMIN_IDS:
        if int(other_admin) != admin_id:
            bot_message = bot.send_message(
                chat_id=other_admin,
                text="This support request has already been taken by another admin."
            )

            requests.append(bot_message)

    await asyncio.gather(*requests)

    # @router.message(Command("end_support"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
    # async def end_private_chat(user_id):
    #     await bot.send_message(chat_id=CHANNEL_ID, text="The admin has resolved your request for support. Thank you.")
    #     if active_request.get(user_id):
    #         active_request.pop(user_id)
    #         return
