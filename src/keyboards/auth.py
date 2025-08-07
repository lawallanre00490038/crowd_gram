from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def organization_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Yes, I'm part of an organization")],
            [KeyboardButton(text="❌ No /❓ I don't know")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def company_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="OpenAI")],
            [KeyboardButton(text="EqualyzAI")],

            [KeyboardButton(text="Google")],
            [KeyboardButton(text="Meta")],
            [KeyboardButton(text="Anthropic")],

            [KeyboardButton(text="African Voices")],

            [KeyboardButton(text="Microsoft")],
            [KeyboardButton(text="HausaNLP")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

