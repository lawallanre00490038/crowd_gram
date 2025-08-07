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
def accept_support_request(chat_id):
    """Inline Keyboard with JSON string format for callback_data"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Accept", callback_data=f'{{"text": "accept","chat_id": {chat_id} }}')  # noqa: E501
                                  ],
        ]
    )