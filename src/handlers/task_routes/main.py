# main.py
import asyncio
from bot import bot, dp
from handlers import text_tasks, img_tasks,img_text_pipeline
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

async def main():
    dp.include_router(img_text_pipeline.router)
    dp.include_router(text_tasks.router)
    dp.include_router(img_tasks.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
