from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from src.models.api2_models.status import StatusModel
from src.services.server.api2_server.status import get_contributor_status, get_reviewer_status, get_analytics, get_daily_analytics
from src.responses.status_response import format_agent_status, format_reviewer_status


logger = logging.getLogger(__name__)


router = Router()


@router.message(Command("status"))
async def handle_status(message: Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")
    role = data.get("role")
    if not (email and role):
        await message.answer("Please login first using /start.")
        return
    try:
        status_request = StatusModel(email=email)
        if role == "agent":
            response = await get_contributor_status(status_request)
            status_msg = format_agent_status(response.model_dump())
            await message.answer(status_msg, parse_mode="HTML")
        elif role == "reviewer":
            response = await get_reviewer_status(status_request)
            status_msg = format_reviewer_status(response.model_dump())
            await message.answer(status_msg, parse_mode="HTML")
        else:
            await message.answer("Role not recognized. Please contact support.")
    except Exception as e:
        logger.error(f"Error in handle_status: {str(e)}")
        await message.answer("An error occurred while fetching your status. Please try again later.")