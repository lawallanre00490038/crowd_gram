from aiogram import Bot
from aiogram.types import BotCommand

async def set_main_menu(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Start interacting with the bot"),
        BotCommand(command="start_task", description="🚀 Start task flow"),
        BotCommand(command="status", description="📊 Check your task status"),
        BotCommand(command="projects", description="📁 View available projects"),
        BotCommand(command="exit", description="❌ Exit or end current session"),
    ]
    await bot.set_my_commands(commands)
