import asyncio

from aiogram.utils.formatting import Bold, Italic, Text, as_section

from src.config import CHANNEL_ID
from src.loader import bot
from src.utils.llm import llm
from src.utils.text_utils import format_json_str_to_json, format_json_to_table

from .prompt import CONTEST_PROMPT

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
