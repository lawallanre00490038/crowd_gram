from aiogram import Router
from aiogram.types import ErrorEvent

router = Router()

@router.errors()
async def error_handler(event: ErrorEvent):
    # Log and notify
    print(f"Error: {event.exception}")
