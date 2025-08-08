from aiogram.fsm.state import StatesGroup, State

class TaskState(StatesGroup):
    waiting_for_task = State()
    reviewing = State()

class AudioTaskSubmission(StatesGroup):
    waiting_for_audio = State()

class TextTaskSubmission(StatesGroup):
    waiting_for_text = State()

class ImageTaskSubmission(StatesGroup):
    waiting_for_image = State()

class VideoTaskSubmission(StatesGroup):
    waiting_for_video = State()