import asyncio
import logging

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

from .prompt import CONTEST_PROMPT, WELLNESS_PROMPT

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
