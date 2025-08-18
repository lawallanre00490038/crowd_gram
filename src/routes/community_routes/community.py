import asyncio

from aiogram import F, Router, types
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from src.data.community_mock_data import (
    json_data_broadcast_policy_insert,
    json_data_broadcast_project_insert,
    json_data_broadcast_trainings_insert,
    json_str,
)
from src.utils.text_utils import format_json_str_to_json, format_json_to_table

from .broadcast import (
    broadcast_new_policies,
    broadcast_new_projects,
    broadcast_new_trainings,
    create_poll,
    daily_trivia,
    get_top_agent_this_week,
    handle_message,
    is_trivia_reply,
    send_leaderboard_weekly,
    send_monthly_contest,
    send_wellness_weekly,
)

router = Router()

async def start_community_background_tasks():
    asyncio.create_task(send_leaderboard_weekly())
    asyncio.create_task(get_top_agent_this_week())
    asyncio.create_task(send_monthly_contest())
    asyncio.create_task(broadcast_new_projects())
    asyncio.create_task(broadcast_new_trainings())
    asyncio.create_task(broadcast_new_policies())
    asyncio.create_task(send_wellness_weekly())
    asyncio.create_task(daily_trivia())



@router.message(Command("poll"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def handle_poll(message: Message):
    await create_poll(message)


@router.message(Command("leaderboard"))
async def send_leaderboard_to_bot(message: types.Message):
    """Send Leaderboard to Bot"""

    json_data = format_json_str_to_json(json_str=json_str)

    table = format_json_to_table(json_data=json_data)

    code_text = (
    "- N : Name\n"
    "- TT: Total Task\n"
    "- TC: Task Completed\n"
    "- CE: Coin Earned\n"
    "- R : Ratings"
    )

    text = (
    "🏆 <b>Leaderboard This Week</b>\n\n"
    "Meaning of Columns\n{}\n"
    "<pre>{}</pre>"
    ).format(code_text, table)

    await message.answer(text=text)




#For handling trivia questions
@router.message(is_trivia_reply)
async def handle_message_wrapper(message: types.Message):
    await handle_message(message)
