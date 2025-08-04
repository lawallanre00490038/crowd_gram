import asyncio
import logging
import re

from aiogram import types
from aiogram.utils.formatting import (
    Bold,
    Italic,
    Text,
    Underline,
    as_section,
)

from src.config import CHANNEL_ID
from src.loader import bot
from src.utils.llm import llm
from src.utils.text_utils import format_json_str_to_json, format_json_to_table

from .prompt import CONTEST_PROMPT, TRIVIA_PROMT, WELLNESS_PROMPT

json_str = """
[
  {
    "#": 1,
    "N": "Alice",
    "TT": 20,
    "TC": 19,
    "CE": 150,
    "R": 4.9
  },
  {
    "#": 2,
    "N": "Bob",
    "TT": 18,
    "TC": 16,
    "CE": 130,
    "R": 4.7
  },
  {
    "#": 3,
    "N": "Charlie",
    "TT": 17,
    "TC": 15,
    "CE": 120,
    "R": 4.5
  },
  {
    "#": 4,
    "N": "Diana",
    "TT": 15,
    "TC": 13,
    "CE": 110,
    "R": 4.3
  },
  {
    "#": 5,
    "N": "Ethan",
    "TT": 14,
    "TC": 12,
    "CE": 100,
    "R": 4.1
  }
]
"""

json_data_broadcast_project_insert = [{
      "Task": "audio",
      "Cat": "static",
      "Language": "Yoruba",
      "Count": 4
   }]

json_data_broadcast_policy_insert = """
    [
    {
      "announcement_title": "Upcoming Security Policy Update",
      "body": "To enhance account protection, we're introducing a mandatory two-factor authentication policy starting August 15. Please ensure your mobile number is up to date in your profile settings."
    },
    {
      "announcement_title": "Payment Policy Update",
      "body": "We're adding additional forms of payment including - PayPal, Venmo, CashApp, & Zelle."
    }
    ]
"""  # noqa: E501

json_data_broadcast_trainings_insert = """
    [
    {
      "announcement_title": "New User Onboarding Course Available",
      "body":  "We've launched an updated onboarding training for new users. This 45-minute course walks through the core features and best practices for getting started quickly."
    },
    {
      "announcement_title": "Interface Training Available",
      "body": "To allow better transition into the platform we've provided a new training to allow a new user to become more comfortable. The training is 1-hour and self-paced."
    }
    ]
"""  # noqa: E501




async def send_leaderboard_weekly():
    """Send Weekly Leaderboard to Channel"""

    delay = 604800  # 7 days
    while True:
        # logic to retrieve data from backend

        # format json
        json_data = format_json_str_to_json(json_str=json_str)

        table = format_json_to_table(json_data=json_data)

        text = "🏆 <b>Leaderboard This Week</b>\n<pre>{}</pre>".format(table)

        await bot.send_message(chat_id=CHANNEL_ID, text=text)

        await asyncio.sleep(delay=delay)


async def get_top_agent_this_week():

    delay = 604800

    while True:
        # logic to retrieve data from backend

        # format json

        json_object = format_json_str_to_json(json_str=json_str)

        max_task_completed = 0
        top_agent_index = None

        for i, data in enumerate(json_object):
            if data["TC"] >= max_task_completed:
                max_task_completed = data["TC"]
                top_agent_index = i

        top_agent = json_object[top_agent_index]

        agent_text = (
            f"Name: {top_agent['N']}\n"
            f"Task Completed: {top_agent['TC']}\n"
            f"Coins Earned: {top_agent['CE']}\n"
            f"Rating: {top_agent['R']}"
        )

        text = f"🏆 <b>Top Agent This Week</b>\n\n{agent_text}"

        await bot.send_message(chat_id=CHANNEL_ID, text=text)

        await asyncio.sleep(delay=delay)



async def send_monthly_contest():

    delay = 2592000  # 30 days
    while True:
        try:
            response = await llm.ainvoke(
                CONTEST_PROMPT.format()
            )

            json_object = format_json_str_to_json(response.content)[0]

            title = json_object["Contest Title"]

            task_instruction = json_object["Task Instruction"]

            submission_requirements = json_object["Submission Requirements"]

            judging_criteria = json_object["Judging Criteria"]

            social_media_instruction = json_object["Social Media Instruction"]

            deadline = json_object["Deadline"]

            reward = json_object["Reward"]

            result = as_section(
                Bold(f"📢 {title}\n\n"),
                Text(Bold("📝 Task Instruction"), f"\n{task_instruction}\n\n"),
                Text(Bold("📦 Submission Requirements"),
                     f"\n{submission_requirements}\n\n"),
                Text(Bold("⚖️ Judging Criteria\n"),
                     f"{'\n'.join(f"- {criteria}" for criteria in judging_criteria)}\n\n"),  # noqa: E501
                Italic(f"{social_media_instruction}\n\n"),
                Text(Bold("📅 Deadline"), f"\n{deadline}\n\n"),
                Text(Bold("🏆 Reward"), f"\n{reward}")
            )

            await bot.send_message(**result.as_kwargs(), chat_id=CHANNEL_ID)

        except Exception as e:
            print(f"Error sending contest message: {e}")

        await asyncio.sleep(delay)

