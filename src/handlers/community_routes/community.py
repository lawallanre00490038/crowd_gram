import asyncio
from aiogram import F, Router,types

from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from .broadcast import (
    broadcast_new_policies,
    broadcast_new_projects,
    broadcast_new_trainings,
    daily_trivia,
    create_poll,
    get_top_agent_this_week,
    handle_message,
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

#For handling trivia questions
@router.message()
async def handle_message_wrapper(message: types.Message):
    await handle_message(message)
