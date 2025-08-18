from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states.onboarding import Onboarding
from src.states.authentication import Authentication
from src.keyboards.reply import gender_kb, task_type_kb, industry_kb, language_kb, education_kb, age_kb, writing_ability_kb, phone_quality_kb, favourite_speaker_kb
from src.keyboards.inline import g0_to_tutorials_kb, user_type_kb, ready_kb
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from src.routes.onboarding_routes.quiz import start_quiz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
 
from src.data.country import COUNTRIES  
from src.data.country_state import COUNTRY_STATES
from src.data.language_dialect import LANGUAGE_DIALECTS
from src.utils.keyboard_utils import create_countries_keyboard_reply, create_states_keyboard, create_dialect_keyboard
from src.utils.dialect_format import format_dialects





import re

from pathlib import Path
from aiogram.types import InputFile
from aiogram.types import FSInputFile


router = Router()



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
        "👋 Welcomme to Equalyz Crowd!\n\n"
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
    selection_text = (
        "🔽 Now, please tell us what type of user you are:"
    )
    await message.answer(selection_text)
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
        nav_row.append(InlineKeyboardButton(text="➡️ Next Video", callback_data="next"))
    else:
        nav_row.append(InlineKeyboardButton(text="✅ Ready for Quiz", callback_data="quiz_yes"))
    
    if nav_row:
        buttons.append(nav_row)

    if index < len(tutorial_videos) - 1:
        buttons.append([InlineKeyboardButton(text="⏭️ Skip videos", callback_data="skip_videos")])  
    else:
        buttons.append([InlineKeyboardButton(text="⏭️ Skip quiz", callback_data="skip_quiz")])  
    


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
#         video_file = FSInputFile(path=video_path)  # 
#         print(video_file)
        
#         await message.answer_video(
#             video=video_file,
#             caption=f"Tutorial {index + 1}",
#             reply_markup=tutorial_nav_kb(index)
#         )
#     except FileNotFoundError:
#         await message.answer("⚠️ Video file not found.")


# --- Handle navigation (next/back/ready) ---

@router.callback_query(Tutorial.watching, F.data.in_(["next", "prev", "ready", "skip_videos"]))
async def tutorial_navigation(callback: CallbackQuery, state: FSMContext):
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
   
    elif callback.data == "skip_videos":
        await callback.message.answer("Have you finished watching all the videos?\nStart quiz now?", reply_markup=ready_kb)
     
@router.callback_query(Tutorial.watching, F.data == "skip_quiz")
async def handle_skip_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("⏭️ Quiz skipped!")
    await show_user_type_selection(callback.message, state)

@router.callback_query(Tutorial.watching, F.data.in_(["quiz_yes", "quiz_no"]))
async def quiz_ready_response(callback: CallbackQuery, state: FSMContext):
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

#END TUTO AND QUIZ DISPLAY



#FINISH ONBOARDING

@router.message(Onboarding.location)
async def handle_location_step(message: Message, state: FSMContext):
    """Handle country selection step"""

    user_data = await state.get_data()
    
    if not user_data.get("country_selection_started"):
        await state.update_data(country_selection_started=True, country_page=0)
        await message.answer(
            "🌍 What is your nationality?\n\n"
            "Please select your country:",
            reply_markup=create_countries_keyboard_reply()
        )
        return

    if message.text in COUNTRIES:

        selected_country = message.text.strip()
        await state.update_data(location=selected_country)
        await message.answer(f"✅ Nationality selected: {selected_country}")
        
       
        await message.answer(
            f"🏘️ What state/region do you live in within {selected_country}?\n\n"
            "Please select your state of residence:",
            reply_markup=create_states_keyboard(selected_country)
        )
        await state.set_state(Onboarding.state_residence)
        return
    
    if message.text == "Next ➡️":
        current_page = user_data.get("country_page", 0)
        new_page = current_page + 1
        await state.update_data(country_page=new_page)
        await message.answer(
            "...",
           reply_markup=create_countries_keyboard_reply(page=new_page)
        )
        
        return
    
    if message.text == "⬅️ Previous":
        current_page = user_data.get("country_page", 0)
        new_page = max(0, current_page - 1)
        await state.update_data(country_page=new_page)
        await message.answer(
            "...",
            reply_markup=create_countries_keyboard_reply(page=new_page)
        )
        return




