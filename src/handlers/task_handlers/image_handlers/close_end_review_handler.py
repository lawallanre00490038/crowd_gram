import logging
from aiogram.types import Message

logger = logging.getLogger(__name__)

async def handle_submission():
    """
    Handles the review or submission step for close-ended image tasks.
    """
    # This is a placeholder for any review logic you want to add
    # For now, just log and return a message
    logger.info("Reviewed close-ended image task submission.")
    return "✅ Submission received and reviewed."
