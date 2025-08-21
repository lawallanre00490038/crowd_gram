import asyncio
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states.test_knowledge import TestKnowledge
from src.keyboards.inline import create_task_ready_keyboard
from src.utils.downloader import download_telegram
from src.services.quality_assurance.audio_validation import validate_audio_input
from src.services.quality_assurance.audio_parameter_check import TaskParameterModel
from src.utils.test_knowledge import load_json_file
import os
from pathlib import Path
import random


# Load test_your_knowledge audio quiz data
audio_quiz_data = load_json_file(Path("src/data/audio_quiz.json"))  
audio_tasks = random.sample(audio_quiz_data, 2)

async def send_audio_question(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data.get("current_aq", 0)
    target_lang = data.get("target_language", "Yoruba")

    if not audio_quiz_data:
        await message.answer("❌ No audio quiz data available")
        return
    if q_index >= len(audio_tasks):
        await message.answer("❌ Audio question index out of range")
        return

    selected = audio_tasks[q_index]
    await message.answer(
        f"🎧 Theme: {selected['theme']}\n\n"
        f"📋 Instruction: {selected['instruction']}\n"
        f"💡 Example guidance: {selected['example_prompt']}\n\n"
        f"Please send a **voice note or audio file** in **{target_lang}** (10–20 seconds)."
    )
    await state.set_state(TestKnowledge.audio_quiz_submission)

async def run_audio_validation_and_respond(message: Message, state: FSMContext):
    bot: Bot = message.bot
    try:
        # Extract the file_id depending on what user sent
        if message.voice:
            file_id = message.voice.file_id
            filename = f"voice_{file_id}.oga"
        elif message.audio:
            file_id = message.audio.file_id
            # keep the original extension if available
            guessed_ext = os.path.splitext(message.audio.file_name or "")[1] or ".oga"
            filename = f"audio_{file_id}{guessed_ext}"
        else:
            await message.answer("❌ Please send a voice or audio file.")
            return

        # call helper
        local_path = await download_telegram(file_id=file_id, bot=bot)

    except Exception as e:
        await message.answer(f"❌ Could not download your audio. Error: {e}")
        return


    params = TaskParameterModel(
        min_duration=10.0,
        max_duration=20.0,
        language="Yoruba",
        expected_format="oga",
        sample_rate=48_000,
        bit_depth=32
    )

    try:
        result = validate_audio_input(audio_path=local_path, params=params, try_enhance=params.try_enhance)
    except Exception as e:
        await message.answer(f"❌ Audio validation failed unexpectedly. Error: {e}")
        return
 

    success = result.get("success", False)
    reasons = result.get("fail_reasons", [])
    meta = result.get("metadata", {})

    summary = "✅ Approved! Your audio passed our quality checks." if success \
              else "❌ Not approved. Please fix the issues below and resend."


    details = ""
    if reasons:
        details += ("\n**Issues:**\n" + "\n".join(f"- {r}" for r in reasons))

    await message.answer(summary + ("\n\n" + details if details else ""))

    data = await state.get_data()
    q_index = data.get("current_aq", 0)
    num_aq = data.get("num_aq", 0)

    if success:
        num_aq -= 1
        if num_aq > 0:
            await state.update_data(num_aq=num_aq, current_aq=q_index + 1)
            await send_audio_question(message, state)
        else:
            await asyncio.sleep(0.5)
            await message.answer("🎉 All assessments completed!\n\nClick below to access the task portal:",
                                 reply_markup=create_task_ready_keyboard())
            await state.clear()
    else:
        await message.answer("💡 Tip: Speak clearly in Yoruba for 10–20 seconds, in a quiet place.")
        await send_audio_question(message, state)
