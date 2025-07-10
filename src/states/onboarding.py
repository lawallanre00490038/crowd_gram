from aiogram.fsm.state import State, StatesGroup

class Onboarding(StatesGroup):
    intro = State()
    quiz = State()

    quiz_question = State()
    quiz_answer = State()
    quiz_retry = State()
    profile_name = State()

    name = State()
    phone = State()
    gender = State()
    location = State()
    languages = State()
    education = State()
    task_type = State()
    referrer = State()
