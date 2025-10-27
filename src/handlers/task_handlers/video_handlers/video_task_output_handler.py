from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from typing import List
from aiogram.utils.markdown import hbold
from src.keyboards.inline import quiz_options_kb
from aiogram.types import Message, FSInputFile
# You should define this similar to IMAGE_REQUEST_MESSAGE
from src.routes.task_routes.task_formaters import VIDEO_REQUEST_MESSAGE

# --- Utility Functions ---


def format_caption(question: str, target_lang: str, annotation_type: str) -> str:
    """
    Formats the caption for open-ended video tasks.
    """
    return f"❓{hbold(question)}\n\n Make sure to describe in {target_lang} using {annotation_type}."


# --- Handlers ---
async def handle_open_end_task(message: Message, quiz, target_lang: str):
    """
    Handles open-ended video task.
    """
    video_file = FSInputFile(quiz['video_id'])
    caption = format_caption(
        quiz['question'], target_lang, quiz['annotation_type'])
    return await message.answer_video(video=video_file, caption=caption)


async def handle_close_end_task(message: Message, video_path: str, question: str, options: list):
    """
    Handles close-ended video task: sends video, question, and options as inline keyboard.
    """
    video_file = FSInputFile(video_path)
    caption = f"❓{hbold(question)}\n\nChoose the correct option."
    # Build inline keyboard for options
    await message.answer_video(video=video_file, caption=caption, reply_markup=quiz_options_kb(options))
    logger.info("Sent close-ended video task with options.")


async def handle_request_task(message: Message, quiz, target_lang: str):
    """
    Handles video request task.
    """
    theme = quiz['theme']
    annotation_type = quiz['annotation_type']
    question = quiz['question']
    example = quiz['example_prompt']
    msg = VIDEO_REQUEST_MESSAGE.format(
        target_lang=target_lang,
        theme=theme,
        annotation_type=annotation_type,
        question=question,
        example=example
    )
    return await message.answer(msg)


async def handle_video_task(message: Message, quiz_data, target_lang: str):
    """
    Handles video task for all types.
    """
    video_task_type = quiz_data.get('mine_type')
    print(video_task_type)
    if video_task_type == "OpenEnd":
        return await handle_open_end_task(
            message,
            quiz=quiz_data,
            target_lang=target_lang
        )
    elif video_task_type == "CloseEnd":
        await handle_close_end_task(
            message,
            video_path=quiz_data['video_id'],
            question=quiz_data['question'],
            options=quiz_data['options']
        )
    elif video_task_type == "request":
        return await handle_request_task(message, quiz_data, target_lang=target_lang)
    else:
        return "❌ Invalid video task type"
