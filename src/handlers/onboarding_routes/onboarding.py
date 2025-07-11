from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states.onboarding import Onboarding
from src.keyboards.reply import gender_kb, task_type_kb
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
    await message.answer(
        "👋 Welcome! Let's get you onboarded.\n\n"
    )
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
        




# --- Collect name ---
@router.message(Onboarding.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("📱 What's your phone number?")
    await state.set_state(Onboarding.phone)


# --- Collect phone number ---
@router.message(Onboarding.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await message.answer("⚧ What’s your gender?", reply_markup=gender_kb)
    await state.set_state(Onboarding.gender)


# --- Collect gender ---
@router.message(Onboarding.gender)
async def get_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text.strip())
    await message.answer("🌍 What's your current location?")
    await state.set_state(Onboarding.location)


# --- Collect location ---
@router.message(Onboarding.location)
async def get_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text.strip())
    await message.answer("🗣️ Which languages or dialects do you speak?")
    await state.set_state(Onboarding.languages)


# --- Collect spoken languages ---
@router.message(Onboarding.languages)
async def get_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text.strip())
    await message.answer("🎓 What's your highest level of education?")
    await state.set_state(Onboarding.education)


# --- Education ---
@router.message(Onboarding.education)
async def get_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text.strip())
    await message.answer("📌 What types of tasks would you like to work on?", reply_markup=task_type_kb)
    await state.set_state(Onboarding.task_type)


# --- Task preferences ---
@router.message(Onboarding.task_type)
async def get_task_type(message: Message, state: FSMContext):
    await state.update_data(task_type=message.text.strip())
    await message.answer("💡 Do you have a referral code? (If none, type 'none')")
    await state.set_state(Onboarding.referrer)


# --- Referrer ---
@router.message(Onboarding.referrer)
async def get_referrer(message: Message, state: FSMContext):
    await state.update_data(referrer=message.text.strip())

    user_data = await state.get_data()
    # Here you would save to your DB
    await message.answer("🎉 Thank you! You're now onboarded and ready for tasks.")

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
        f"Education: {user_data['education']}\n"
        f"Task Type: {user_data['task_type']}\n"
        f"Referrer: {user_data['referrer']}"
    )
    
    await state.clear()
