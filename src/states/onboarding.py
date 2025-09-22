from aiogram.fsm.state import State, StatesGroup

class Onboarding(StatesGroup):
    intro = State()
    quiz = State()

    quiz_question = State()
    quiz_answer = State()
    quiz_retry = State()
    profile_name = State()
    local_goverment = State()
    
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

    category_question = State() 

    referrer = State()
    registration_retry = State()

class Tutorial(StatesGroup):
    ready_to_start = State()
    watching = State()