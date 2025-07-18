from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states.authentication import Authentication
from src.states.onboarding import Onboarding
from src.keyboards.auth import company_kb
import re

router = Router()

#validate format 
def validate_phone_format(phone: str) -> bool:
    """Validation plus stricte avec codes pays"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    # verif pattern
    pattern = r'^\+\d{1,4}\d{6,12}$'
    
    if not re.match(pattern, phone):
        return False
    
    # 10-15 after +
    phone_digits = phone[1:]
    return 10 <= len(phone_digits) <= 15

def format_phone(phone: str) -> str:
    return phone.strip().replace(" ", "").replace("-", "") 
    

# Handler: Are you part of organization?
@router.message(Authentication.organization_check)
async def handle_organization_check(message: Message, state: FSMContext):
    response = message.text.strip()
    await state.update_data(has_organization=response)
    
    if "Yes" in response:
        # Show company selection
        await message.answer(
            "🏢 Please select your organization:\n\n"
            "Choose from the list below:",
            reply_markup=company_kb()
        )
        await state.set_state(Authentication.company_selection)
    else:
        # Skip company, go directly to name
        await state.update_data(company="Individual")
        await message.answer(
            "👤 What's your full name?\n\n"
            "This will be used for your account registration."
        )
        await state.set_state(Authentication.name_input)

# Handler: Company selection
@router.message(Authentication.company_selection)
async def handle_company_selection(message: Message, state: FSMContext):
    company = message.text.strip()
    await state.update_data(company=company)
    
    await message.answer(
        "👤 What's your full name?\n\n"
        "This will be used for your account registration."
    )
    await state.set_state(Authentication.name_input)

# Handler: Name input
@router.message(Authentication.name_input)
async def handle_name_input(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(auth_name=name)
    
    await message.answer(
        "📧 What's your email address?\n\n"
        "We'll use this for account verification and important updates."
    )
    await state.set_state(Authentication.email_input)

# Handler: Email input
@router.message(Authentication.email_input)
async def handle_email_input(message: Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(email=email)
    
    await message.answer(
        "📱 What's your phone number?\n\n"
        "Format: +234XXXXXXXXX (include country code)"
    )
    await state.set_state(Authentication.phone_input)
    
  
    
   
# Handler: Password input
@router.message(Authentication.password_input)
async def handle_password_input(message: Message, state: FSMContext):
    password = message.text.strip()

    # verif
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        await message.answer(
            "❌ Password too weak.\n\n"
            "It must be at least 8 characters long and include both letters and numbers.\n"
            "Please try again:"
        )
        return  # on ne passe pas à l'étape suivante

    # validated
    await state.update_data(password=password)

    await message.answer(
        "🔒 Please confirm your password:\n\n"
        "Re-enter the password you created."
    )
    await state.set_state(Authentication.confirm_password)


# Handler: Phone input
@router.message(Authentication.phone_input)
async def handle_phone_input(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not validate_phone_format(phone):
        await message.answer(
            "❌ Invalid phone number format.\n\n"
            "Please use international format: +CountryCodeNumber\n"
            "Examples: +234803123456, +1555123456, +33123456789\n\n"
            "Try again:"
        )
        return
    formatted_phone= format_phone(phone)

    await state.update_data(auth_phone=formatted_phone)
    
    await message.answer(
        "🔒 Create a secure password:\n\n"
        "Password should be at least 8 characters long."
    )
    await state.set_state(Authentication.password_input)





# Handler: Confirm password
@router.message(Authentication.confirm_password)
async def handle_confirm_password(message: Message, state: FSMContext):
    confirm_password = message.text.strip()
    user_data = await state.get_data()
    
    if confirm_password != user_data.get('password'):
        await message.answer(
            "❌ Passwords don't match! Please try again:\n\n"
            "Re-enter your password:"
        )
        return
    
    # Passwords match - create account
    await message.answer(
        "✅ Account created successfully!\n\n"
        "🎉 Welcome to Equalyz Crowd!\n\n"
        "Now let's complete your profile..."
    )
    
     # Passer à l'onboarding (en skippant le nom)
    await message.answer("🌍 What's your current location?")
    await state.set_state(Onboarding.location)  # Skip name, start from location

    # TO DO:  call API
    # create_account_api(user_data)
    
  

