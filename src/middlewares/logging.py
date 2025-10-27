import time
import sys
from loguru import logger
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

# Set up Loguru logging (log to file and console)
logger.add("logs/bot_logs.log", rotation="1 day",
           retention="7 days", compression="zip", level="INFO")
# logger.add(sys.stdout, level="INFO")  # Logs to the console as well


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        # Now can accept both Message and CallbackQuery
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,  # `event` can be either Message or CallbackQuery
        data: Dict[str, Any]
    ) -> Any:
        # Get the start time to calculate response time
        start_time = time.time()

        user_info = f"{event.from_user.username} ({event.from_user.id})"

        if isinstance(event, Message):
            # Handle Message
            endpoint = event.text if event.text else "Non-command message"
            logger.info(f"📩 Incoming message: {endpoint} from {user_info}")
        elif isinstance(event, CallbackQuery):
            # Handle CallbackQuery
            endpoint = event.data if event.data else "Non-command callback"
            logger.info(f"📩 Incoming callback: {endpoint} from {user_info}")
        else:
            # Unknown event type
            logger.warning(f"Unknown event type: {type(event)}")
            return await handler(event, data)

        # Process the update by calling the next handler
        result = await handler(event, data)

        # Calculate the response time
        response_time = time.time() - start_time

        # Log the response time and the endpoint
        if isinstance(event, Message):
            logger.info(
                f"✅ Response sent for message: {endpoint} in {response_time:.2f} seconds to {user_info}")
        elif isinstance(event, CallbackQuery):
            logger.info(
                f"✅ Response sent for callback: {endpoint} in {response_time:.2f} seconds to {user_info}")

        return result
