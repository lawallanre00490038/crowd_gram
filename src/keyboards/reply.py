# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# onboarding_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="Start Quiz")],
#     ],
#     resize_keyboard=True
# )


   

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

onboarding_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚀 Let's begin")]],
    resize_keyboard=True
)

gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="♂️ Male"), KeyboardButton(text=" ♀️ Female")],
        [KeyboardButton(text=" 🙈 Prefer not to say")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

task_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝Text annotation"), KeyboardButton(text="🎤 Voice recording")],
        [KeyboardButton(text="🖼️ Image tagging"), KeyboardButton(text="🌐 Translation")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

industry_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Education")],
        [KeyboardButton(text="Engineering")],
        [KeyboardButton(text="Farming")],
        [KeyboardButton(text="Governance")],
        [KeyboardButton(text="Health")],
        [KeyboardButton(text="Security")],
        [KeyboardButton(text="Technology")],
        [KeyboardButton(text="Telecommunication")]

    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

primary_device_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Smartphone only")],
        [KeyboardButton(text="💻 Computer/Laptop only")],
        [KeyboardButton(text="📱💻 Both smartphone and computer")],
        [KeyboardButton(text="📱 Tablet")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Keyboard pour la fluency des dialectes
dialect_fluency_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌟 Native speaker")],
        [KeyboardButton(text="🔥 Fluent")],
        [KeyboardButton(text="💬 Conversational")],
        [KeyboardButton(text="📖 Basic understanding")],
        [KeyboardButton(text="❌ Not applicable")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

internet_quality_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Very good (Fast, reliable)")],
        [KeyboardButton(text="✅ Good (Mostly stable)")],
        [KeyboardButton(text="⚠️ Fair (Sometimes slow)")],
        [KeyboardButton(text="❌ Poor (Often disconnects)")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
) 
