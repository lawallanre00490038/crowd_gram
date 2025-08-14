from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.data.country import COUNTRIES
from src.data.country_state import COUNTRY_STATES
from src.data.language_dialect import LANGUAGE_DIALECTS


def create_countries_keyboard_reply(page: int = 0, columns: int = 3, rows: int = 5):

    # Calculate pagination parameters
    items_per_page = columns * rows
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(COUNTRIES))
    page_countries = COUNTRIES[start_idx:end_idx]
    
    # Create country buttons grid
    keyboard = []
    for row_idx in range(0, len(page_countries), columns):
        row = page_countries[row_idx:row_idx + columns]
        keyboard.append([KeyboardButton(text=country) for country in row])
    
    # Add navigation buttons
    navigation_row = []
    total_pages = (len(COUNTRIES) + items_per_page - 1) // items_per_page
    
    # Previous button
    if page > 0:
        navigation_row.append(KeyboardButton(text="⬅️ Previous"))
    
    # Page indicator
    navigation_row.append(KeyboardButton(text=f"📄 {page+1}/{total_pages}"))
    
    # Next button
    if end_idx < len(COUNTRIES):
        navigation_row.append(KeyboardButton(text="Next ➡️"))
    
    if navigation_row:
        keyboard.append(navigation_row)
    
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def create_states_keyboard(country: str, columns: int = 2):
    """
    Create keyboard for states/regions of a specific country
    """
    # Récupérer les états du pays, ou utiliser "Other" par défaut
    #states = COUNTRY_STATES.get(country, COUNTRY_STATES["Other"])
    states = COUNTRY_STATES.get(country, [])
    if not states:
        states = ["Other"]
    
    # Créer le clavier avec les états
    keyboard = []
    for i in range(0, len(states), columns):
        row = states[i:i + columns]
        keyboard.append([KeyboardButton(text=state) for state in row])

    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    ) 


def create_dialect_keyboard(language: str, columns: int = 2):
    """
    Create keyboard for dialects of a specific language
    """
    # Récupérer les dialectes de la langue
    dialects = LANGUAGE_DIALECTS.get(language, ["Not listed here"])
    
    # Créer le clavier avec les dialectes
    keyboard = []
    for i in range(0, len(dialects), columns):
        row = dialects[i:i + columns]
        keyboard.append([KeyboardButton(text=dialect) for dialect in row])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


