from aiogram.fsm.state import StatesGroup, State

class TaskState(StatesGroup):
    waiting_for_submission = State()
    reviewing = State()
    language_selection = State()
    task_in_progress = State()
    task_completed = State()

'''
class AssessmentState(StatesGroup):
    
    ready_to_start_assessment = State()
    waiting_for_translation = State()
    assessment_complete = State()'''