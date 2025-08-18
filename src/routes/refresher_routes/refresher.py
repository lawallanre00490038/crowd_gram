from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(lambda msg: msg.text.lower() == "replay video")
async def replay_video(message: Message):
    await message.answer("🎥 Here's the video again: https://youtu.be/yourvideo")




