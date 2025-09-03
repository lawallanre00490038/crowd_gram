from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.keyboards.inline import retry_keyboard, g0_to_tutorials_kb, user_type_kb, ready_kb, tutorial_choice_kb, yes_no_inline_keyboard,tutorial_nav_kb


from src.responses.onboarding_response import (WELCOME_MESSAGE, TUTORIAL_MSG, USER_TYPE_MSG, 
                                              PERSONAL_MSG, LANGUAGE_MSG,TASK_TYPE_MSG, ABILITY_MSG, REFERRAL_MSG, 
                                              COMPLETION_MSG)

from src.data.video_tutorials import tutorial_videos
from src.services.server.getters_api import get_companies_from_api


async def show_user_type_selection(message: Message):
    # await message.answer(USER_TYPE_MSG["selection"])
    await message.answer(USER_TYPE_MSG["option"], reply_markup=user_type_kb
    )


async def send_tutorial(message: Message, state: FSMContext, index: int = 0):
    data = await state.get_data()
    index = data.get("tutorial_index", 0)
    await state.update_data(tutorial_index=index)
    await message.answer(tutorial_videos[index], reply_markup=tutorial_nav_kb(index))

async def get_company_id(company_name: str) -> str:
    data = await get_companies_from_api()

    for i in data:
        if company_name == i.name:
            return i.id 
    
    return None
