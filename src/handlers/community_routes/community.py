import asyncio
import json
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from prettytable import PrettyTable
from time import sleep
from src.config import CHANNEL_ID, BOT_TOKEN
from src.loader import bot
from aiogram.utils.formatting import Bold, Text


router = Router()
json_data_broadcast_project = "[]"
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

json_data_broadcast_project_insert1 = """
    {
      "Task": "audio",
      "Cat": "static",
      "Language": "Yoruba",
      "Count": 4
   }
"""
json_data_broadcast_project_insert2 = """
  {
      "Task": "text",
      "Cat": "translation",
      "Lang": "Hausa",
      "Count": 20
  }  
"""
json_data_broadcast_policy_insert1 = """
    {
      "policy 1": "We have decided to increase time of voice recordings",
      "policy 2": "We have added a annotation fee"
    }
"""

json_data_broadcast_policy_insert2 = """
    {
      "policy 3": "There are no more tasks for images",
      "policy 4": "We have added a translation fee"     
    }
"""

json_data_broadcast_trainings_insert1 = """
    {
      "Message": "We are training on text annotation",
      "Date":  "11/12/25",
      "Time": "8:00AM",
      "Venue": "Zoom" 
    }
"""

json_data_broadcast_trainings_insert2 = """
    {
      "Message": "We are training on telegram onboarding",
      "Date":  "12/12/26",
      "Time": "9:00AM",
      "Venue": "Zoom"  
    }
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
inserts = []

def json_to_list(data: str):
    str_lst = ""
    try:
        new_list = json.loads(data)
        for item in new_list:
           if isinstance(item, dict):
              for k, v in item.items():
                str_lst+= f"{k}: {v}\n"
        return str_lst
    except Exception as err:
        print(f"Issue with formatting list {err}")

def insert_item(inserts):
    try:
      if len(inserts) == 0:
        return None   
      return json.loads(inserts.pop())
    except Exception as err:
        print(f"an error occured {err}")

async def send_broadcast(brod_type: str):
    """Broadcast New Projects, New Training, and New Policies"""
    title = ""
    # Logic to retrieve from the backend

    insert_type = {
        "new_projects":  [json_data_broadcast_project_insert1, json_data_broadcast_project_insert2], 
        "new_trainings": [json_data_broadcast_trainings_insert1, json_data_broadcast_trainings_insert2] ,
        "new_policys": [json_data_broadcast_policy_insert1, json_data_broadcast_policy_insert2]
    }
    broadcast_type = {
        "new_projects": format_json_to_table,
        "new_trainings": json_to_list,
        "new_policys": json_to_list
    }
    title_name = {
        "new_projects": "Projects",
        "new_trainings": "Trainings",
        "new_policys": "Policies"       
    }    
    type = broadcast_type.get(brod_type)
    insert_type = insert_type.get(brod_type)
    if insert_type:
        inserts = insert_type
    struct = brod_type
    if title_name:
        title = title_name.get(brod_type)
    try: 
      prev_state = "[]"
      while True:
          try:
            if prev_state != "[]":
                if type:    
                  struct = type(prev_state)
                  context = f"📢<b>Here are the New {title}</b>  \n<pre>{struct}</pre>"
                  await bot.send_message(chat_id=CHANNEL_ID, text=context)
                  prev_state = "[]"
            await asyncio.sleep(10)
            updated_projects = json.loads("[]")
            updated_projects.append(insert_item(inserts))
            
            if None in updated_projects:
                continue
            prev_state = json.dumps(updated_projects).strip()

          except Exception as err:
              print(f"Something went wrong for the function {err}")
              return
    except Exception as err:
        print(f"Something went wrong for the function {err}")
        return 
    