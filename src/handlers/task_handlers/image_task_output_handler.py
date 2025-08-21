import logging
from typing import List

from src.keyboards.inline import quiz_options_kb


logger = logging.getLogger(__name__)


async def handle_openEnd_task(image_path: str, question: str, target_lang: str):
    """
    Handles open-ended image task.

    Args:
        image_path (str): The image path.
        question (str): The task to be carried out on the image.
        target_lang (str): The translation language.
        
    Returns:
        image_file (FSInputFile): task image file.
        caption (str): Task instruction text.
    """
    image_file = image_path
    caption = f"❓{question}\n\n Make sure to describe in {target_lang}."
    
    return message.answer_photo(
        photo=image_file,
        caption=caption
    )
    
async def handle_closeEnd_task(image_path: str, question: str, options: List):
    """
    Handles close-ended image task.

    Args:
        image_path (str): The image path.
        question (str): The task to be carried out on the image.
        options (List): The list of the options to be selected from to answer the question.
    
    Returns:
        image_file (FSInputFile): task image file.
        caption (str): Task instruction text.
        options (keyboard): Task Options in form of a clickable button.
    """
    image_file = image_path
    caption = f"❓{question}\n."
    options = quiz_options_kb(options)
    
    return image_file, caption, options

async def handle_request_task(question: str):
    """
    Handles Image request task.

    Args:
        question (str): The theme the image requested from the user need to answer.
        
    Returns:
        theme (str): Task instruction theme text to provide image.
    """
    return f"❓{question}\n"
    
    
    
async def handle_image_task(quiz_data, image_task_type: str):
    """
    Handles images task for all types.
    """
    if image_task_type == "openEnd":
        return handle_openEnd_task(image_path=quiz_data['image'], question=quiz_data['question'], target_lang=quiz_data['target_lang'])
    elif image_task_type == "closeEnd":
        return handle_closeEnd_task(image_path=quiz_data['image'], question=quiz_data['question'], options=quiz_data['option'])
    elif image_task_type == "request":
        return handle_request_task(question=quiz_data['question'])
    else:
        return "❌ Invalid image task type"