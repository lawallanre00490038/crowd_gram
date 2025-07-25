# Remplacer les imports en haut du fichier authentication_routes
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import sessionmaker
from src.database.models import Agent 
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from src.states.authentication import Authentication
from src.states.onboarding import Onboarding
from src.keyboards.auth import company_kb
from src.utils.password import hash_password, verify_password  # Nouvelle import
import re

router = Router()

async def check_user_exists(identifier: str):
    """
    verify is user exist via mail or phone/ if not-> none
    """
    # replace w/ database instance 
    # session = SessionLocal()
    # try:
    #     agent = session.query(Agent).filter(
    #         (Agent.email == identifier) | (Agent.phone == identifier)
    #     ).first()
    #     return agent
    # finally:
    #     session.close()
    
    # simulation for now
    return None

# Handler: Choix du type d'utilisateur (collector/registered/new)
@router.callback_query(Authentication.collector_check, F.data.in_(["collector_yes", "registered_yes", "new_user"]))
async def handle_user_type_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    if callback.data == "collector_yes":
        # TODO: Rediriger vers le flow collector (à implémenter plus tard)
        await callback.message.answer(
            "Collector flow in development."
        )
        await state.clear()
        
    elif callback.data == "registered_yes":
        # Utilisateur existant -> Login
        await callback.message.answer(
            "🎉 Welcome back!\n\n"
            "Please enter your email or phone number to login:"
        )
        await state.set_state(Authentication.login_email)
        
    elif callback.data == "new_user":
        # Nouveau utilisateur -> Flow normal d'authentication
        # Créer les boutons pour organization check
        org_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Yes", callback_data="org_yes")],
                [InlineKeyboardButton(text="❌ No", callback_data="org_no")]
            ]
        )

        welcome_text=(    
            "Great! Let's get you set up! 👋 Welcome to Equalyz Crowd!\n\n"
            "As a contributor/agent, you'll help train AI models and earn money for quality work.\n\n"
            "This quick onboarding sets up your profile so we can match you with the best tasks.\n\n"
            "Let’s begin! 🚀"
        )
        await callback.message.answer(welcome_text)
        await callback.message.answer(
            "Are you part of an organization?",
            reply_markup=org_kb
        )
        
        await state.set_state(Authentication.organization_check)

# Handler: Login - Email/Phone input
@router.message(Authentication.login_email)
async def handle_login_identifier(message: Message, state: FSMContext):
    identifier = message.text.strip()
    await state.update_data(login_identifier=identifier)
    
    # Vérifier si l'utilisateur existe
    user = await check_user_exists(identifier)
    
    if not user:
        await message.answer(
            "❌ No account found with this email/phone.\n\n"
            "Would you like to create a new account instead?"
        )
        
        # Proposer de créer un compte
        choice_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Create Account", callback_data="create_account")],
                [InlineKeyboardButton(text="🔄 Try Again", callback_data="try_login_again")]
            ]
        )
        await message.answer(
            "What would you like to do?",
            reply_markup=choice_kb
        )
        return
    
    # Utilisateur trouvé -> Demander le mot de passe
    await message.answer(
        "🔒 Please enter your password:"
    )
    await state.set_state(Authentication.login_password)

# Handler: Login - Password input
@router.message(Authentication.login_password)
async def handle_login_password(message: Message, state: FSMContext):
    password = message.text.strip()
    user_data = await state.get_data()
    identifier = user_data.get('login_identifier')
    
    # next step-> verify user
    # user = await check_user_exists(identifier)
    # if user and verify_password(password, user.password_hash):
    #     # Login réussi
    #     await message.answer(f"✅ Welcome back, {user.name}!")
    #     # Rediriger vers le dashboard/menu principal
    #     await state.clear()
    # else:
    #     await message.answer("❌ Incorrect password. Please try again:")
    #     return
    
    # for now simulation of successful login
    await message.answer(
        "✅ Login successful!\n\n"
        "🎉 Welcome back to Equalyz Crowd!\n\n"
        "You can now access your tasks and continue earning."
    )
    await state.clear()

# Handler: Gestion des choix après échec de login
@router.callback_query(Authentication.login_email, F.data.in_(["create_account", "try_login_again"]))
async def handle_login_failure_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    if callback.data == "create_account":
        # Rediriger vers le flow de création de compte
        await callback.message.answer(
            "🌟 Let's create your account!\n\n"
        )
        
        org_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Yes", callback_data="org_yes")],
                [InlineKeyboardButton(text="❌ No", callback_data="org_no")]
            ]
        )
        await callback.message.answer(
            "Are you part of an organization?",
            reply_markup=org_kb
        )
        await state.set_state(Authentication.organization_check)
        
    elif callback.data == "try_login_again":
        await callback.message.answer(
            "🔄 Please enter your email or phone number:"
        )
        await state.set_state(Authentication.login_email)






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
@router.callback_query(Authentication.organization_check, F.data.in_(["org_yes", "org_no"]))
async def handle_organization_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    if callback.data == "org_yes":
        await state.update_data(has_organization="Yes")
        await callback.message.answer(
            "🏢 Please select your organization:\n\n"
            "Choose from the list below:",
            reply_markup=company_kb()
        )
        await state.set_state(Authentication.company_selection)
    else:
        await state.update_data(has_organization="No", company="Individual")
        await callback.message.answer(
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
    

      # Hash le mot de passe avant de le sauvegarder
    hashed_password = hash_password(confirm_password)
    await state.update_data(password_hash=hashed_password)
    # Passwords match - create account
    await message.answer(
        "✅ Account created successfully!\n\n"
        "🎉 Welcome to Equalyz Crowd!\n\n"
        "Now let's complete your profile..."
    )
     # Passer à l'onboarding (en skippant le nom)
    await message.answer("🌍 What's your current location?")
    await state.set_state(Onboarding.location)  # Skip name, start from location

    # TO DO:  
    #user_data= await state.get_data()
    # call API
    # create_account_api(user_data)
    
  

   