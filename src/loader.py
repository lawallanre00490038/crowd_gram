import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession, TCPConnector
from aiogram.fsm.storage.mongo import MongoStorage 
from aiogram.fsm.storage.memory import MemoryStorage
from motor.motor_asyncio import AsyncIOMotorClient  # async MongoDB driver
from src.config import BOT_TOKEN, MONGO_DB_URI, MONGODB_DB_NAME, USE_MONGO_DB


logger = logging.getLogger(__name__)

# Initialize bot
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

# MongoDB FSM storage
async def create_bot():
    print(USE_MONGO_DB)
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
        storage= MemoryStorage()


    dp = Dispatcher(storage=storage)

    return bot, dp