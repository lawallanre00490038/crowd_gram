from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states.onboarding import Onboarding
from src.states.authentication import Authentication
from src.keyboards.reply import gender_kb, task_type_kb, industry_kb, primary_device_kb, dialect_fluency_kb
from src.keyboards.inline import g0_to_tutorials_kb
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from src.handlers.onboarding_routes.quiz import start_quiz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


router = Router()

tutorial_videos = [
    "🎥 Video 1: Introduction to Data Collection\nhttps://youtu.be/FSV1uAMbYqM?list=PLeBirUGntTt1TGeuP3xQX9ZbpeGSdbmzm",
    "🎥 Video 2: How Annotation Works\nhttps://youtu.be/FSV1uAMbYqM?list=PLeBirUGntTt1TGeuP3xQX9ZbpeGSdbmzm",
    "🎥 Video 3: Quality and Submission Guide\nhttps://youtu.be/FSV1uAMbYqM?list=PLeBirUGntTt1TGeuP3xQX9ZbpeGSdbmzm"
]


# --- Custom tutorial states ---
class Tutorial(StatesGroup):
    ready_to_start = State()
    watching = State()



@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    #verification user exist??
    welcome_text=(    
            "👋 Welcome to Equalyz Crowd!\n\n"
            "We're building the future of AI by collecting multilingual data across Africa.\n\n"
            "As a contributor/agent, you'll help train AI models and earn money for quality work.\n\n"
            "This quick onboarding sets up your profile so we can match you with the best tasks.\n\n"
            "Let’s begin! 🚀"
        )
    await message.answer(welcome_text)
    
    await message.answer(
            "🧠 You will be guided through a series of videos to learn about the basics of data collection and annotation.\n\n",
         reply_markup=g0_to_tutorials_kb()
        )
    await state.set_state(Tutorial.ready_to_start)



@router.callback_query(Tutorial.ready_to_start, F.data == "tutorial_yes")
async def start_tutorial_sequence(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(tutorial_index=0)
    await state.set_state(Tutorial.watching)
    await send_tutorial(callback.message, state)



# --- Navigation buttons ---
def tutorial_nav_kb(index: int):
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Back", callback_data="prev"))
    if index < len(tutorial_videos) - 1:
        buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data="next"))
    else:
        buttons.append(InlineKeyboardButton(text="✅ Ready for Quiz", callback_data="ready"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


# --- Send tutorial video ---
async def send_tutorial(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data.get("tutorial_index", 0)
    await message.answer(tutorial_videos[index], reply_markup=tutorial_nav_kb(index))


# --- Handle navigation (next/back/ready) ---
@router.callback_query(Tutorial.watching, F.data.in_(["next", "prev", "ready"]))
async def tutorial_navigation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    index = data.get("tutorial_index", 0)

    if callback.data == "next" and index < len(tutorial_videos) - 1:
        index += 1
        await state.update_data(tutorial_index=index)
        await send_tutorial(callback.message, state)

    elif callback.data == "prev" and index > 0:
        index -= 1
        await state.update_data(tutorial_index=index)
        await send_tutorial(callback.message, state)

    elif callback.data == "ready":
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="👍 Yes, I'm ready", callback_data="quiz_yes"),
                InlineKeyboardButton(text="🔁 No, show again", callback_data="quiz_no")
            ]]
        )
        await callback.message.answer("Have you finished watching all the videos?\nStart quiz now?", reply_markup=kb)


# --- Handle yes/no response ---
@router.callback_query(Tutorial.watching, F.data.in_(["quiz_yes", "quiz_no"]))
async def quiz_ready_response(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "quiz_yes":
        await callback.message.answer("✅ Great! Let's begin the short quiz.")
        await state.set_state(Onboarding.intro)
        await start_quiz(callback.message, state)

    elif callback.data == "quiz_no":
        await state.update_data(tutorial_index=0)
        await send_tutorial(callback.message, state)
        



# --- Collect location ---
@router.message(Onboarding.location)
async def get_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text.strip())
    #phone number already collected from authentification
    await message.answer("⚧ What’s your gender? Your privacy is protected - this data is never shared publicly.", reply_markup=gender_kb)
    await state.set_state(Onboarding.gender)


# --- Collect phone number ---
#@router.message(Onboarding.phone)
#async def get_phone(message: Message, state: FSMContext):
   # await state.update_data(phone=message.text.strip())
    

