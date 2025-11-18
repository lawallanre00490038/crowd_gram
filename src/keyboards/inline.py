from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.data.video_tutorials import tutorial_videos


def task_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Accept", callback_data="accept")],
            [InlineKeyboardButton(text="Reject", callback_data="reject")]
        ]
    )


def review_task_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Accept", callback_data="accept")],
            [InlineKeyboardButton(text="Reject", callback_data="reject")]
        ]
    )


def start_task_inline_kb(user_type: str):
    if user_type.lower() == "agent":
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Start Task", callback_data="start_agent_task")],
                [InlineKeyboardButton(
                    text="Redo Task", callback_data="start_agent_redo_task")]
            ]
        )
    elif user_type.lower() == "reviewer":
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Start Task", callback_data="start_reviewer_task"),
                    InlineKeyboardButton(
                 text="Redo Task", callback_data="start_reviewer_redo_task")
                 ]
            ]
        )


def next_task_inline_kb(user_type: str, task_type: str):
    if user_type.lower() == "agent":
        if task_type.lower() == "redo":
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Next REDO Task", callback_data="start_agent_redo_task")],
                    [InlineKeyboardButton(
                        text="Start Task", callback_data="start_agent_task")]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Next Task", callback_data="start_agent_task")]
                ]
            )
    elif user_type.lower() == "reviewer":
        if task_type.lower() == "redo":
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Next REDO Task", callback_data="start_reviewer_redo_task")],
                    [InlineKeyboardButton(
                        text="Start Task", callback_data="start_reviewer_task")]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Next Task", callback_data="start_reviewer_task")]
                ]
            )


def review_task_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Click to Review",
                                  callback_data="review_task")]
        ]
    )


def create_score_kb(param_index: int, scale: int = 5):
    """Generate inline keyboard for scoring"""
    buttons = [
        InlineKeyboardButton(
            text=str(i), callback_data=f"score:{param_index}:{i}")
        for i in range(scale + 1)
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[buttons]
    )


def summary_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Submit Review",
                              callback_data="submit_review")],
        [InlineKeyboardButton(text="🔄 Start Again",
                              callback_data="restart_review")]
    ])


def quiz_options_kb(options: list[str]):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=opt, callback_data=f"opt_{i}")] for i, opt in enumerate(options)]
    )


def project_selection_kb(projects: list[str]):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=proj, callback_data=f"proj_{i}")] for i, proj in enumerate(projects)]
    )


def tutorial_choice_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📺 Yes, show me the tutorials", callback_data="tutorial_yes")],
            [InlineKeyboardButton(text="⏭️ Skip tutorials",
                                  callback_data="skip_tutorials")]
        ]
    )


def g0_to_tutorials_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👍 Yes, I'm ready",
                                  callback_data="tutorial_yes")]
        ]
    )


def accept_support_request(chat_id):
    """Inline Keyboard with JSON string format for callback_data"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Accept", callback_data=f'{{"text": "accept","user_id": {chat_id} }}')  # noqa: E501
                                  ],
        ]
    )


user_type_kb = InlineKeyboardMarkup(
    inline_keyboard=[

        [InlineKeyboardButton(
            text="👤 Sign In", callback_data="registered_yes")],
        [InlineKeyboardButton(text="🆕 Sign Up", callback_data="new_user")],
        # [InlineKeyboardButton(text="🔙 Back to tutorials", callback_data="back_to_tutorials")]
    ]
)

ready_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="👍Yes, I'm ready", callback_data="quiz_yes")],
        [InlineKeyboardButton(
            text="🔁No, show again", callback_data="quiz_no")],
        [InlineKeyboardButton(text="⏭️Skip Quiz",
                              callback_data="skip_quiz")]
    ]
)

set_signup_type_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Email", callback_data="email")],
        # [InlineKeyboardButton(text="Phone Number", callback_data="phone_number")]
    ]
)

new_api_login_type_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Login", callback_data="login")],
        # [InlineKeyboardButton(text="Register", callback_data="register")]
    ]
)


def create_ready_button():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yes I'm ready!",
                                  callback_data="ready_start")]
        ]
    )


def create_task_ready_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ I understand, let's begin!", callback_data="start_real_tasks")]
        ]
    )


def create_task_action_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Start Translation",
                                  callback_data="start_translate")],
            [InlineKeyboardButton(text="Get Another Task",
                                  callback_data="get_next_task")],
        ]
    )


def create_next_task_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Next Task", callback_data="get_next_task")],
            [InlineKeyboardButton(text="Menu", callback_data="view_commands")],
        ]
    )


def yes_no_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Yes", callback_data="org_yes")],
            [InlineKeyboardButton(text="❌ No", callback_data="org_no")]
        ]
    )


def create_account_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Create Account",
                                  callback_data="create_account")],
            [InlineKeyboardButton(text="🔄 Try Again",
                                  callback_data="try_login_again")]
        ]
    )


def tutorial_nav_kb(index: int):
    buttons = []

    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton(
            text="⬅️ Back", callback_data="prev"))
    if index < len(tutorial_videos) - 1:
        nav_row.append(InlineKeyboardButton(
            text="➡️ Next Video", callback_data="next"))
    else:
        nav_row.append(InlineKeyboardButton(
            text="✅ Ready for Task", callback_data="ready_for_task"))

    if nav_row:
        buttons.append(nav_row)

    if index < len(tutorial_videos) - 1:
        buttons.append([InlineKeyboardButton(
            text="⏭️ Skip videos", callback_data="skip_videos")])
    else:
        buttons.append([InlineKeyboardButton(
            text="⏭️ Skip quiz", callback_data="skip_quiz")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def retry_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Try Again", callback_data="retry_reg")]
    ])


def build_predefined_comments_kd(options: list[str], selected: list[str] = None) -> InlineKeyboardMarkup:
    selected = selected or []
    keyboard = []

    for option in options:
        is_selected = "✅" if option in selected else "❌"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{is_selected} {option}",
                callback_data=f"toggle_comment:{option}"
            )
        ])

    # Add a confirm button
    keyboard.append([
        InlineKeyboardButton(
            text="✅ Confirm", callback_data="confirm_comments")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
