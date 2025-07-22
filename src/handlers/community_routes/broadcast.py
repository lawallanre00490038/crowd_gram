import json
import logging

from src.config import CHANNEL_ID, GROQ_ID
from src.loader import bot
from src.handlers.community_routes.community import format_json_to_table
from aiogram import Router
from groq import Groq

client = Groq(api_key=GROQ_ID)
router = Router()


json_data_broadcast_project_insert = """
    {
      "Task": "audio",
      "Cat": "static",
      "Language": "Yoruba",
      "Count": 4
   }
"""
json_data_broadcast_policy_insert = """
    {
      "announcement_title": "Upcoming Security Policy Update",
      "body": "To enhance account protection, we're introducing a mandatory two-factor authentication policy starting August 15. Please ensure your mobile number is up to date in your profile settings."
    }
"""

json_data_broadcast_trainings_insert = """
    {
      "announcement_title": "New User Onboarding Course Available",
      "body":  "We've launched an updated onboarding training for new users. This 45-minute course walks through the core features and best practices for getting started quickly."
    }
"""

# Uses Groq Model to general an emoji based on the announcement title for trainings and policies
def generate_emoji(title: str):
    chat_completion = client.chat.completions.create(
    messages = [
        {

         "role": "system",
         "content": "You are generating emoji's"
         
         },
         {
             "role": "user",
             "content": "Provide one or two emoji's for" +  title,
         }
    ],
    model = "llama-3.3-70b-versatile"
    
    )
    return chat_completion.choices[0].message.content

def format_json_to_text(data: str):
   parsed = json.loads(data)
   final = f"<u><b>Check out this New Announcement</b></u>\n\n"
   if len(parsed) > 1:
       final = f"<u><b>Check out these New Announcements</b></u>\n\n"
   for item in parsed:
      print(item)
      final += f"{generate_emoji(item['announcement_title'])}<b>{item['announcement_title']}</b>\n\n {item['body']}"
   return final
   
async def broadcast():
    """Broadcast New Projects, Trainings, and Policies"""
    # @{name}.post("/projects")
    async def broadcast_new_projects(request: str):
        """Broadcast New Projects"""
        # TODO Logic to recieve and retrieve json from backend request

        try:
            structure = format_json_to_table(request)
            context = f"📢<b>Check out these New Projects</b>  \n<pre>{structure}</pre>"
            await bot.send_message(chat_id=CHANNEL_ID, text=context)
        except Exception as err:
            logging.error(f"Community-Broadcast Projects Router Error: Failed to parse json. Details: {err}")

    # @{name}.post("/trainings")
    async def broadcast_new_trainings(request: str):
        """Broadcast New Trainings"""
        # TODO Logic to recieve and retrieve json from backend request
        
        try:
            context = format_json_to_text(request)
            await bot.send_message(chat_id=CHANNEL_ID, text=context)
        except Exception as err:
            logging.error(f"Community-Broadcast Training Router Error: Failed to parse json. Details: {err}")

    # @{name}.post("/policies")
    async def broadcast_new_policies(request: str):
        """Broadcast New Policies"""   
        # TODO Logic to receive and retrieve json from backend request

        try:
            context = format_json_to_text(request)
            await bot.send_message(chat_id=CHANNEL_ID, text=context)
        except Exception as err:
         logging.error(f"Community-Broadcast Policies Router Error: Failed to parse json. Details: {err}")


    await broadcast_new_projects(f'[{json_data_broadcast_project_insert}]')
    await broadcast_new_trainings(f'[{json_data_broadcast_trainings_insert}]')
    await broadcast_new_policies(f'[{json_data_broadcast_policy_insert}]')