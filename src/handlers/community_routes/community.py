from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/leaderboard")
async def leaderboard(message: Message):
    # Fetch and display leaderboard
    await message.answer("This week's leaderboard: ...")
