PROJECT_SELECTION_MESSAGE = "Please select a project to work on:"

PROJECT_WELCOME_MSG = {
    "intro": (
        "👋 Welcome to the <b>{project_name}</b> project!\n\n\n"
        "🎯 You’re about to contribute valuable data to this initiative."
    ),

    "stats": (
        "💰 <b>{user_type} Coin:</b> {user_coin}\n"
    ),

    "ready": (
        "🚀 You can now start working on your assigned tasks.\n"
        "Use the buttons below to begin!"
    ),

    "no_tasks": (
        "⚠️ There are currently no available tasks in this project.\n"
        "Please check back later or select another project."
    ),

    "resuming": (
        "👋 Welcome back to <b>{project_name}</b>!\n"
        "You have unfinished tasks waiting.\n\n"
        "💪 Let’s pick up where you left off."
    ),

    "completed": (
        "🎉 Congratulations! You’ve completed all your tasks in <b>{project_name}</b>.\n"
        "Thank you for your contribution! 🏅"
    ),
}

START_TASK_PROMPT = "Click the button below to start your first task!"

PROJECT_FULL_WELCOME_MSG = (
    PROJECT_WELCOME_MSG['intro'].format(project_name="{project_name}")
    + "\n\n"
    + PROJECT_WELCOME_MSG['stats'].format(user_type="{user_type}", user_coin="{user_coin}")
    + "\n\n"
    + PROJECT_WELCOME_MSG['ready']
)

