# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# onboarding_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="Start Quiz")],
#     ],
#     resize_keyboard=True
# )




from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

onboarding_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Let's begin")]],
    resize_keyboard=True
)

gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Male"), KeyboardButton(text="Female")],
        [KeyboardButton(text="Prefer not to say")]
    ],
    resize_keyboard=True
)

task_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Text annotation"), KeyboardButton(text="Voice recording")],
        [KeyboardButton(text="Image tagging"), KeyboardButton(text="Translation")]
    ],
    resize_keyboard=True
)
