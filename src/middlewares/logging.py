import time
import sys
from loguru import logger
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

# Set up Loguru logging (log to file and console)
logger.add("logs/bot_logs.log", rotation="1 day",
           retention="7 days", compression="zip", level="INFO")
# logger.add(sys.stdout, level="INFO")  # Logs to the console as well


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Get the start time to calculate response time
        start_time = time.time()

        # Track the message endpoint (command or text)
        endpoint = event.text if event.text else "Non-command message"
        user_info = f"{event.from_user.username} ({event.from_user.id})"

        # Log the incoming request
        logger.info(f"📩 Incoming request: {endpoint} from {user_info}")

        # Process the update by calling the next handler
        result = await handler(event, data)

        # Calculate the response time
        response_time = time.time() - start_time

        # Log the response time and the endpoint
        logger.info(
            f"✅ Response sent for endpoint: {endpoint} in {response_time:.2f} seconds to {user_info}")

        return result
