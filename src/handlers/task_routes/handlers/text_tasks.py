# handlers/text_tasks.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command
from states import TextTaskSubmission
from db.mongo import submissions
from .qa_text_validation import validate_text_input

router = Router()


@router.callback_query(lambda c: c.data.startswith("text:"))
async def on_text_task_selected(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Please enter your text:")
    await state.set_state(TextTaskSubmission.waiting_for_text)
    await state.update_data(task_id=callback.data.split(":")[1])
    await callback.answer()

@router.message(StateFilter(TextTaskSubmission.waiting_for_text))
async def handle_text_input(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()

    task_id = data.get("task_id")
    task_lang = data.get("task_lang", "en")
    task_script = data.get("task_script", "LATIN").upper()
    user_id = message.from_user.id

    result = validate_text_input(text, task_lang=task_lang,exp_task_script=task_script)

    if result["success"]:
        await message.answer("Submission Passed.\n\nTo get the next task, type /next.")        
        await submissions.insert_one({
            "user_id": user_id,
            "task": f"Text task ({task_id})",
            "text": text,
            "type": "text",
            "status": "submitted"
        })
        await state.clear()
    else:
        await message.answer(
            "Your submission has some issues:\n\n" +
            "\n".join(f"• {reason}" for reason in result["fail_reasons"])
        )
