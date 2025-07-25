import asyncio

from aiogram import Router

from .broadcast import (
    get_top_agent_this_week,
    send_leaderboard_weekly,
    send_monthly_contest,
)

router = Router()

async def start_community_background_tasks():
    asyncio.create_task(send_leaderboard_weekly())
    asyncio.create_task(get_top_agent_this_week())
    asyncio.create_task(send_monthly_contest())
