from typing import List
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.services.server.getters_api import get_countries_from_api, get_region_from_api, get_states_from_api
from src.keyboards.reply import task_type_kb 



async def create_countries_keyboard_reply_api(page: int = 0, columns: int = 3, rows: int = 5) -> ReplyKeyboardMarkup:
    
    countries = await get_countries_from_api()
    countries = [i.country for i in countries]
    # Pagination (3x5 = 15 )
    items_per_page = columns * rows
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(countries))
    page_countries = countries[start_idx:end_idx]
    

    buttons = []
    for i in range(0, len(page_countries), columns):
        row = page_countries[i:i + columns]
        button_row = [KeyboardButton(text=country) for country in row]
        buttons.append(button_row)

    navigation_row = []
    total_pages = (len(countries) + items_per_page - 1) // items_per_page
    
    # Previous button
    if page > 0:
        navigation_row.append(KeyboardButton(text="⬅️ Previous"))
    
    # Page indicator
    navigation_row.append(KeyboardButton(text=f"📄 {page+1}/{total_pages}"))
    
    # Next button
    if end_idx < len(countries):
        navigation_row.append(KeyboardButton(text="Next ➡️"))
    
    if navigation_row:
        buttons.append(navigation_row)
    
    return ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True, 
        one_time_keyboard=False
    )


async def create_states_keyboard_api(states, columns: int = 2):
    states = [state.state for state in states]
    keyboard=[]
    for i in range (0, len(states), columns):
        row = states[i:i + columns]
        keyboard.append([KeyboardButton(text=state) for state in row])

    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    ) 

async def create_region_keyboard_api(regions: List[str], columns: int = 2):
    keyboard=[]
    for i in range (0, len(regions), columns):
        row = regions[i:i + columns]
        keyboard.append([KeyboardButton(text=state) for state in row])

    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    ) 

def create_data_type_keyboard_with_done():
            kb_buttons = task_type_kb.keyboard
            kb_buttons_with_done = [row[:] for row in kb_buttons]
            kb_buttons_with_done.append([KeyboardButton(text="✅ Done")])
            return ReplyKeyboardMarkup(keyboard=kb_buttons_with_done, resize_keyboard=True, one_time_keyboard=True)
    