from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.models.company_models import CompanyInfo
from src.services.server.getters_api import get_companies_from_api, get_countries_from_api

def organization_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Yes, I'm part of an organization")],
            [KeyboardButton(text="❌ No /❓ I don't know")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def company_kb():
    parsed_users = await get_companies_from_api()
    
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=info.name)] 
                  for info in parsed_users],
        resize_keyboard=True,
        one_time_keyboard=True
    )

