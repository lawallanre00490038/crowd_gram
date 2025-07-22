import asyncio
import json
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from prettytable import PrettyTable
from src.config import CHANNEL_ID
from src.loader import bot


router = Router()
json_data = """
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


def format_json_to_table(json_data: str) -> str:
    try:
        data = json.loads(json_data)

        full_headers = []
        full_values = []
        for item in data:
            headers = []
            values = []
            for key in item.keys():
                header = key
                if isinstance(item[key], dict):
                    for key_2 in item[key]:
                        header += "/" + key_2
                        value = item[key][key_2]
                        headers.append(value)
                        values.append(value)

                else:
                    value = item[key]
                    headers.append(header)
                    values.append(value)
            full_headers.append(headers)
            full_values.append(values)

        table = PrettyTable()

        table.field_names = full_headers[0]
        table.add_rows(full_values)

        table.align = "l"
        table.max_width = 12

        stringify_table = table.get_string()

        return stringify_table

    except Exception as e:
        logging.error(
            f"Community Route Error: Failed to convert JSON to table format. Details: {e}"
        )


@router.message(Command("leaderboard"))
async def command_base_get_leaderboard(message: Message):
    """
    Retrieve the Leaderboard using command '/leaderboard'
    """

    # route will be here to get data from backend

    table = format_json_to_table(json_data=json_data)

    text = "🏆 <b>Top Agents This Week</b>\n<pre>{}</pre>".format(table)

    await message.answer(text, parse_mode="HTML")


async def send_leaderboard_weekly():
    """Send Weekly Leaderboard to Channel"""

    delay = 604800  # 7 days * 24 hours * 60 minutes * 60 seconds = 604800 seconds

    while True:
        # logic to retrieve data from backend

        # format json
        table = format_json_to_table(json_data=json_data)

        text = "🏆 <b>Top Agents This Week</b>\n<pre>{}</pre>".format(table)

        await bot.send_message(chat_id=CHANNEL_ID, text=text)

        await asyncio.sleep(delay=delay)
