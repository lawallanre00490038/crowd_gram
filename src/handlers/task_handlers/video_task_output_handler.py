import logging
from typing import List
from aiogram.types import FSInputFile

from src.keyboards.inline import quiz_options_kb

logger = logging.getLogger(__name__)


async def handle_openEnd_task(video_path: str, question: str, target_lang: str):
    """
    Handles open-ended video task.

    Args:
        video_path (str): The video path.
        question (str): The task to be carried out on the video.
        target_lang (str): The translation language.
        
    Returns:
        tuple: (FSInputFile, str) -> task video file, task instruction text
    """
    video_file = FSInputFile(video_path)
    caption = f"❓ {question}\n\nMake sure to describe in {target_lang}."
    
    return video_file, caption


async def handle_closeEnd_task(video_path: str, question: str, options: List[str]):
    """
    Handles close-ended video task.

    Args:
        video_path (str): The video path.
        question (str): The task to be carried out on the video.
        options (List[str]): The list of the options to be selected from to answer the question.
    
    Returns:
        tuple: (FSInputFile, str, InlineKeyboardMarkup)
    """
    video_file = FSInputFile(video_path)
    caption = f"❓ {question}"
    keyboard = quiz_options_kb(options)
    
    return video_file, caption, keyboard


async def handle_request_task(question: str):
    """
    Handles Video request task.

    Args:
        question (str): The theme the video requested from the user needs to answer.
        
    Returns:
        str: Task instruction theme text to provide video.
    """
    return f"❓ {question}\n"
    
    
async def handle_video_task(quiz_data, video_task_type: str):
    """
    Handles video tasks for all types.

    Args:
        quiz_data (dict): Contains video task data.
        video_task_type (str): Task type ("openEnd", "closeEnd", "request")

    Returns:
        Depends on task type
    """
    if video_task_type == "openEnd":
        return await handle_openEnd_task(
            video_path=quiz_data['video'], 
            question=quiz_data['question'], 
            target_lang=quiz_data['target_lang']
        )
    elif video_task_type == "closeEnd":
        return await handle_closeEnd_task(
            video_path=quiz_data['video'], 
            question=quiz_data['question'], 
            options=quiz_data['option']
        )
    elif video_task_type == "request":
        return await handle_request_task(question=quiz_data['question'])
    else:
        logger.error(f"Invalid video task type: {video_task_type}")
        return "❌ Invalid video task type"