@router.message(Onboarding.state_residence)
async def handle_state_residence(message: Message, state: FSMContext):
    user_data = await state.get_data()
    selected_country = user_data.get("location", "")
    
    # to suppress later id dataset is complete--> handle undefined countries 
    if selected_country not in COUNTRY_STATES:
        #if country not defined 
        await message.answer(f"State of residence: {selected_country} (No states defined)")
        await state.update_data(state_residence=selected_country)
        
       
        await message.answer(
            "⚧ What's your gender? Your privacy is protected - this data is never shared publicly.", 
            reply_markup=gender_kb
        )
        await state.set_state(Onboarding.gender)
        return
    
    #selected countries list
    valid_states = COUNTRY_STATES.get(selected_country, [])
 
    if not valid_states:
        await message.answer(f"State of residence: {selected_country} (No states available)")
        await state.update_data(state_residence=selected_country)
        
        await message.answer(
            "⚧ What's your gender? Your privacy is protected - this data is never shared publicly.", 
            reply_markup=gender_kb
        )
        await state.set_state(Onboarding.gender)
        return
    

    if message.text in valid_states:
        state_residence = message.text.strip()
        await state.update_data(state_residence=state_residence)
        await message.answer(f"State of residence: {state_residence}")
        await message.answer(
            "⚧ What's your gender? Your privacy is protected - this data is never shared publicly.", 
            reply_markup=gender_kb
        )
        await state.set_state(Onboarding.gender)
        return
    
    
    await message.answer(
        f"🏘️ What state/region do you live in within {selected_country}?\n\n"
        "Please select your state of residence:",
        reply_markup=create_states_keyboard(selected_country)
    )
    
  
@router.message(Onboarding.gender)
async def get_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text.strip())
    await message.answer("How old are you? Please select your age range", reply_markup=age_kb)
    await state.set_state(Onboarding.age_range)



@router.message(Onboarding.age_range)
async def get_age(message: Message, state: FSMContext):
    await state.update_data(age_range=message.text.strip())

    await state.update_data(selected_languages=[])

    await message.answer("🎓 What's your highest level of education?", reply_markup=education_kb)
    await state.set_state(Onboarding.education)



@router.message(Onboarding.education)
async def get_education(message: Message, state: FSMContext):
    
    valid_options = ["High School Diploma", "Bachelor's Degree", "Master's Degree", "Doctorate Degree", "SSCE/WAEC", "Other"]

    if message.text in valid_options:
        await state.update_data(education=message.text.strip())

        await message.answer(f"✅ Education level selected: {message.text}")

        await message.answer("💼 What field do you work in?", reply_markup=industry_kb)
        await state.set_state(Onboarding.industry)
    else:

        await message.answer(
            "Please select a valid education level from the options provided.",
            reply_markup=education_kb
        )
 

@router.message(Onboarding.industry)
async def get_industry(message: Message, state: FSMContext):
    await state.update_data(industry=message.text.strip())
    await message.answer("🗣️ Which languages do you speak fluently?\n"
        "Select up to 2 languages. Click each language to select.",
        reply_markup=language_kb)  
        
    await state.set_state(Onboarding.languages) 
    


@router.message(Onboarding.languages, F.text == "✅ Done")
async def language_selection_done(message: Message, state: FSMContext):
    user_data = await state.get_data()
    selected_languages = user_data.get("selected_languages", [])
    
    if len(selected_languages) >= 1:
        await state.update_data(languages=", ".join(selected_languages))
        await message.answer("✅ Selection confirmed!")
        
        await state.update_data(
            dialect_selection_index=0,  
            selected_dialects={} 
        )
        await start_dialect_selection(message, state)
       
    else:
        await message.answer("Please select at least one language before continuing.")

@router.message(Onboarding.languages)
async def get_language(message: Message, state: FSMContext):
    all_languages = ["English", "French", "Fulani", "Hausa", "Hindi", "Igbo", "Pidgin", "Punjabi", "Shona", "Swahili", "Yoruba"]
    

    if message.text in all_languages:
        user_data = await state.get_data()
        selected_languages = user_data.get("selected_languages", [])

        def create_language_keyboard_with_done():
            kb_buttons = language_kb.keyboard
            kb_buttons_with_done = [row[:] for row in kb_buttons]
            kb_buttons_with_done.append([KeyboardButton(text="✅ Done")])
            return ReplyKeyboardMarkup(keyboard=kb_buttons_with_done, resize_keyboard=True, one_time_keyboard=True)
        
        if message.text in selected_languages:
           
            selected_languages.remove(message.text)
            await message.answer(f"❌ Removed: {message.text}")
        else:
            
            if len(selected_languages) >= 2:
                await message.answer("❌ You can only select up to 2 languages.")
                return # Stop here if max reached
            selected_languages.append(message.text)
            await message.answer(f"Added: {message.text}")
        
        await state.update_data(selected_languages=selected_languages)
        
        num_selected = len(selected_languages)
        if num_selected == 0:
            await message.answer("🗣️ Which languages do you speak fluently?\nSelect up to 2 languages.", reply_markup=language_kb)
        elif num_selected == 1:
            await message.answer(" One language selected.\nSelect a second language or press '✅ Done' to continue.", reply_markup=create_language_keyboard_with_done())
        elif num_selected == 2:
            #go to next step if selection of 2 
            await state.update_data(languages=", ".join(selected_languages))
            await message.answer(f"✅ Two languages selected: {', '.join(selected_languages)}. Proceeding to the next step!")
            
            
            await state.update_data(
                dialect_selection_index=0,
                selected_dialects={}
            )
            await start_dialect_selection(message, state)
    else:
        await message.answer("🗣️ Which languages do you speak fluently?\nSelect up to 2 languages.", reply_markup=language_kb)


