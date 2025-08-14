from aiogram.fsm.state import State, StatesGroup

class Onboarding(StatesGroup):
    intro = State()
    quiz = State()

    quiz_question = State()
    quiz_answer = State()
    quiz_retry = State()
    profile_name = State()

    
    name = State()
    location = State()
    state_residence = State() 
    age_range= State()
    gender = State()
    education = State()
    industry = State()
    languages = State()
    dialect_selection = State()
    task_type = State()

    text_writing_ability = State() 
    phone_quality = State()         
    favourite_speaker = State()
    referrer = State()
