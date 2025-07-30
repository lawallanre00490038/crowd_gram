import asyncio

from aiogram import Router

from aiogram import types

from .broadcast import (
    broadcast_new_policies,
    broadcast_new_projects,
    broadcast_new_trainings,
    get_top_agent_this_week,
    send_leaderboard_weekly,
    send_monthly_contest,
    send_wellness_weekly,
    daily_trivia,
    current_trivia,
    user_answers,
    handle_message,
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


@router.message()
async def handle_message_wrapper(message: types.Message):
    await handle_message(message)