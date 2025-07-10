from aiogram.fsm.state import StatesGroup, State

class TaskState(StatesGroup):
    waiting_for_submission = State()
    reviewing = State()
