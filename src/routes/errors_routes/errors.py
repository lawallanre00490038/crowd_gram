from loguru import logger
from aiogram import Router
from aiogram.types import ErrorEvent

router = Router()


@router.errors()
async def error_handler(event: ErrorEvent):
    # Log and notify
    logger.trace(f"Error: {event.exception}")