# --- Collect gender ---
@router.message(Onboarding.gender)
async def get_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text.strip())
    await message.answer("🗣️ Please list the languages or dialects you speak fluently (e.g., English, French, Yoruba, Fulfulde, Gungbe...).")
    await state.set_state(Onboarding.languages)

    
# --- Collect spoken languages ---
@router.message(Onboarding.languages)
async def get_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text.strip())
    dialect_text = (
        "🗣️ How well do you speak your local language or dialect?\n\n"
        "Many of our tasks involve local languages, so this is very valuable!\n\n"
        "Rate your fluency:"
    )
    await message.answer(dialect_text, reply_markup=dialect_fluency_kb)
    await state.set_state(Onboarding.dialect_fluency)

# --- Dialect Fluency ---
@router.message(Onboarding.dialect_fluency)
async def get_dialect_fluency(message: Message, state: FSMContext):
    await state.update_data(dialect_fluency=message.text.strip())
    await message.answer("🎓 What's your highest level of education? "\
    "Examples: High School, Bachelor's Degree, Master's, PhD, Technical Diploma...")
    await state.set_state(Onboarding.education)

# --- Education ---
@router.message(Onboarding.education)
async def get_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text.strip())
    industry_text=(
        "💼 What field do you work in or have experience with?\n\n"
        "Choose the option that best describes you:"
    )
    await message.answer(industry_text, reply_markup = industry_kb)
    await state.set_state(Onboarding.industry)

# --- Industry ---
@router.message(Onboarding.industry)
async def get_industry(message: Message, state: FSMContext):
    await state.update_data(industry=message.text.strip())
    device_text = (
        "📱 What device do you mainly use for work and internet?\n\n"
        "Select your primary device:"
    )
    await message.answer(device_text, reply_markup=primary_device_kb)
    await state.set_state(Onboarding.primary_device)


# --- Primary Device ---
@router.message(Onboarding.primary_device)
async def get_primary_device(message: Message, state: FSMContext):
    await state.update_data(primary_device=message.text.strip())
    await message.answer("📌 What types of tasks would you like to work on?", reply_markup=task_type_kb)
    await state.set_state(Onboarding.task_type)


# --- Task preferences ---
@router.message(Onboarding.task_type)
async def get_task_type(message: Message, state: FSMContext):
    await state.update_data(task_type=message.text.strip())
    await message.answer("🤝 Referral Code (Optional)\n\n" 
    "Were you invited by another contributor?\n\n"
    "If yes, please enter their referral code;" 
    "If none, just type 'none'"
    )
    await state.set_state(Onboarding.referrer)

  
# --- Referrer ---
@router.message(Onboarding.referrer)
async def get_referrer(message: Message, state: FSMContext):
    await state.update_data(referrer=message.text.strip())
   
    user_data = await state.get_data()
    # Here you would save to your DB
    await message.answer("🎉 Thank you! You're now onboarded and ready for tasks.\n\n" \
    "Welcome to the EqualyzAI contributor community! 🌟")

    # Set agent status to 'Pending' and notify admin optionally
    # Trigger next stage (demo task, eligibility test, etc.)
    print(message.from_user.id, "has completed onboarding with data:", user_data)
    await message.answer(
        "📝 Your profile:\n"
        f"Name: {user_data['name']}\n"
        f"Phone: {user_data['phone']}\n"
        f"Gender: {user_data['gender']}\n"
        f"Location: {user_data['location']}\n"
        f"Languages: {user_data['languages']}\n"
        f"Dialect Fluency: {user_data['dialect_fluency']}\n"
        f"Education: {user_data['education']}\n"
        f"Industry: {user_data['industry']}\n"
        f"Primary Device: {user_data['primary_device']}\n"
        #f"Internet Quality: {user_data['internet_quality']}\n"
        f"Task Type: {user_data['task_type']}\n"
        f"Referrer: {user_data['referrer']}"
    )  
    await state.clear()
    
    #diriger vs test acknowledgement
    await message.answer("🎉 Thank you! You're now onboarded and ready for tasks.\n\n" \
"Welcome to the Equalyz Crowd contributor community! 🌟")

    await message.answer(
        "🧠 Next Step: Knowledge Assessment\n\n"
        "Before you start earning, we'll test your knowledge with a few practical tasks:\n"
        "• 📝 Text annotation\n"
        "• 🎵 Audio transcription\n" 
        "• 🖼️ Image classification\n"
        "• 🎥 Video analysis\n\n"
        "This helps us assign you the right tasks for your skill level!\n\n"
    )