from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from src.data.video_tutorials import tutorial_videos


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


def tutorial_choice_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📺 Yes, show me the tutorials", callback_data="tutorial_yes")],
            [InlineKeyboardButton(text="⏭️ Skip tutorials", callback_data="skip_tutorials")]
        ]
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
            [InlineKeyboardButton(text="Accept", callback_data=f'{{"text": "accept","user_id": {chat_id} }}')  # noqa: E501
                                  ],
        ]
    )

user_type_kb = InlineKeyboardMarkup(
        inline_keyboard=[

            [InlineKeyboardButton(text="👤 Sign In", callback_data="registered_yes")],
            [InlineKeyboardButton(text="🆕 Sign Up", callback_data="new_user")],
           # [InlineKeyboardButton(text="🔙 Back to tutorials", callback_data="back_to_tutorials")]
        ]
    )

ready_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="👍Yes, I'm ready", callback_data="quiz_yes")],
                [InlineKeyboardButton(text="🔁No, show again", callback_data="quiz_no")],
                [InlineKeyboardButton(text="⏭️Skip Quiz", callback_data="skip_quiz")]
            ]
        )


def create_ready_button():
   
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yes I'm ready!", callback_data="ready_start")]
        ]
    )


def create_task_ready_keyboard():
    
    return InlineKeyboardMarkup(
         inline_keyboard=[
            [InlineKeyboardButton(text="✅ I understand, let's begin!", callback_data="begin_translation")]
        ]
    )


def create_task_action_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Start Translation", callback_data="start_translate")],
            [InlineKeyboardButton(text="Get Another Task", callback_data="get_next_task")],
        ]
    )

def create_next_task_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Next Task", callback_data="get_next_task")],
            [InlineKeyboardButton(text="Menu", callback_data="view_commands")],
        ]
    )

def yes_no_inline_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Yes", callback_data="org_yes")],
                [InlineKeyboardButton(text="❌ No", callback_data="org_no")]
            ]
        )

def create_account_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Create Account", callback_data="create_account")],
            [InlineKeyboardButton(text="🔄 Try Again", callback_data="try_login_again")]
        ]
    )


def tutorial_nav_kb(index: int):
    buttons = []
    
    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Back", callback_data="prev"))
    if index < len(tutorial_videos) - 1:
        nav_row.append(InlineKeyboardButton(text="➡️ Next Video", callback_data="next"))
    else:
        nav_row.append(InlineKeyboardButton(text="✅ Ready for Quiz", callback_data="quiz_yes"))
    
    if nav_row:
        buttons.append(nav_row)

    if index < len(tutorial_videos) - 1:
        buttons.append([InlineKeyboardButton(text="⏭️ Skip videos", callback_data="skip_videos")])  
    else:
        buttons.append([InlineKeyboardButton(text="⏭️ Skip quiz", callback_data="skip_quiz")])  
    


    return InlineKeyboardMarkup(inline_keyboard=buttons)


def retry_keyboard():
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Try Again", callback_data="retry_reg")]
    ])