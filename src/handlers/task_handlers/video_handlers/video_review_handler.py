import logging
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import List
from src.utils.parameters import UserParams
from src.handlers.task_handlers.video_handlers.video_task_submission_handler import handle_video_submission
from src.handlers.task_handlers.audio_task_handler import handle_audio_submission
from src.utils.extract_option import extract_option
from src.routes.task_routes.task_formaters import VIDEO_SUBMISSION_RECEIVED_MESSAGE, VIDEO_REQUEST_ANNOTATION_MESSAGE
import asyncio

logger = logging.getLogger(__name__)

# --- Description Review Handler ---
async def handle_description_review(message: Message, state: FSMContext, annotation_type: str):
    """
    Review user input for video description based on required type from task_info.
    """
    data = await state.get_data()

    if annotation_type == 'text':
        if message.text:
            await message.answer("📝 Text description received. Reviewing...")
            await asyncio.sleep(3)
            # ...text review logic...
            await message.answer("✅ Text review complete.")
        else:
            await message.answer("❌ Please send a text description as required by the task.")
    elif annotation_type == 'audio':
        if message.voice or message.audio:
            await message.answer("🔊 Audio description received. Reviewing...")
            # ...audio review logic...
            # out_message = await handle_audio_submission(data.get('task_info', {}), (message.voice or message.audio).file_id, message.from_user.id, message.bot)
            # await message.answer(out_message)
            await asyncio.sleep(3)
            await message.answer("✅ Audio review complete.")
        else:
            await message.answer("❌ Please send an audio description as required by the task.")
    else:
        await message.answer("❌ Invalid description type specified in the task.")

# --- Close-Ended Review Handler ---
async def handle_closeEnd_submission(callback: CallbackQuery, options: List, answer: str):
    user_answer = callback.data
    await callback.answer()
    # Use extract_option to map callback data to the actual option
    selected_option = extract_option(user_answer, options)
    if selected_option == answer:
        await callback.message.answer('✅ Correct!')
    else:
        await callback.message.answer("❌ Incorrect. Try again:")

# --- Request Task Submission Handler ---
async def handle_request_submission(message: Message, state: FSMContext, bot, quiz):
    """
    Handles user submission for request tasks: expects a video, then a description (text or audio).
    """
    data = await state.get_data()
    theme = quiz['theme']
    annotation_type = quiz['annotation_type']
    target_lang = data.get('target_lang', 'Yoruba')

    if message.video:
        await message.answer(VIDEO_SUBMISSION_RECEIVED_MESSAGE)
        
        # out_message = await handle_video_submission(data, message.video.file_id, message.from_user.id, bot)
        # await message.answer(str(out_message))
        await asyncio.sleep(3)
        await state.update_data(video_submitted=True)
        
        video_validation_check = True # TODO: QA Team

        if video_validation_check:
            # Set state to expect description next
            await message.answer(VIDEO_REQUEST_ANNOTATION_MESSAGE.format(theme=theme, target_lang=target_lang, annotation_type=annotation_type))
            
            if message.text or message.voice or message.audio:
                # Only allow description if video has been submitted
                if data.get('video_submitted'):
                    await handle_description_review(message, state, annotation_type)
                else:
                    await message.answer("❌ Please send a video first before describing it.")
    else:
        await message.answer("Please send a video, then describe it with the required type.")


async def handle_video_task_review(message_or_callback, state: FSMContext, quiz):
    """
    Combined handler for all video task types (open-ended, close-ended, request).
    Dispatches to the correct review/handling function based on task type and input.
    Args:
        message_or_callback: Message or CallbackQuery object from aiogram
        state: FSMContext for state management (optional)
        bot: Bot instance (optional, for submission handlers)
    """
    task_type = quiz['mine_type']
    
    if task_type == 'OpenEnd':
        # Only allow text or audio as specified in task_info
        if state is not None:
            await handle_description_review(message_or_callback, state, quiz['annotation_type'])
        else:
            raise ValueError('FSMContext (state) required for openEnd task review.')
    elif task_type == 'CloseEnd':
        # message_or_callback is expected to be CallbackQuery
        options = quiz['options']
        answer = quiz['answer']
        if options is not None and answer is not None:
            await handle_closeEnd_submission(message_or_callback, options, answer)
        else:
            raise ValueError('Options and answer required for closeEnd task review.')
    elif task_type == 'request':
        # message_or_callback is expected to be Message
        if state is not None and message_or_callback.bot is not None:
            await handle_request_submission(message_or_callback, state, message_or_callback.bot, quiz)
        else:
            raise ValueError('FSMContext (state) and bot required for request task review.')
    else:
        raise ValueError('Invalid or missing task_type for video task review.')