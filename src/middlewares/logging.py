import time
import psutil
import asyncio
from loguru import logger
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Update
import os

logs_folder = os.getenv("LOGS_FOLDER", "log")
print(f"Logs will be stored in: {logs_folder}")

# Set up Loguru logging (log to file and console)
logger.add(f"{logs_folder}/bot_logs.log", rotation="1 day",
           retention="7 days", compression="zip", level="INFO")
logger.add(f"{logs_folder}/trace.log", rotation="1 day",
           retention="1 days", compression="zip", level="TRACE")
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
        start_time = time.perf_counter()

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

        logger.debug(f"Processing endpoint: {endpoint}")
        # Process the update by calling the next handler
        result = await handler(event, data)

        logger.trace(f"Result of processing: {result}")

        # Calculate the response time
        response_time = time.perf_counter() - start_time

        # Log the response time and the endpoint
        if isinstance(event, Message):
            logger.info(
                f"✅ Response sent for message: {endpoint} to {user_info} [Latency] {response_time*1000:.2f} ms")
        elif isinstance(event, CallbackQuery):
            logger.info(
                f"✅ Response sent for callback: {endpoint} to {user_info} [Latency] {response_time*1000:.2f} ms")

        return result


async def monitor_resources(interval=5):
    process = psutil.Process()
    while True:
        cpu = process.cpu_percent()
        mem = process.memory_info().rss / (1024 ** 2)
        logger.trace(f"[Resources] CPU: {cpu:.2f}% | Memory: {mem:.2f} MB")
        await asyncio.sleep(interval)
