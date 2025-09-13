#------------------------start--------------------------
WELCOME_MESSAGE=(    
        "👋 Welcomme to Equalyz Crowd!\n\n"
        "We're building the future of AI by collecting multilingual data across Africa.\n\n"
        "As a contributor/agent, you'll help train AI models and earn money for quality work.\n\n"
        "Let's begin! 🚀"   
    )



# ---------------- TUTORIAL ----------------
TUTORIAL_MSG = {
    "intro": (
        "🧠 You will be guided through a series of videos to learn about the basics of data collection and annotation.\n\n"
        "Would you like to watch the tutorial videos?"
    ),
    
    "start": ("📺 Great! Let's start with the tutorial videos."),
    
    "skip_ready": ("Have you finished watching all the videos?\\nStart quiz now?"),
    
    
    "video_not_found": ("⚠️ Video file not found."),
}

# ---------------- USER TYPE ----------------
USER_TYPE_MSG = {
    "selection": ("🔽 Now, please tell us what type of user you are:"),
    
    "option": ("Please select an option:")
}

# ---------------- LOCATION ----------------
LOCATION_MSG = {
    "country_prompt": (
        "🌍 What is your nationality?\n\n"
        "Please select your country:"
    ),

      
    "state_prompt": (
        "🏘️ What state/region do you live in within {country}?\n\n"
        "Please select your state of residence:"
    ),

    "lga_prompt": (
        "🏘️ What lga do you live in within {state}?\n\n"
        "Please select your Local Goverment:"
    ),
    
    "state_selected": ("State of residence: {state}"),
    
    "state_undefined": ("State of residence: {country} (No states defined)"),
    
    "state_unavailable": ("State of residence: {country} (No states available)"),
    
    "pagination": ("..."),

    "select_country": ("Please select a valid country from the list."),

    "select_state": ("Please select a valid state for {selected_country}:"),
}

# ---------------- PERSONAL INFO ----------------
PERSONAL_MSG = {
    "gender": (
        "⚧ What's your gender? Your privacy is protected - this data is never shared publicly."
    ),
    
    "age": ("How old are you? Please select your age range"),
    
    "education": ("🎓 What's your highest level of education?"),
    
    
    "education_invalid": ("Please select a valid education level from the options provided."),
    
    "industry": ("💼 What field do you work in?"),

    "education_level_selected": ("✅ Education level selected: {level}"),
    
    "Field": "💼 What field do you work in?"
    
}

# ---------------- LANGUAGES ----------------
LANGUAGE_MSG = {
    "selection_prompt": (
        "🗣️ Which languages do you speak fluently?\n\n"
        "Select up to 2 languages. Click each language to select/deselect."
    ), 

    "selection_another": (
        "🗣️ Select another language you speak fluently\n\n"
        "Click another language to select/deselect it \n\n"
        "Click ✅ Done to continue"
    ),  

    "max_reached": ("❌ You can only select up to 2 languages.\n\n"
                    "Click ✅ Done to continue or Deselect a previously selected language"),
    
    "added": ("Added: {language}"),
    
    "removed": ("❌ Removed: {language}"),
    
    "one_selected": (
        "One language selected.\n"
        "Select a second language or press '✅ Done' to continue."
    ),
    
    "two_selected": (
        "✅ Two languages selected: {languages}. Proceeding to the next step!"
    ),
    
    "selection_confirmed": ("✅ Language Selection Complete")
}

# ---------------- DIALECTS ----------------
DIALECT_MSG = {
    "selection_prompt": ("🗣️ Select the type of <b>{language}</b> you speak in your hometown:"),
    
    "manual_entry": ("Write your hometown language below:"),
    
    "invalid_selection": ("🗣️ Please select a valid dialect for **{language}**:"),
    
    "selected": ("✅ {language} dialect: {dialect}"),
    
    "summary": ("✅ Dialects selected:\n{dialects}")
}

# ---------------- TASK TYPE ----------------
TASK_TYPE_MSG = {
    "prompt": ("📌 What kind of data do you want to give?"),
    
    "multi_prompt": ("📌 What kind of data do you want to give?\nSelect one or both."),
    
    "min_selection": ("Please select at least one data type before continuing."),
    
    "added": ("✅ Added: {data_type}"),
    
    "removed": ("❌ Removed: {data_type}"),
    
    "one_selected": (
        "One data type selected.\n"
        "Select another or press '✅ Done' to continue."
    ),
    
    "both_selected": ("✅ Both selected: {data_types}!"),
    
    "selection_confirmed": ("✅ Data type selection confirmed!")
}

# ---------------- ABILITIES ----------------
ABILITY_MSG = {
    "writing": ("✍️ Can you write in your language?"),
    
    "phone_quality": ("📱 How good is your phone's mouthpiece and speaker?"),
    
    "favourite_speaker": ("🔊 What is your favourite speaker?"),
    
}

# ---------------- REFERRAL ----------------
REFERRAL_MSG = {
    "prompt": (
        "🤝 Referral Code (Optional)\n\n"
        "Were you invited by another contributor?\n\n"
        "If yes, please enter their referral code; "
        "If none, just type 'none'"
    )
}

# ---------------- COMPLETION ----------------
COMPLETION_MSG = {
    "success": (
        "🎉 Thank you! You're now onboarded and ready for tasks.\n\n"
        "Welcome to the EqualyzAI contributor community! 🌟"
    ),
    
   
}

QUIZ_MSG = {
    "quiz_skip": ("⏭️ Quiz skipped!"),
    
    "begin_quiz": ("✅ Great! Let's begin the short quiz.")}