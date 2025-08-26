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
from src.services.task_distributor import TranslationTask
from src.states.tasks import AudioTaskSubmission
import os
from pathlib import Path
import random
from typing import List




async def send_audio_question_test_knowledge(message: Message, state: FSMContext,audio_quiz_data:List, audio_tasks:list):
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






async def send_audio_question_actual_tasks(
    message: Message,
    state: FSMContext,
    *,
    task: TranslationTask,                 # <-- Pydantic model for actual tasks
    state_key_task_id: str = "current_task_id",
    state_key_target_lang: str = "target_language",
    default_duration_text: str = "10–20 second",
    show_meta: bool = True,                  # include reward/deadline line in the prompt
) -> None:
    """
    Send a single assigned audio task prompt (actual tasks only).
    """
    await state.update_data(
        **{
            state_key_task_id: task.task_id,
            state_key_target_lang: task.required_language or "English",
          
        }
    )

    # --- 2) Build the prompt from TranslationTask fields ---
    theme = (task.task_type or task.category or "Audio Task").strip()
    instruction = (task.task_instructions or task.task_description or "Record a short audio sample.").strip()
    description = task.task_description or "No description provided."
    language = (task.required_language or "English").strip()
    duration_text = default_duration_text

  
    if show_meta:
        bits = []
        if task.rewards:         bits.append(f"💰 Reward: {task.rewards}")
        if task.deadline:        bits.append(f"🕒 Deadline: {task.deadline}")
        if task.extend_deadline: bits.append(f"➕ Extend: {task.extend_deadline}")
        if bits:
            meta_line = "\n" + " · ".join(bits)

    # --- 3) Send the message ---
    await message.answer(
        f"🎧 Theme: {theme}\n\n"
        f"📋 Instruction: {instruction}\n"
        f"💡 Description: {description}\n"
        f"Please send a {duration_text} **voice note or audio file** in **{language}**."
    )

    # --- 4) Advance to the next state in the real-task flow ---
    await state.set_state( AudioTaskSubmission.waiting_for_audio)


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
