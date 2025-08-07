from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states.onboarding import Onboarding
from src.states.authentication import Authentication
from src.keyboards.reply import gender_kb, task_type_kb, industry_kb, primary_device_kb, dialect_fluency_kb
from src.keyboards.inline import g0_to_tutorials_kb
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from src.handlers.onboarding_routes.quiz import start_quiz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import re

from pathlib import Path
from aiogram.types import InputFile
from aiogram.types import FSInputFile


router = Router()

COUNTRIES = [
    "Afghanistan", "Aland Islands", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antarctica",
    "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh",
    "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bonaire, Sint Eustatius and Saba",
    "Bosnia and Herzegovina", "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory", "Brunei", "Bulgaria",
    "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands", "Central African Republic",
    "Chad", "Chile", "China", "Christmas Island", "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo", "Cook Islands",
    "Costa Rica", "Côte d'Ivoire", "Croatia", "Cuba", "Curaçao", "Cyprus", "Czech Republic", "Democratic Republic of the Congo",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador",
    "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands", "Faroe Islands", "Fiji Islands", "Finland",
    "France", "French Guiana", "French Polynesia", "French Southern Territories", "Gabon", "Georgia", "Germany", "Ghana",
    "Gibraltar", "Great Britain", "Greece", "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guernsey and Alderney",
    "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Heard Island and McDonald Islands", "Honduras", "Hong Kong S.A.R.",
    "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jersey",
    "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia",
    "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau S.A.R.", "Macedonia", "Madagascar", "Malawi", "Malaysia",
    "Maldives", "Mali", "Malta", "Man", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico",
    "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia",
    "Nauru", "Nepal", "Netherlands", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island",
    "North Korea", "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestinian State Occupied", "Panama",
    "Papua new Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn Island", "Poland", "Portugal", "Puerto Rico", "Qatar",
    "Reunion", "Romania", "Russia", "Rwanda", "Saint Helena", "Saint Kitts and Nevis", "Saint Lucia", "Saint Pierre and Miquelon",
    "Saint Vincent and the Grenadines", "Saint-Barthélemy", "Saint-Martin (French part)", "Samoa", "San Marino",
    "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
    "Sint Maarten (Dutch part)", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Georgia",
    "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Svalbard And Jan Mayen Islands", "Swaziland",
    "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Togo",
    "Tokelau", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks and Caicos Islands", "Tuvalu",
    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "United States Minor Outlying Islands",
    "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City State (Holy See)", "Venezuela", "Vietnam", "Virgin Islands (British)",
    "Virgin Islands (US)", "Wallis and Futuna Islands", "Western Sahara", "Yemen", "Zambia", "Zimbabwe", "Other"
]

# Niveaux d'éducation
EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Doctorate Degree", 
    "High School Diploma",
    "Master's Degree",
    "SSCE/WAEC",
    "Other"
]

# LISTE - Dialectes (sélection multiple max 2)
DIALECT_OPTIONS = [
    "English",
    "French", 
    "Fulani",
    "Hausa",
    "Hindi",
    "Igbo",
    "Pidgin",
    "Punjabi", 
    "Shona",
    "Swahili",
    "Yoruba"
]

