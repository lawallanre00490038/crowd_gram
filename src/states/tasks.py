from aiogram.fsm.state import StatesGroup, State

class TaskState(StatesGroup):
    waiting_for_submission = State()
    reviewing = State()

class TextTaskSubmission(StatesGroup):
    waiting_for_text = State()

class ImageTaskSubmission(StatesGroup):
    waiting_for_image = State()