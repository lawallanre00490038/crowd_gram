from pydantic import BaseModel, Field
from datetime import timedelta
from typing import Dict

# Define the Pydantic model for your task data.
# Each field corresponds to a key in your dictionary.
class TranslationTask(BaseModel):
    """
    A Pydantic model representing a translation task.
    This model provides data validation and type-hinting for task data.
    """
    category: str
    task_id: str
    deadline: str
    extend_deadline: str
    required_language: str
    required_dialects: str
    task_type: str
    rewards: str
    category_type: str
    task_description: str
    task_instructions: str

class TaskDetail(BaseModel):
    task_id: str
    required_language: str
    min_duration: timedelta
    max_duration: timedelta

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

async def get_full_task_detail(task_id) -> TaskDetail:
    return TaskDetail(**full_task_detail[task_id])