#helpers for dialects selection:
async def start_dialect_selection(message: Message, state: FSMContext):
    #start selection
    user_data = await state.get_data()
    selected_languages = user_data.get("selected_languages", [])
    current_index = user_data.get("dialect_selection_index", 0)
    
    if current_index < len(selected_languages):
        current_language = selected_languages[current_index]
        await ask_dialect_for_language(message, state, current_language)
    else:
        await finish_dialect_selection(message, state)

async def ask_dialect_for_language(message: Message, state: FSMContext, language: str):

    await message.answer(
        f"🗣️ Select the type of **{language}** you speak in your hometown:",
        reply_markup=create_dialect_keyboard(language)
    )
    await state.set_state(Onboarding.dialect_selection)

async def finish_dialect_selection(message: Message, state: FSMContext):
    
    user_data = await state.get_data()
    selected_dialects = user_data.get("selected_dialects", {})
    
    #summary of dialect selected
    dialect_summary = []
    for language, dialect in selected_dialects.items():
        dialect_summary.append(f"{language}: {dialect}")
    
    await state.update_data(dialects=selected_dialects)
    await message.answer(f"✅ Dialects selected:\n" + "\n".join(dialect_summary))
    
    #go to next step
    await message.answer("📌 What kind of data do you want to give?", reply_markup=task_type_kb)
    await state.set_state(Onboarding.task_type)
        


#handler for selection dialect
@router.message(Onboarding.dialect_selection)
async def get_dialect(message: Message, state: FSMContext):
    """Gérer la sélection d'un dialecte"""
    user_data = await state.get_data()
    selected_languages = user_data.get("selected_languages", [])
    current_index = user_data.get("dialect_selection_index", 0)
    selected_dialects = user_data.get("selected_dialects", {})
    

    if current_index >= len(selected_languages):
        await finish_dialect_selection(message, state)
        return
    
    current_language = selected_languages[current_index]
    valid_dialects = LANGUAGE_DIALECTS.get(current_language, [])
    
    # "Not listed" selected
    if message.text == "Not listed here":
        await message.answer(" Write your hometown language below:")
        await state.update_data(awaiting_manual_dialect=True, current_dialect_language=current_language)
        return
    
    # user can write 
    if user_data.get("awaiting_manual_dialect"):
        dialect = message.text.strip()
        language_for_manual = user_data.get("current_dialect_language")
        selected_dialects[language_for_manual] = dialect
        
        await state.update_data(
            selected_dialects=selected_dialects,
            awaiting_manual_dialect=False,
            current_dialect_language=None
        )
        
        await message.answer(f"✅ {language_for_manual} dialect: {dialect}")
        
        # go to next language
        next_index = user_data.get("dialect_selection_index", 0) + 1
        await state.update_data(dialect_selection_index=next_index)
        await start_dialect_selection(message, state)
        return
    
    # is dialect valid?
    if message.text in valid_dialects:
        selected_dialect = message.text.strip()
        selected_dialects[current_language] = selected_dialect
        
        await state.update_data(selected_dialects=selected_dialects)
        await message.answer(f"✅ {current_language} dialect: {selected_dialect}")
        
        # next step
        next_index = current_index + 1
        await state.update_data(dialect_selection_index=next_index)
        await start_dialect_selection(message, state)
        return
    
    # unrecognised message - ask question again
    await message.answer(
        f"🗣️ Please select a valid dialect for **{current_language}**:",
        reply_markup=create_dialect_keyboard(current_language)
    )


@router.message(Onboarding.task_type, F.text == "✅ Done")
async def data_type_selection_done(message: Message, state: FSMContext):
    user_data = await state.get_data()
    selected_data_types = user_data.get("selected_data_types", [])
    
    if len(selected_data_types) >= 1:
        await state.update_data(task_type=", ".join(selected_data_types))
        await message.answer("✅ Data type selection confirmed!")
        
        if "📝Text" in selected_data_types:
            await message.answer("✍️ Can you write in your language?", reply_markup=writing_ability_kb)
            await state.set_state(Onboarding.text_writing_ability)
        elif "🎤Audio" in selected_data_types:
            await message.answer("📱 How good is your phone's mouthpiece and speaker?", reply_markup=phone_quality_kb)
            await state.set_state(Onboarding.phone_quality)
    else:
        await message.answer("Please select at least one data type before continuing.")

