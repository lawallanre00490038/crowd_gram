from aiogram.fsm.state import StatesGroup, State

class QAState(StatesGroup):
    processing = State()
    completed = State()
