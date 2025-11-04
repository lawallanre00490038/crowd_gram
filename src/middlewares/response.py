import time
import psutil
import asyncio
from loguru import logger
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Update


class ResponseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        # Now can accept both Message and CallbackQuery
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,  # `event` can be either Message or CallbackQuery
        data: Dict[str, Any]
    ) -> Any:
        # Get the start time to calculate response time
        start_time = time.time()

        # Process the update by calling the next handler
        await event.message.edit_reply_markup(reply_markup=None)

        resp = ""
        for mk_keys in event.message.reply_markup:
            _, mk_keys = mk_keys
            for mk_key in mk_keys:
                for mkk in mk_key:
                    if mkk.callback_data == event.data:
                        resp = mkk.text
        resp_text = event.message.text + f"\nResponse: {resp}"

        await event.message.edit_text(resp_text)

        result = await handler(event, data)
        return result
