import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from src.keyboards.inline import quiz_options_kb
from src.states.onboarding import Onboarding
from src.states.authentication import Authentication
from src.keyboards.auth import organization_kb

quiz_router = Router()

with open("src/data/quiz.json", "r") as f:
    quiz_data = json.load(f)

@quiz_router.message(Onboarding.intro)
async def start_quiz(message: Message, state: FSMContext):
    await state.update_data(current_q=0, score=0, retry_count=0)
    await send_quiz_question(message, state)


async def send_quiz_question(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data["current_q"]

    if q_index >= len(quiz_data):
        score = data.get("score", 0)
        await message.answer(f"🎉 Quiz complete! You got {score} out of {len(quiz_data)} right.")   
             
        from src.routes.onboarding_routes.onboarding import show_user_type_selection  
        await message.answer("✅ Great! Now let's continue with your setup.")
        await show_user_type_selection(message, state)
        return
    
      
    question = quiz_data[q_index]
    await message.answer(
        f"❓ {hbold(question['question'])}",
        reply_markup=quiz_options_kb(question["options"])
    )
    await state.set_state(Onboarding.quiz_answer)

@quiz_router.callback_query(Onboarding.quiz_answer)
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    user_answer = callback.data
    await callback.answer()

    data = await state.get_data()
    q_index = data["current_q"]
    retry = data.get("retry_count", 0)
    score = data.get("score", 0)

    correct_answer = quiz_data[q_index]["answer"]

    if user_answer == correct_answer:
        score += 1
        await callback.message.answer("✅ Correct!")
        await state.update_data(score=score, retry_count=0, current_q=q_index + 1)
        await send_quiz_question(callback.message, state)

    else:
        retry += 1
        await state.update_data(retry_count=retry)

        if retry >= 3:
            video = quiz_data[q_index]["video"]
            await callback.message.answer(
                f"❌ That's still incorrect.\n📽️ Here's a video to help you understand better:\n{video}"
            )

        await callback.message.answer("❌ Incorrect. Try again:")
        await send_quiz_question(callback.message, state)  # resend same question
