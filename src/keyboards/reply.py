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
        [KeyboardButton(text="📝Text")],
        [KeyboardButton(text="🎤Audio")]
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


age_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="18-30")],
        [KeyboardButton(text="31-40")],
        [KeyboardButton(text="41-50")],
        [KeyboardButton(text="51-60")],
        [KeyboardButton(text="51-70")],
        [KeyboardButton(text="71-80")],
        [KeyboardButton(text="81-90")],
        [KeyboardButton(text="91-100")]

    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


# Éducation
education_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="High School Diploma"), KeyboardButton(text="Bachelor's Degree")],
        [KeyboardButton(text="Master's Degree"), KeyboardButton(text="Doctorate Degree")],
        [KeyboardButton(text="SSCE/WAEC"), KeyboardButton(text="Other")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


writing_ability_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Good")],
        [KeyboardButton(text="Not so good")], 
        [KeyboardButton(text="Very good (with all the tonal marks)")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


phone_quality_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Fair"), KeyboardButton(text="Good")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


favourite_speaker_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Alexa"), KeyboardButton(text="DJ")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

 