#@{name}.post(/projects)
async def broadcast_new_projects():
    """Broadcast New Projects"""
    # TODO Logic to recieve and retrieve json from backend request

    try:
        structure = format_json_to_table(json_data_broadcast_project_insert)
        context = f"📢<b>Check out these New Projects</b>  \n<pre>{structure}</pre>"
        await bot.send_message(chat_id=CHANNEL_ID, text=context)
    except Exception as err:
        logging.error(f"Community-Broadcast Projects Router Error: Details: {err}")

# @{name}.post("/trainings")
async def broadcast_new_trainings():
    """Broadcast New Trainings"""
    # TODO Logic to recieve and retrieve json from backend request
    try:
            response_obj = format_json_str_to_json(json_data_broadcast_trainings_insert)
            items = []
            for i, content in enumerate(response_obj):
                body = Text(
                    Bold(Text(i+1), ". "),
                    Bold(content['announcement_title']),
                    '\n\n',
                    content["body"],
                    '\n\n'
                )
                items.append(body)
            result = as_section(
                Text(Underline(Bold("📢 Check out these New Policy Announcements\n"))),
                Text(*items, sep="\n\n")
            )

            await bot.send_message(**result.as_kwargs(), chat_id=CHANNEL_ID)
    except Exception as err:
        logging.error(f"Community-Broadcast Policies Router Error: Details: {err}")  # noqa: E501


# @{name}.post("/policies")
async def broadcast_new_policies():
    """Broadcast New Policies"""
    # TODO Logic to receive and retrieve json from backend request

    try:
            response_obj = format_json_str_to_json(json_data_broadcast_policy_insert)
            items = []
            for i, content in enumerate(response_obj):
                body = Text(
                    Bold(Text(i+1, ". ")),
                    Bold(content['announcement_title']),
                    '\n\n',
                    content["body"],
                    '\n\n'
                )
                items.append(body)
            result = as_section(
                Text(Underline(Bold("📢 Check out these New Policy Announcements\n"))),
                Text(*items, sep="\n\n")
            )

            await bot.send_message(**result.as_kwargs(), chat_id=CHANNEL_ID)
    except Exception as err:
        logging.error(f"Community-Broadcast Policies Router Error. Details: {err}")



theme_history = []
async def send_wellness_weekly():
    """Send Weekly Wellness Activities"""
    delay = 604800 # weekly delay
    title = ""
    activities = ""
    while True:
        try:

          chat_response = await llm.ainvoke(
              WELLNESS_PROMPT.format(theme_history=str(theme_history))
          )

          response_obj = format_json_str_to_json(chat_response.content)[0]


          items = []
          try:
            if response_obj["Title"] and response_obj["Activities"]:
                title = response_obj["Title"]
                activities = response_obj["Activities"]
                for i, activity in enumerate(activities):
                    body = Text(
                        Bold(Text(i+1, ". ")),
                        Bold('Activity: '),
                        Bold("⚡", activity['Activity Name']),
                        '\n',
                        activity['Activity Instructions'],
                        '\n\n'
                    )
                    items.append(body)
          except Exception as err:
              logging.error(
                  f"Community Error Wellness Router Error: Details {err}")

          result = as_section(
              Text(Underline(Bold("🧘‍♀️ Wellness Activities of the Week\n"))),
              Text(Bold("Theme: ", title, "\n\n")),
              Text(*items, sep="\n")
          )
          theme_history.append(title)
          await bot.send_message(**result.as_kwargs(), chat_id=CHANNEL_ID)
          await asyncio.sleep(delay=delay)

        except Exception as err:
            logging.error(
                f"Community Error Wellness Router Error: Details: {err}")




#<==============================Trivia Questions==========================>



"""Global variables for trivia management"""
current_trivia = None
current_trivia_message_id = None
user_answers = {}

"""Format trivia questions into a single message with options."""

