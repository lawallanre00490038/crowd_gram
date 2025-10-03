# ---------------- LOGIN ----------------
LOGIN_MSG = {
    "login":(
            # "🎉 Welcome back!\n\n"
            "Please select email to login:"
    ),


    "enter_email": ("🔄 Please enter your email"),
    "enter_phone": "🔄 Please enter your phone number",
    "register": "To register, please enter your name",

    "success": (
        "✅ Login successful!\n\n🎉 Welcome back to {name}\n\n"
        "You can now access your tasks and continue earning."
    ),

    "success_2": (
        "✅ Login successful!\n\n🎉 Welcome back,  {name}\n\n"
        "You can now access your tasks and continue earning."
    ),
    "fail": (
        "❌ Login failed! Please check your credentials and try again.\n\n"
    ),
    "login": "Please enter your email to login:"


}

LOGOUT = {
    "logout":(
        "You have been logged out. To log in again, use /login"
    ),
}

EXIT = {
    "exit":(
        "You have been Exited the platform. To Start again, use /start"
    ),
}

# ---------------- ONBOARDING / WELCOME ----------------
ONBOARDING_MSG = {
    "welcome": (
        "Great! Let's get you set up! 👋 Welcome to Equalyz Crowd!\n\n"
        "This quick onboarding sets up your profile so we can match you with the best tasks.\n\n"
        "Let's begin! 🚀"
    ),

    "account_created": (
        "✅ Account created successfully!\n\n"
        "Please Input OTP sent to you"
    ),
     "organization": ("Are you part of an organization?"),

    "org_selection": (
        "🏢 Please select your organization:\n\n"
            "Choose from the list below:"),
            
    "name_input": (
            "👤 What's your full name?\n\n"
            "This will be used for your account registration."
        ),

    "set_signup_type": (
        "Please set your signup type \n\n"
    ),

    "wrong_otp": {
        "❌ Please enter the right OTP\n"
        "Please enter the right OTP"
    },

    "right_otp": (
        "🎉 Welcome to Equalyz Crowd!\n\n"
        "Now let's complete your profile..."
    ),

    "error_occured": (
        "An Error Occured: {error}"
    )
}

# ---------------- EMAIL ----------------
EMAIL_MSG= {
    "prompt": (
        "📧 What's your email address?\n\n"
        "We'll use this for account verification and important updates."
    ),

    "invalid": (
        "❌ Please enter a valid email address.\n"
        "Example: user@example.com"
    ),
}

# ---------------- PHONE ----------------
PHONE_MSG = {
    "prompt": (
        "📱 What's your phone number?\n\n"
        "Format: +234XXXXXXXXX (include country code)"
    ),
    "invalid": (
        "❌ Invalid phone number format.\n\n"
        "Please use international format: +CountryCodeNumber\n"
        "Examples: +234803123456, +1555123456, +33123456789\n\n"
        "Try again:"
    ),
}

# ---------------- PASSWORD ----------------
PASSWORD_MSG= {
    "prompt": (
        "🔒 Create a secure password:\n\n"
        "Password should be at least 8 characters long."
    ),
    "uppercase": "It must include at least one uppercase letter.",
    "special_character": "It must include at least one special character.",
    "password": "It must include at least one number.",
    "long_characters": "It must be at least 8 characters long.",
    "weak": (
        "❌ Password too weak.\n\n"
        "{problems}\n\n"
        "Please try again:"
    ),
    "confirm": (
        "🔒 Please confirm your password:\n\n"
        "Re-enter the password you created."
    ),
    "mismatch": (
        "❌ Passwords don't match! Please try again:\n\n"
        "Re-enter your password:"
    ),
    "enter_password": ("🔒 Please enter your password:"),
}
