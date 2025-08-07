# handlers/pipeline.py

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from states import TextTaskSubmission, ImageTaskSubmission
import random

router = Router()


# MOCK TASKS FOR SELECTION
TEXT_TASKS = [
    {
        "type": "text",
        "id": "swh_translation_1",
        "label": "Translate to Swahili",
        "instructions": "Translate the following into Swahili: 'Be kind to your neighbor during difficult times.'",
        "task_lang": "Swahili",
        "task_script": "Latin"
    },
    {
        "type": "text",
        "id": "amharic_translation_1",
        "label": "Translate to Amharic",
        "instructions": "Translate the following into Amharic: 'Support your friend when they lose their job.'",
        "task_lang": "Amharic",
        "task_script": "Ethiopic"
    },
    {
        "type": "text",
        "id": "yoruba_quote",
        "label": "Write a motivational quote in Yoruba",
        "instructions": "Write an original motivational quote in Yoruba (at least 10 words).",
        "task_lang": "Yoruba",
        "task_script": "Latin"
    },
    {
        "type": "text",
        "id": "hausa_advice",
        "label": "Give advice in Hausa",
        "instructions": "Provide one piece of life advice in Hausa (no English words).",
        "task_lang": "Hausa",
        "task_script": "Latin"
    },
    {
        "type": "text",
        "id": "swh_experience",
        "label": "Describe your market visit (in Swahili)",
        "instructions": "Briefly describe your last visit to a local market using Swahili only.",
        "task_lang": "Swahili",
        "task_script": "Latin"
    },
    {
        "type": "text",
        "id": "amharic_story",
        "label": "Short story in Amharic",
        "instructions": "Write a short story (2–3 sentences) in Amharic. Avoid using English words.",
        "task_lang": "Amharic",
        "task_script": "Ethiopic"
    },
    {
        "type": "text",
        "id": "yoruba_instructions",
        "label": "Give directions in Yoruba",
        "instructions": "In Yoruba, give directions from your home to a nearby school.",
        "task_lang": "Yoruba",
        "task_script": "Latin"
    }
]

IMAGE_TASKS = [
    {
        "type": "image",
        "id": "street_vendor",
        "label": "Photo of a street vendor",
        "instructions": "Take or upload a clear photo of a street vendor operating in a public place (e.g., roadside or market).",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "local_meal",
        "label": "Photo of a local meal",
        "instructions": "Take a photo of a traditional/local dish before eating it. Ensure the image is well-lit and not blurry.",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "public_signboard",
        "label": "Capture a public signboard",
        "instructions": "Take a photo of any signboard written in a local language (e.g., shop signs, road signs, public notices).",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "market_scene",
        "label": "Busy market scene",
        "instructions": "Take or upload a photo showing a busy marketplace with at least 3 visible people or stalls.",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "school_gate",
        "label": "School entrance gate",
        "instructions": "Take a photo of a school gate or entrance signboard. Make sure the school name is visible.",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "public_transport",
        "label": "Public transport in motion",
        "instructions": "Capture a public transport vehicle (bus, keke, bodaboda, taxi, etc.) in use. Try to avoid motion blur.",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "street_art",
        "label": "Local graffiti or mural",
        "instructions": "Photograph a piece of street art, graffiti, or a wall mural in your area. Capture the full design if possible.",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "workspace_desk",
        "label": "Your study or work desk",
        "instructions": "Take a photo of your current workspace (desk, table, etc.). Ensure it's tidy and clearly visible.",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "morning_view",
        "label": "View outside in the morning",
        "instructions": "Take a photo from your home or compound early in the morning (before 9am). Try to include the sky.",
        "task_lang": None,
        "task_script": None
    },
    {
        "type": "image",
        "id": "local_product",
        "label": "Local product or handmade item",
        "instructions": "Take a clear photo of a locally-made product (clothing, food item, craft, etc.) sold in your area.",
        "task_lang": None,
        "task_script": None
    }

]
TASKS = TEXT_TASKS + IMAGE_TASKS

def ready_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ I'm ready", callback_data="ready:start")]]
    )

# Entry point: show button
@router.message(Command("task"))
async def start_pipeline(message: types.Message, state: FSMContext):
    await message.answer("👋 Are you ready to begin your assigned task?", reply_markup=ready_keyboard())

# /next command: assign task immediately
@router.message(Command("next"))
async def next_task(message: types.Message, state: FSMContext):
    await assign_and_send_task(message=message, state=state, show_keyboard=False)

# Inline button click: show task after "I'm ready"
@router.callback_query(lambda c: c.data == "ready:start")
async def assign_task(callback: CallbackQuery, state: FSMContext):
    await assign_and_send_task(message=callback.message, state=state, show_keyboard=True)
    await callback.answer()


# Shared function for assigning and sending task
async def assign_and_send_task(message: types.Message, state: FSMContext, show_keyboard: bool = False):
    task = random.choice(TASKS)

    await state.update_data(
        task_id=task["id"],
        task_label=task["label"],
        task_type=task["type"],
        task_instructions=task["instructions"],
        
        task_lang=task["task_lang"].upper() if task["task_lang"] else None,
        task_script=task["task_script"] if task["task_script"] else None
    )

    msg = f"🔔 **Task Assigned:** {task['label']}\n\n📌 *Instructions:* {task['instructions']}"

    if task["type"] == "text":
        await state.set_state(TextTaskSubmission.waiting_for_text)
    else:
        await state.set_state(ImageTaskSubmission.waiting_for_image)

    await message.answer(msg, parse_mode="Markdown")