from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Accept", callback_data="accept")],
            [InlineKeyboardButton(text="Reject", callback_data="reject")]
        ]
    )

def quiz_options_kb(options: list[str]):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=opt, callback_data=opt)] for opt in options]
    )



def g0_to_tutorials_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👍 Yes, I'm ready", callback_data="tutorial_yes")]
        ]
    )
