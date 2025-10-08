from aiogram.fsm.state import State, StatesGroup

class Authentication(StatesGroup):

    collector_check = State()        # "Are you a collector?"
    user_type_check = State()        # "Are you a registered user?"
    login_email = State()            # Login: email
    login_phone = State()         # Login: phone
    login_password = State()        #Login password



    organization_check = State()      # Are you part of org?
    company_selection = State()       # Select company
    name_input = State()             # Name
    email_input = State()            # Email 
    phone_input = State()            # Phone 
    password_input = State()         # Password
    confirm_password = State()       # Confirm password
    registration_complete = State()   # Done

    set_signup_type = State()
    set_login_type = State()
    otp_step = State()

    #login_password = State()
    #login_success = State()
    
    
    # New States for API v2
    api_login_type = State()
    api_login_email = State()
    api_login_password = State()
    api_register_type = State()      