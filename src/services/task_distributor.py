from pydantic import BaseModel, Field
from datetime import timedelta
from typing import Dict
from src.models.task_models import TranslationTask, TaskDetail

sample_translation_text_task = {
    "category": "Text",
    "task_id": "#125702",
    "deadline": "2h",
    "extend_deadline": "2h",
    "required_language": "Pidgin",
    "required_dialects": "Port Harcourt",
    "task_type": "Translation",
    "rewards": "₦10",
    "category_type": "Static",
    "task_description": "What’s something that made you smile today?",
    "task_instructions": "Translate the following text into Pidgin English.",
}


full_task_detail = {
    "#125702": {
        'task_id': "#125702",
        "required_language": "Pidgin",
        "min_duration": timedelta(seconds=30),
        "max_duration": timedelta(seconds=120),
    }
}
async def assign_task(agent_id):
    # Logic to fetch and assign a task based on agent profile
    return TranslationTask(**sample_translation_text_task)

async def get_full_task_detail(task_id, user_id) -> TaskDetail:
    """
    Fetches the full details of a task based on its ID.

    Args:
        task_id (str): The ID of the task to fetch details for.
    Returns:
        TaskDetail: A Pydantic model containing the full details of the task.
    """
    return TaskDetail(**full_task_detail[task_id])