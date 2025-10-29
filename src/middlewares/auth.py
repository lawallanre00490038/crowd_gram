from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
from src.config import ADMIN_IDS


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and event.from_user.id in ADMIN_IDS:
            return await handler(event, data)
        return
