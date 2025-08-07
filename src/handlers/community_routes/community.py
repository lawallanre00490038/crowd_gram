import asyncio

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from .broadcast import (
    broadcast_new_policies,
    broadcast_new_projects,
    broadcast_new_trainings,
    create_poll,
    get_top_agent_this_week,
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


@router.message(Command("poll"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def handle_poll(message: Message):
    await create_poll(message)
