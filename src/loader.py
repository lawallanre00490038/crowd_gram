from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession, TCPConnector
from src.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

def create_bot():
    connector = TCPConnector(limit=50, limit_per_host=50, ttl_dns_cache=300)
    # session = AiohttpSession(connector=connector, timeout=60)
    
    dp = Dispatcher()
    return bot, dp



# dp = Dispatcher(storage=MemoryStorage())
