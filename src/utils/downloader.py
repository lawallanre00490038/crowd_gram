import os
import logging
import tempfile

from aiogram import Bot

logger = logging.getLogger(__name__)


# Save to a temporary file
async def download_telegram(file_id, bot: Bot) -> str:
    # Get file info from Telegram
    file = await bot.get_file(file_id)

    file_type = os.path.splitext(file.file_path)[-1]

    # Create a temporary file to store the downloaded content
    with tempfile.NamedTemporaryFile(suffix=file_type, delete=False) as tmp_file:
        # Download and write into the temp file
        await bot.download_file(file.file_path, tmp_file)
        temp_file_path = tmp_file.name  # Save the path to return or use

    logger.info(f"File: {file.file_path} downloaded to temporary path: {temp_file_path}")
    return temp_file_path  # You can return it if needed later