#  FONCTION pour créer le clavier des pays (existante)
def create_countries_keyboard(page=0, per_page=40):
    print(f"🔍 [DEBUG] Creating countries keyboard - Page: {page}, Per page: {per_page}")
    
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(COUNTRIES))
    
    buttons = []
    for i, country in enumerate(COUNTRIES[start_idx:end_idx]):
        country_index = start_idx + i
        buttons.append([InlineKeyboardButton(
            text=country, 
            callback_data=f"ctry_{country_index}"
        )])
    
    # Navigation
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"page_{page-1}"))
    if end_idx < len(COUNTRIES):
        nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Indicateur de page
    total_pages = (len(COUNTRIES) + per_page - 1) // per_page
    page_info = f"📄 Page {page + 1}/{total_pages}"
    buttons.append([InlineKeyboardButton(text=page_info, callback_data="page_info")])
    
    print(f"🔍 [DEBUG] Keyboard created with {len(buttons)} rows, showing countries {start_idx}-{end_idx-1}")
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_education_keyboard():
    """Créer le clavier avec tous les niveaux d'éducation"""
    print(f"🔍 [DEBUG] Creating education keyboard with {len(EDUCATION_LEVELS)} options")
    
    buttons = []
    for i, education in enumerate(EDUCATION_LEVELS):
        buttons.append([InlineKeyboardButton(
            text=education, 
            callback_data=f"edu_{i}"
        )])
    
    print(f"🔍 [DEBUG] Education keyboard created with {len(buttons)} rows")
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_dialect_keyboard(selected_dialects=None):
    """Créer le clavier avec dialectes - permet sélection multiple (max 2)"""
    if selected_dialects is None:
        selected_dialects = []
    
    print(f"🔍 [DEBUG] Creating dialect keyboard - Selected: {selected_dialects}")
    
    buttons = []
    
    # Afficher les dialectes avec checkmarks si sélectionnés
    for i, dialect in enumerate(DIALECT_OPTIONS):
        if dialect in selected_dialects:
            text = f"✅ {dialect}"  # Sélectionné
        else:
            text = f"⚪ {dialect}"  # Non sélectionné
        
        buttons.append([InlineKeyboardButton(
            text=text, 
            callback_data=f"dial_{i}"
        )])
    
    # Zone d'information sur la sélection
    if selected_dialects:
        selected_text = ", ".join(selected_dialects)
        info_text = f"Selected: {selected_text} ({len(selected_dialects)}/2)"
    else:
        info_text = "Select up to 2 dialects (0/2)"
    
    buttons.append([InlineKeyboardButton(
        text=f"📋 {info_text}", 
        callback_data="dial_info"
    )])
    
    # Bouton Done (seulement si au moins 1 dialecte sélectionné)
    if selected_dialects:
        buttons.append([InlineKeyboardButton(
            text="✅ Done - Continue", 
            callback_data="dial_done"
        )])
    
    print(f"🔍 [DEBUG] Dialect keyboard created with {len(buttons)} rows")
    return InlineKeyboardMarkup(inline_keyboard=buttons)

tutorial_videos = [
    "🎥 Video 1: Introduction to Data Collection\nhttps://youtu.be/FSV1uAMbYqM?list=PLeBirUGntTt1TGeuP3xQX9ZbpeGSdbmzm",
    "🎥 Video 2: How Annotation Works\nhttps://youtu.be/FSV1uAMbYqM?list=PLeBirUGntTt1TGeuP3xQX9ZbpeGSdbmzm",
    "🎥 Video 3: Quality and Submission Guide\nhttps://youtu.be/FSV1uAMbYqM?list=PLeBirUGntTt1TGeuP3xQX9ZbpeGSdbmzm"
]



# tutorial_videos = [
#     Path("compressed/tutorial_1.mp4"),
#     Path("compressed/tutorial_2.mp4"),
#     Path("compressed/tutorial_3.mp4")
# ]


# --- Custom tutorial states ---

class Tutorial(StatesGroup):
    ready_to_start = State()
    watching = State()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    print(f"🔍 [DEBUG] /start command received from user {message.from_user.id}")
    
    welcome_text = (    
        "👋 Welcome to Equalyz Crowd!\n\n"
        "We're building the future of AI by collecting multilingual data across Africa.\n\n"
        "As a contributor/agent, you'll help train AI models and earn money for quality work.\n\n"
        "Let's begin! 🚀"   
    )
    await message.answer(welcome_text)

    tutorial_intro_text = (
        "🧠 You will be guided through a series of videos to learn about the basics of data collection and annotation.\n\n"
        "Would you like to watch the tutorial videos?"
    )
    
    tutorial_choice_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📺 Yes, show me the videos", callback_data="tutorial_yes")],
            [InlineKeyboardButton(text="⏭️ Skip tutorials", callback_data="skip_tutorials")]
        ]
    )
    await message.answer(tutorial_intro_text, reply_markup=tutorial_choice_kb)
    await state.set_state(Tutorial.ready_to_start)

