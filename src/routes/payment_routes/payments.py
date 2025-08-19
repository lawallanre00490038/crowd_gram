from aiogram import Router, F
from aiogram.types import Message
from src.services.payment import get_payment_status

router = Router()

@router.message(F.text == "/payment")
async def payment_status(message: Message):
    status = get_payment_status(message.from_user.id)
    await message.answer(f"Payment status: {status}")