def format_all_trivia(trivia_list):
    """Format 4 trivia questions + options as one HTML string message."""
    message = "<b> Trivia Time! Answer all 4 questions below:</b>\n\n"
    option_labels = ['A', 'B', 'C', 'D']

    for idx, trivia in enumerate(trivia_list, start=1):
        question = trivia.get("q")
        options = trivia.get("options", [])
        message += f"<b>{idx}. {question}</b>\n"
        for label, option_text in zip(option_labels, options):
            clean_option = re.sub(r"^\d+\.\s*", "", option_text)
            message += f"{label}. {clean_option}\n"
        message += "\n"

    message += (
        " Please reply to this message in this exact format:\n"
        "<code>1. A\n2. B\n3. C\n4. D</code>\n\n"
        "<b>You have 1 hour to submit your answers!</b>"
    )
    return message

"""Parse user response text into a list of uppercase letters (A-D). """

def parse_user_response(text: str):
    """
    Parse user answer text like:
      1. C
      2. A
      3. D
      4. B
    Returns a list of uppercase letters, or None if parsing fails.
    """
    lines = text.strip().splitlines()
    answers = []

    for line in lines:
        match = re.match(r"^\s*\d+\.\s*([A-Da-d])\s*$", line)
        if match:
            answers.append(match.group(1).upper())
        else:
            return None

    return answers if answers else None

"""Send trivia results to channel after collecting answers."""

async def send_trivia_results():
    """
    Evaluate all collected answers and announce winners.
    """
    global current_trivia, user_answers

    if not current_trivia:
        return

    option_labels = ['A', 'B', 'C', 'D']
    correct_letters = []
    for q in current_trivia:
        correct_answer = q.get("a")
        options = q.get("options", [])
        try:
            idx = options.index(correct_answer)
            correct_letters.append(option_labels[idx])
        except ValueError:
            correct_letters.append("?")

    # Compose correct answers message
    answer_msg = "<b>Correct Answers:</b>\n"
    for i, letter in enumerate(correct_letters, start=1):
        answer_msg += f"{i}. {letter}\n"

    # Find winners who got all answers correct
    winners = []
    for user_id, data in user_answers.items():
        if data.get("answers") == correct_letters:
            winners.append((user_id, data.get("username", "User")))

    winners = winners[:10]  # Limit to top 10 winners

    if winners:
        winner_text = (
            "\n🎉 <b>Congratulations to the Top 3 Participants who got all "
            "answers correct:</b>\n"
        )
        for rank, (uid, uname) in enumerate(winners, start=1):
            winner_text += f"{rank}. @{uname}\n"
    else:
        winner_text = "\n😞 No one answered all questions correctly this time."

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=answer_msg + winner_text,
        parse_mode="HTML"
    )

# === Main Trivia Loop ===

async def daily_trivia():
    """
    Runs the trivia loop indefinitely:
    - Fetch 4 questions
    - Send them in one message, record message ID
    - Wait 1 hour for answers
    - Evaluate and announce winners
    - Wait 24 hours before next trivia
    """
    global current_trivia, user_answers, current_trivia_message_id

    while True:
        try:
            # Get trivia questions from LLM (ensure your prompt needs no .format())
            response = await llm.ainvoke(TRIVIA_PROMT.format())
            trivia_list = format_json_str_to_json(response.content)

            if not trivia_list or len(trivia_list) < 4:
                logging.error(
                    "Failed to load 4 trivia questions. Retrying in 1 hour..."
                )
                await asyncio.sleep(3600)
                continue

            user_answers.clear()
            current_trivia = trivia_list[:4]

            # Send trivia questions to channel
            # Note: Uncomment if you want to see what happens when a person gets
            # everything correct. The correct answers will be sent first before
            # the trivia questions.
            """await send_trivia_results()"""

            trivia_message = format_all_trivia(current_trivia)
            sent_message = await bot.send_message(
                chat_id=CHANNEL_ID,
                text=trivia_message,
                parse_mode="HTML"
            )

            current_trivia_message_id = sent_message.message_id


            await asyncio.sleep(3600)  # 1 hour in seconds

            # Announce results
            await send_trivia_results()

        except Exception:
            logging.exception("Trivia session failed.")


        await asyncio.sleep(86400)  # 24 hours in seconds





# === Message Handler ===#

async def handle_message(message: types.Message):
    """
    Handles incoming messages to collect trivia answers.
    Requires user to reply to trivia question message.
    """

     # Note: Comment if you want to see what happens when a person gets everything
     # correct. The correct answers will be sent first before the trivia questions.
    if not current_trivia:

        return



    if (
        not message.reply_to_message
        or message.reply_to_message.message_id != current_trivia_message_id
    ):

        return

    answers = parse_user_response(message.text)
    if not answers:
        await message.reply(
            "Please use this exact format:\n\n"
            "1. A\n2. B\n3. C\n4. D",
            parse_mode="Markdown"
        )
        return

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    user_answers[user_id] = {
        "username": username,
        "answers": answers
    }