#same logic as select languages 
@router.message(Onboarding.task_type)
async def get_task_type(message: Message, state: FSMContext):
    all_data_types = ["📝Text", "🎤Audio"]
    
    #first time initialized
    if message.text not in all_data_types:
        await state.update_data(selected_data_types=[])
        await message.answer("📌 What kind of data do you want to give?\nSelect one or both.", reply_markup=task_type_kb)
        return
    
    #for selection of multiple 
    user_data = await state.get_data()
    selected_data_types = user_data.get("selected_data_types", [])

    def create_data_type_keyboard_with_done():
        kb_buttons = task_type_kb.keyboard
        kb_buttons_with_done = [row[:] for row in kb_buttons]
        kb_buttons_with_done.append([KeyboardButton(text="✅ Done")])
        return ReplyKeyboardMarkup(keyboard=kb_buttons_with_done, resize_keyboard=True, one_time_keyboard=True)
    
    if message.text in selected_data_types:
        selected_data_types.remove(message.text)
        await message.answer(f"❌ Removed: {message.text}")
    else:
        selected_data_types.append(message.text)
        await message.answer(f"✅ Added: {message.text}")
    
    await state.update_data(selected_data_types=selected_data_types)
    
    num_selected = len(selected_data_types)
    if num_selected == 0:
        await message.answer("📌 What kind of data do you want to give?\nSelect one or both.", reply_markup=task_type_kb)
    elif num_selected == 1:
        await message.answer("One data type selected.\nSelect another or press '✅ Done' to continue.", reply_markup=create_data_type_keyboard_with_done())
    elif num_selected == 2:
        await state.update_data(task_type=", ".join(selected_data_types))
        await message.answer(f"✅ Both selected: {', '.join(selected_data_types)}!")
        await message.answer("✍️ Can you write in your language?", reply_markup=writing_ability_kb)
        await state.set_state(Onboarding.text_writing_ability)


@router.message(Onboarding.text_writing_ability)
async def handle_text_writing_ability(message: Message, state: FSMContext):
    await state.update_data(text_writing_ability=message.text.strip())
    await message.answer(f"✅ Writing ability: {message.text}")
    
     
    
    user_data = await state.get_data()
    selected_data_types = user_data.get("selected_data_types", [])
    
    # if audio is also selected
    if "🎤Audio" in selected_data_types:
        await message.answer(
            "📱 How good is your phone's mouthpiece and speaker?",
            reply_markup=phone_quality_kb
        )
        await state.set_state(Onboarding.phone_quality)
    else:
        # only text selected go directly to refferer
        await message.answer(
            "🤝 Referral Code (Optional)\n\n"
            "Were you invited by another contributor?\n\n"
            "If yes, please enter their referral code; "
            "If none, just type 'none'"
        )
        await state.set_state(Onboarding.referrer)

@router.message(Onboarding.phone_quality)
async def handle_phone_quality(message: Message, state: FSMContext):
    await state.update_data(phone_quality=message.text.strip())
    await message.answer(f"Phone quality: {message.text}")
    
    await message.answer(
        "🔊 What is your favourite speaker?",
        reply_markup=favourite_speaker_kb
    )
    await state.set_state(Onboarding.favourite_speaker)

@router.message(Onboarding.favourite_speaker)
async def handle_favourite_speaker(message: Message, state: FSMContext):
    await state.update_data(favourite_speaker=message.text.strip())
    await message.answer(f"Favourite speaker: {message.text}")
    
    await message.answer(
        "🤝 Referral Code (Optional)\n\n"
        "Were you invited by another contributor?\n\n"
        "If yes, please enter their referral code; "
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
        f"Nationality: {user_data.get('location', 'N/A')}\n"
        f"State of Residence: {user_data.get('state_residence', 'N/A')}\n" 
        f"Languages: {user_data.get('languages', 'N/A')}\n"
        f"Dialects: {format_dialects(user_data.get('dialects', {}))}\n" 
        f"Education: {user_data.get('education', 'N/A')}\n"
        f"Industry: {user_data.get('industry', 'N/A')}\n"
        f"Data Type: {user_data.get('task_type', 'N/A')}\n"
        f"Referrer: {user_data.get('referrer', 'N/A')}"
    )
    
    from src.routes.task_routes.test_knowledge_router import handle_start_knowledge_assessment
    await handle_start_knowledge_assessment(message, state)

    print(message.from_user.id, "has completed onboarding with data:", user_data)
    