@router.callback_query(Tutorial.ready_to_start, F.data.in_(["tutorial_yes", "skip_tutorials"]))
async def handle_tutorial_choice(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Tutorial choice: {callback.data}")
    await callback.answer()
    
    if callback.data == "tutorial_yes":
        await callback.message.answer("📺 Great! Let's start with the tutorial videos.")
        await state.update_data(tutorial_index=0)
        await state.set_state(Tutorial.watching)
        await send_tutorial(callback.message, state)
     
    elif callback.data == "skip_tutorials":
        await show_user_type_selection(callback.message, state)

async def show_user_type_selection(message: Message, state: FSMContext):
    print(f"🔍 [DEBUG] Showing user type selection")
    selection_text = (
        "🔽 Now, please tell us what type of user you are:"
    )
    await message.answer(selection_text)
    
    user_type_kb = InlineKeyboardMarkup(
        inline_keyboard=[

            [InlineKeyboardButton(text="👤 I'm a Registered User", callback_data="registered_yes")],
            [InlineKeyboardButton(text="🆕 I'm New Here", callback_data="new_user")],

            # [InlineKeyboardButton(text="📊 I'm a Contibutor", callback_data="collector_yes")],
            [InlineKeyboardButton(text="👤 Sign Up", callback_data="registered_yes")],
            [InlineKeyboardButton(text="🆕 Sign In", callback_data="new_user")],

            [InlineKeyboardButton(text="🔙 Back to tutorials", callback_data="back_to_tutorials")]
        ]
    )
    
    await message.answer(
        "Please select your user type:",
        reply_markup=user_type_kb
    )
    await state.set_state(Authentication.collector_check)

def tutorial_nav_kb(index: int):
    buttons = []
    
    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Back", callback_data="prev"))
    if index < len(tutorial_videos) - 1:
        nav_row.append(InlineKeyboardButton(text="➡️ Watch Next Video", callback_data="next"))
    else:
        nav_row.append(InlineKeyboardButton(text="✅ Ready for Quiz", callback_data="ready"))
    
    if nav_row:
        buttons.append(nav_row)
   
    buttons.append([InlineKeyboardButton(text="⏭️ Skip Videos", callback_data="skip_videos")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def send_tutorial(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data.get("tutorial_index", 0)
    await message.answer(tutorial_videos[index], reply_markup=tutorial_nav_kb(index))



# async def send_tutorial(message: Message, state: FSMContext):
#     data = await state.get_data()
#     index = data.get("tutorial_index", 0)
#     video_path = tutorial_videos[index]  # this is a pathlib.Path object

#     try:
#         video_file = FSInputFile(path=video_path)  # ✅ This is the correct class to use
#         print(video_file)
        
#         await message.answer_video(
#             video=video_file,
#             caption=f"Tutorial {index + 1}",
#             reply_markup=tutorial_nav_kb(index)
#         )
#     except FileNotFoundError:
#         await message.answer("⚠️ Video file not found.")



# --- Handle navigation (next/back/ready) ---

@router.callback_query(Tutorial.watching, F.data.in_(["next", "prev", "ready"]))
async def tutorial_navigation(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Tutorial navigation: {callback.data}")
    await callback.answer()
    data = await state.get_data()
    index = data.get("tutorial_index", 0)

    if callback.data == "next" and index < len(tutorial_videos) - 1:
        index += 1
        await state.update_data(tutorial_index=index)
        await send_tutorial(callback.message, state)

    elif callback.data == "prev" and index > 0:
        index -= 1
        await state.update_data(tutorial_index=index)
        await send_tutorial(callback.message, state)

    elif callback.data == "ready":
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="👍 Yes, I'm ready", callback_data="quiz_yes"),
                InlineKeyboardButton(text="🔁 No, show again", callback_data="quiz_no"),
                InlineKeyboardButton(text="⏭️ Skip Quiz", callback_data="skip_quiz")
            ]]
        )
        await callback.message.answer("Have you finished watching all the videos?\nStart quiz now?", reply_markup=kb)
    
    elif callback.data == "skip_videos":
        await show_user_type_selection(callback.message, state)

@router.callback_query(Tutorial.watching, F.data.in_(["quiz_yes", "quiz_no"]))
async def quiz_ready_response(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Quiz response: {callback.data}")
    await callback.answer()

    if callback.data == "quiz_yes":
        await callback.message.answer("✅ Great! Let's begin the short quiz.")
        await state.set_state(Onboarding.intro)
        await start_quiz(callback.message, state)

    elif callback.data == "quiz_no":
        await state.update_data(tutorial_index=0)
        await send_tutorial(callback.message, state)

@router.callback_query(Authentication.collector_check, F.data == "back_to_tutorials")
async def handle_back_to_tutorials(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Back to tutorials clicked")
    await callback.answer()
    
    tutorial_intro_text = (
        "🧠 You will be guided through a series of videos to learn about the basics of data collection and annotation.\n\n"
        "Would you like to watch the tutorial videos?"
    )
    
    tutorial_choice_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📺 Yes, show me the videos", callback_data="tutorial_yes")],
            [InlineKeyboardButton(text="⏭️ Skip tutorials", callback_data="skip_tutorials")]
        ]
    )
    
    await callback.message.answer(tutorial_intro_text, reply_markup=tutorial_choice_kb)
    await state.set_state(Tutorial.ready_to_start)


@router.message(Onboarding.location)
async def get_location(message: Message, state: FSMContext):
    print(f"🔍 [DEBUG] get_location called - Message: '{message.text}'")
    user_data = await state.get_data()
    print(f"🔍 [DEBUG] User data: awaiting_manual_location = {user_data.get('awaiting_manual_location')}")
    
    try:
        # Vérifier si on attend une saisie manuelle
        if user_data.get("awaiting_manual_location"):
            location = message.text.strip()
            await state.update_data(location=location, awaiting_manual_location=False)
            
            print(f"🔍 [DEBUG] Manual location saved: {location}")
            await message.answer(f"✅ Location entered: {location}")
            
            # Continuer vers l'étape suivante
            await message.answer(
                "⚧ What's your gender? Your privacy is protected - this data is never shared publicly.", 
                reply_markup=gender_kb
            )
            await state.set_state(Onboarding.gender)
            print(f"🔍 [DEBUG] Moved to gender state")
        else:
            # Première fois - afficher la sélection de pays
            print(f"🔍 [DEBUG] First time - showing country selection")
            location_text = (
                "🌍 What's your current location?\n\n"
                "Please select your country:"
            )
            
            await message.answer(location_text, reply_markup=create_countries_keyboard())
            print(f"🔍 [DEBUG] Country keyboard sent")
            
    except Exception as e:
        print(f"❌ [ERROR] Exception in get_location: {e}")

@router.callback_query(Onboarding.location, F.data.startswith("ctry_"))
async def handle_country_by_index(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Country by index handler appelé! Data: {callback.data}")
    
    try:
        await callback.answer()
        print(f"🔍 [DEBUG] Callback answered")
        
        # Extraire l'index
        country_index = int(callback.data.replace("ctry_", ""))
        print(f"🔍 [DEBUG] Country index: {country_index}")
        
        # Vérifier que l'index est valide
        if 0 <= country_index < len(COUNTRIES):
            selected_country = COUNTRIES[country_index]
            print(f"🔍 [DEBUG] Selected country: '{selected_country}'")
            
            # Gérer "Other"
            if selected_country == "Other":
                print(f"🔍 [DEBUG] Other selected")
                await callback.message.answer("✍️ Please type your country/location:")
                await state.update_data(awaiting_manual_location=True)
                return
            
            # Sauvegarder
            await state.update_data(location=selected_country)
            await callback.message.answer(f"✅ Location selected: {selected_country}")
            print(f"🔍 [DEBUG] Location saved")
            
            # Continuer
            await callback.message.answer(
                "⚧ What's your gender? Your privacy is protected - this data is never shared publicly.", 
                reply_markup=gender_kb
            )
            await state.set_state(Onboarding.gender)
            print(f"🔍 [DEBUG] Success - moved to gender!")
            
        else:
            print(f"❌ [ERROR] Invalid country index: {country_index}")
            await callback.answer("Invalid selection", show_alert=True)
            
    except Exception as e:
        print(f"❌ [ERROR] Exception in country by index handler: {e}")
        await callback.answer("Error occurred", show_alert=True)

@router.callback_query(Onboarding.location, F.data.startswith("page_"))
async def handle_page_navigation(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Page handler appelé! Data: {callback.data}")
    
    try:
        await callback.answer()
        print(f"🔍 [DEBUG] Page callback answered")
        
        # Extraire le numéro de page
        page_num = int(callback.data.replace("page_", ""))
        print(f"🔍 [DEBUG] Page number: {page_num}")
        
        # Mettre à jour le message
        location_text = (
            "🌍 What's your current location?\n\n"
            f"Please select your country (Page {page_num + 1}):"
        )
        
        print(f"🔍 [DEBUG] Trying to edit message...")
        await callback.message.edit_text(
            location_text, 
            reply_markup=create_countries_keyboard(page=page_num)
        )
        print(f"🔍 [DEBUG] Message edited successfully")
        
    except Exception as e:
        print(f"❌ [ERROR] Exception in page handler: {e}")
        try:
            # Fallback: nouveau message si l'édition échoue
            await callback.message.answer(
                location_text, 
                reply_markup=create_countries_keyboard(page=page_num)
            )
            print(f"🔍 [DEBUG] Sent new message as fallback")
        except Exception as e2:
            print(f"❌ [ERROR] Fallback also failed: {e2}")
            await callback.answer("Error occurred", show_alert=True)

@router.callback_query(Onboarding.location, F.data == "page_info")
async def handle_page_info_click(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Page info clicked")
    await callback.answer("Page information", show_alert=False)



@router.message(Onboarding.gender)
async def get_gender(message: Message, state: FSMContext):
    print(f"🔍 [DEBUG] Gender received: {message.text}")
    await state.update_data(gender=message.text.strip())
    # ✅ PASSER DIRECTEMENT AUX DIALECTES :
    dialect_text = (
        "🗣️ Which dialects do you speak fluently?\n\n"
        "Select up to 2 dialects that you speak well.\n"
        "This helps us match you with local language tasks!"
    )
    await message.answer(dialect_text, reply_markup=create_dialect_keyboard())
    await state.set_state(Onboarding.dialect_fluency)


@router.callback_query(Onboarding.dialect_fluency, F.data.startswith("dial_"))
async def handle_dialect_selection(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Dialect selection handler appelé! Data: {callback.data}")
    
    try:
        await callback.answer()
        
        # Récupérer les dialectes actuellement sélectionnés
        user_data = await state.get_data()
        selected_dialects = user_data.get("selected_dialects", [])
        print(f"🔍 [DEBUG] Current selected dialects: {selected_dialects}")
        
        if callback.data == "dial_info":
            # Ignorer les clics sur l'info
            print(f"🔍 [DEBUG] Info button clicked - ignored")
            return
            
        elif callback.data == "dial_done":
            # Terminer la sélection
            print(f"🔍 [DEBUG] Done button clicked")
            
            if not selected_dialects:
                await callback.answer("Please select at least 1 dialect!", show_alert=True)
                return
            
            # Sauvegarder et continuer
            dialect_text = ", ".join(selected_dialects)
            await state.update_data(languages=dialect_text)
            await callback.message.answer(f"✅ Selected dialects: {dialect_text}")
            
            # Continuer vers l'éducation
            education_text = (
                "🎓 What's your highest level of education?\n\n"
                "Please select from the options below:"
            )
            await callback.message.answer(education_text, reply_markup=create_education_keyboard())
            await state.set_state(Onboarding.education)
            print(f"🔍 [DEBUG] Success - moved to education!")
            return
            
        else:
            # Sélection/désélection d'un dialecte
            dialect_index = int(callback.data.replace("dial_", ""))
            print(f"🔍 [DEBUG] Dialect index: {dialect_index}")
            
            if 0 <= dialect_index < len(DIALECT_OPTIONS):
                selected_dialect = DIALECT_OPTIONS[dialect_index]
                print(f"🔍 [DEBUG] Dialect: '{selected_dialect}'")
                
                # Toggle la sélection
                if selected_dialect in selected_dialects:
                    # Désélectionner
                    selected_dialects.remove(selected_dialect)
                    print(f"🔍 [DEBUG] Deselected: {selected_dialect}")
                else:
                    # Sélectionner (si pas déjà 2)
                    if len(selected_dialects) >= 2:
                        await callback.answer("Maximum 2 dialects allowed! Deselect one first.", show_alert=True)
                        return
                    
                    selected_dialects.append(selected_dialect)
                    print(f"🔍 [DEBUG] Selected: {selected_dialect}")
                
                # Sauvegarder dans l'état
                await state.update_data(selected_dialects=selected_dialects)
                
                # Mettre à jour le clavier
                await callback.message.edit_text(
                    "🗣️ Which dialects do you speak fluently?\n\n"
                    "Select up to 2 dialects that you speak well.\n"
                    "This helps us match you with local language tasks!",
                    reply_markup=create_dialect_keyboard(selected_dialects)
                )
                print(f"🔍 [DEBUG] Keyboard updated with selections: {selected_dialects}")
                
            else:
                print(f"❌ [ERROR] Invalid dialect index: {dialect_index}")
                await callback.answer("Invalid selection", show_alert=True)
            
    except Exception as e:
        print(f"❌ [ERROR] Exception in dialect selection handler: {e}")
        await callback.answer("Error occurred", show_alert=True)

@router.callback_query(Onboarding.dialect_fluency, F.data == "dial_info")
async def handle_dialect_info_click(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Dialect info clicked")
    await callback.answer("Selection information", show_alert=False)


@router.message(Onboarding.education)
async def get_education(message: Message, state: FSMContext):
    print(f"🔍 [DEBUG] get_education called - Message: '{message.text}'")
    user_data = await state.get_data()
    print(f"🔍 [DEBUG] User data: awaiting_manual_education = {user_data.get('awaiting_manual_education')}")
    
    try:
        # Vérifier si on attend une saisie manuelle (après avoir cliqué "Other")
        if user_data.get("awaiting_manual_education"):
            education = message.text.strip()
            await state.update_data(education=education, awaiting_manual_education=False)
            
            print(f"🔍 [DEBUG] Manual education saved: {education}")
            await message.answer(f"✅ Education level entered: {education}")
            
            # Continuer vers l'étape suivante (industry)
            industry_text = (
                "💼 What field do you work in or have experience with?\n\n"
                "Choose the option that best describes you:"
            )
            await message.answer(industry_text, reply_markup=industry_kb)
            await state.set_state(Onboarding.industry)
            print(f"🔍 [DEBUG] Moved to industry state")
        else:
            # Première fois - afficher la sélection d'éducation
            print(f"🔍 [DEBUG] First time - showing education selection")
            education_text = (
                "🎓 What's your highest level of education?\n\n"
                "Please select from the options below:"
            )
            
            await message.answer(education_text, reply_markup=create_education_keyboard())
            print(f"🔍 [DEBUG] Education keyboard sent")
            
    except Exception as e:
        print(f"❌ [ERROR] Exception in get_education: {e}")

@router.callback_query(Onboarding.education, F.data.startswith("edu_"))
async def handle_education_selection(callback: CallbackQuery, state: FSMContext):
    print(f"🔍 [DEBUG] Education selection handler appelé! Data: {callback.data}")
    
    try:
        await callback.answer()
        print(f"🔍 [DEBUG] Callback answered")
        
        # Extraire l'index
        education_index = int(callback.data.replace("edu_", ""))
        print(f"🔍 [DEBUG] Education index: {education_index}")
        
        # Vérifier que l'index est valide
        if 0 <= education_index < len(EDUCATION_LEVELS):
            selected_education = EDUCATION_LEVELS[education_index]
            print(f"🔍 [DEBUG] Selected education: '{selected_education}'")
            
            # Gérer "Other"
            if selected_education == "Other":
                print(f"🔍 [DEBUG] Other selected")
                await callback.message.answer("✍️ Please type your education level:")
                await state.update_data(awaiting_manual_education=True)
                return
            
            # Sauvegarder
            await state.update_data(education=selected_education)
            await callback.message.answer(f"✅ Education level selected: {selected_education}")
            print(f"🔍 [DEBUG] Education saved")
            
            # Continuer vers l'étape suivante (industry)
            industry_text = (
                "💼 What field do you work in or have experience with?\n\n"
                "Choose the option that best describes you:"
            )
            await callback.message.answer(industry_text, reply_markup=industry_kb)
            await state.set_state(Onboarding.industry)
            print(f"🔍 [DEBUG] Success - moved to industry!")
            
        else:
            print(f"❌ [ERROR] Invalid education index: {education_index}")
            await callback.answer("Invalid selection", show_alert=True)
            
    except Exception as e:
        print(f"❌ [ERROR] Exception in education selection handler: {e}")
        await callback.answer("Error occurred", show_alert=True)




@router.message(Onboarding.industry)
async def get_industry(message: Message, state: FSMContext):
    await state.update_data(industry=message.text.strip())
    await message.answer("📌 What types of tasks would you like to work on?", reply_markup=task_type_kb)
    await state.set_state(Onboarding.task_type)

@router.message(Onboarding.primary_device)
async def get_primary_device(message: Message, state: FSMContext):
    await state.update_data(primary_device=message.text.strip())
    await message.answer("📌 What types of tasks would you like to work on?", reply_markup=task_type_kb)
    await state.set_state(Onboarding.task_type)

@router.message(Onboarding.task_type)
async def get_task_type(message: Message, state: FSMContext):
    await state.update_data(task_type=message.text.strip())
    await message.answer("🤝 Referral Code (Optional)\n\n" 
    "Were you invited by another contributor?\n\n"
    "If yes, please enter their referral code;" 
    "If none, just type 'none'"
    )
    await state.set_state(Onboarding.referrer)

@router.message(Onboarding.referrer)
async def get_referrer(message: Message, state: FSMContext):
    print(f"🔍 [DEBUG] Onboarding completed for user {message.from_user.id}")
    await state.update_data(referrer=message.text.strip())
   
    user_data = await state.get_data()
    await message.answer("🎉 Thank you! You're now onboarded and ready for tasks.\n\n" \
    "Welcome to the EqualyzAI contributor community! 🌟")
    await message.answer(

        "📝 Your profile:\n"
        f"Name: {user_data.get('auth_name', 'N/A')}\n"
        f"Phone: {user_data.get('auth_phone', 'N/A')}\n"
        f"Gender: {user_data.get('gender', 'N/A')}\n"
        f"Location: {user_data.get('location', 'N/A')}\n"
        f"Languages: {user_data.get('languages', 'N/A')}\n"
        f"Dialect Fluency: {user_data.get('dialect_fluency', 'N/A')}\n"
        f"Education: {user_data.get('education', 'N/A')}\n"
        f"Industry: {user_data.get('industry', 'N/A')}\n"
        f"Primary Device: {user_data.get('primary_device', 'N/A')}\n"
        f"Task Type: {user_data.get('task_type', 'N/A')}\n"
        f"Referrer: {user_data.get('referrer', 'N/A')}"

        "🧠 Next Step: Knowledge Assessment\n\n"
        "Before you start earning, we'll test your knowledge with a few practical tasks:\n"
        "• 📝 Text Annotation\n"
        "• 🎵 Audio Recording\n" 
        "• 🖼️ Image Annotation\n"
        "• 🎥 Video Annotation\n\n"
        "This helps us assign you the right tasks for your skill level!\n\n"

    )

    from src.handlers.task_routes.test_knowledge_router import start_knowledge_assessment
    await start_knowledge_assessment(message, state)

    print(message.from_user.id, "has completed onboarding with data:", user_data)
    
