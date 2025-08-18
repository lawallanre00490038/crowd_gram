from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    # Admin dashboard logic
    await message.answer("Welcome to the admin dashboard.")
