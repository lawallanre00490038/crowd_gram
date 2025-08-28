from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from typing import List
from aiogram.utils.markdown import hbold
from src.keyboards.inline import quiz_options_kb
from aiogram.types import Message, FSInputFile
from src.routes.task_routes.task_formaters import IMAGE_REQUEST_MESSAGE

logger = logging.getLogger(__name__)

# --- Utility Functions ---
def format_caption(question: str, target_lang: str) -> str:
    """
    Formats the caption for open-ended image tasks.
    """
    return f"❓{hbold(question)}\n\n Make sure to describe in {target_lang}."


# --- Handlers ---
async def handle_open_end_task(message: Message, image_path: str, question: str, target_lang: str):
    """
    Handles open-ended image task.
    """
    print("open")
    image_file = FSInputFile(image_path)
    caption = format_caption(question, target_lang)
    return await message.answer_photo(photo=image_file, caption=caption)

# --- Handlers ---
async def handle_close_end_task(message: Message, image_path: str, question: str, options: list):
    """
    Handles close-ended image task: sends image, question, and options as inline keyboard.
    """
    print("close")
    image_file = FSInputFile(image_path)
    caption = f"❓{hbold(question)}\n\nChoose the correct option."
    # Build inline keyboard for options
    await message.answer_photo(photo=image_file, caption=caption, reply_markup=quiz_options_kb(options))
    logger.info("Sent close-ended image task with options.")
    

async def handle_request_task(message: Message, quiz, target_lang: str):
    """
    Handles image request task.
    """
    print("request")
    theme = quiz['theme']
    annotation_type = quiz['annotation_type']
    question = quiz['question']
    example = quiz['example_prompt']
    msg = IMAGE_REQUEST_MESSAGE.format(
            target_lang=target_lang,
            theme=theme,
            annotation_type=annotation_type,
            question=question,
            example=example
        )    
    return await message.answer(msg)

async def handle_image_task(message: Message, quiz_data, target_lang: str):
    """
    Handles images task for all types.
    """
    print("image task")
    image_task_type = quiz_data.get('mine_type')
    print(image_task_type)
    if image_task_type == "openEnd":
        return await handle_open_end_task(
            message,
            image_path=quiz_data['image'],
            question=quiz_data['question'],
            target_lang=target_lang
        )
    elif image_task_type == "closeEnd":
        # Modular: import and call close_end_task_handler here if needed
        from . import close_end_review_handler
        await handle_close_end_task(
            message,
            image_path=quiz_data['image'],
            question=quiz_data['question'],
            options=quiz_data['options']
        )
        return await close_end_review_handler.handle_submission()
    elif image_task_type == "request":
        return await handle_request_task(message, quiz_data, target_lang=target_lang)
    else:
        return "❌ Invalid image task type"