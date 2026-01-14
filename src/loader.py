from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.fsm.storage.memory import MemoryStorage
from motor.motor_asyncio import AsyncIOMotorClient  # async MongoDB driver
from src.config import BOT_TOKEN, MONGO_DB_URI, MONGODB_DB_NAME, USE_MONGO_DB


import asyncio
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

# Initialize bot
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

# MongoDB FSM storage
async def create_bot():
    logger.trace(USE_MONGO_DB)
    if USE_MONGO_DB:
        # Initialize MongoDB client
        mongo_client = AsyncIOMotorClient(MONGO_DB_URI)

        # Create FSM storage using aiogram-mongodb
        storage = MongoStorage(
            client=mongo_client,
            db_name=MONGODB_DB_NAME,
            collection_name="fsm_states",  # Optional collection name
        )
        logger.info("Using MongoDB Storage")

    else:
        logger.info("Using In Memory Storage")
        storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    return bot, dp







class TelegramLoader:
    def __init__(self, message: Message, text: str = "Processing"):
        self.message = message
        self.text = text
        self.task = None
        self.loading_msg = None

    async def _animate(self):
        frames = ["(.  )", "(.. )", "(...)"]
        i = 0
        try:
            while True:
                frame = frames[i % len(frames)]
                # Update the message with the current frame
                await self.loading_msg.edit_text(f"⏳ {self.text} {frame}")
                i += 1
                await asyncio.sleep(0.6) # Safe rate limit for Telegram
        except asyncio.CancelledError:
            pass # Task was stopped
        except TelegramBadRequest:
            pass # Message was likely deleted or not changed

    async def __aenter__(self):
        """Starts the animation when entering 'async with'"""
        self.loading_msg = await self.message.answer(f"⏳ {self.text} (...)")
        self.task = asyncio.create_task(self._animate())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stops the animation when exiting 'async with'"""
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        # Final update to the message
        if exc_type is None:
            await self.loading_msg.edit_text(f"✅ {self.text} Complete!")
        else:
            await self.loading_msg.edit_text(f"❌ {self.text} Failed.")