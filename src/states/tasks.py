from aiogram.fsm.state import StatesGroup, State

class TaskState(StatesGroup):
    waiting_for_task = State()
    reviewing = State()
    language_selection = State()
    task_in_progress = State()
    task_completed = State()

'''
class AssessmentState(StatesGroup):
    
    ready_to_start_assessment = State()
    waiting_for_translation = State()
    assessment_complete = State()'''


class AudioTaskSubmission(StatesGroup):
    waiting_for_audio = State()

class TextTaskSubmission(StatesGroup):
    waiting_for_text = State()

class ImageTaskSubmission(StatesGroup):
    waiting_for_image = State()

class VideoTaskSubmission(StatesGroup):
    waiting_for_video = State()


