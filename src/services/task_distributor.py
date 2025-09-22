from pydantic import BaseModel, Field
from datetime import timedelta
from typing import Dict
from src.models.task_models import Task, TaskDetail, TaskType

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

sample_audio_task = {
    "category": "Audio",
    "task_id": "#125702",
    "deadline": "3h",
    "extend_deadline": "2h",
    "required_language": "English",
    "required_dialects": "Nigerian Pidgin",
    "task_type": "Audio Submission",
    "rewards": "₦15",
    "category_type": "Dynamic",
    "task_description": "Record and upload an audio clip based on the given prompt.",
    "task_instructions": "Record an audio message answering the following prompt: 'What made you laugh today?'",
    "audio_upload_required": True,  # Audio upload is required
    "audio_file_format": "MP3, WAV, AAC",  # Accepted audio formats
    "max_audio_size": "50MB",  # Maximum file size for audio upload
}


sample_video_task = {
    "category": "Video",
    "task_id": "#125703",
    "deadline": "4h",
    "extend_deadline": "3h",
    "required_language": "English",
    "required_dialects": "Nigerian Pidgin",
    "task_type": "Video Submission",
    "rewards": "₦20",
    "category_type": "Dynamic",
    "task_description": "Upload a video based on the given prompt.",
    "task_instructions": "Upload a video that answers the following prompt: 'What’s something that made you smile today?'",
    "video_upload_required": True,  # Video upload is required
    "video_file_format": "MP4, MOV, AVI",  # Accepted formats
    "max_video_size": "500MB",  # Maximum file size for upload
}

sample_image_task = {
    "category": "Image",
    "task_id": "#125705",
    "deadline": "4h",
    "extend_deadline": "3h",
    "required_language": "English",
    "required_dialects": "Nigerian Pidgin",
    "task_type": "Image Submission",
    "rewards": "₦25",
    "category_type": "Dynamic",
    "task_description": "Upload an image that answers the given prompt.",
    "task_instructions": "Upload an image that represents something that made you smile today.",
    "image_upload_required": True,  # Image upload is required
    "image_file_format": "JPEG, PNG, GIF",  # Accepted image formats
    "max_image_size": "10MB",  # Maximum file size for image upload
}


full_task_detail = {
    "#125702": {
        'task_id': "#125702",
        "required_language": "Pidgin",
        "min_duration": timedelta(seconds=30),
        "max_duration": timedelta(seconds=120),
    }
}

async def assign_task(agent_id, task_type: TaskType):
    if task_type == TaskType.Text:
        # Logic to fetch and assign a task based on agent profile
        return Task(**sample_translation_text_task)
    elif task_type == TaskType.Audio:
        # Logic to fetch and assign a task based on agent profile
        return Task(**sample_audio_task)
    elif task_type == TaskType.Image:
        return Task(**sample_image_task)
    elif task_type == TaskType.Video:
        return Task(**sample_video_task)

async def get_full_task_detail(task_id, user_id) -> TaskDetail:
    """
    Fetches the full details of a task based on its ID.

    Args:
        task_id (str): The ID of the task to fetch details for.
    Returns:
        TaskDetail: A Pydantic model containing the full details of the task.
    """
    return TaskDetail(**full_task_detail[task_id])