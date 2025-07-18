from aiogram.fsm.state import State, StatesGroup

class Authentication(StatesGroup):
    organization_check = State()      # Are you part of org?
    company_selection = State()       # Select company
    name_input = State()             # Name
    email_input = State()            # Email  
    password_input = State()         # Password
    phone_input = State()            # Phone
    confirm_password = State()       # Confirm password
    registration_complete = State()   # Done

    #login_password = State()
    #login_success = State()