from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states.onboarding import Onboarding
from src.keyboards.reply import onboarding_kb, gender_kb, task_type_kb

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "👋 Welcome! Let's get you onboarded.\n\n"
        "🎥 Please watch this short video to understand how data collection works:\n"
        "👉 https://youtu.be/FSV1uAMbYqM?list=PLeBirUGntTt1TGeuP3xQX9ZbpeGSdbmzm"
    )
    
    await message.answer(
        "🧠 Once you've watched the video, reply *'done'* to start the short quiz.",
        reply_markup=None
    )
    await state.set_state(Onboarding.intro)

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
