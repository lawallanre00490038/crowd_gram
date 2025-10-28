from typing import Dict, List, Optional
from loguru import logger
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.keyboards.inline import retry_keyboard, g0_to_tutorials_kb, user_type_kb, ready_kb, tutorial_choice_kb, yes_no_inline_keyboard, tutorial_nav_kb


from src.keyboards.onboarding_keyboard import list_category_kb
from src.models.auth_models import UserData
from src.models.onboarding_models import BaseLanguage, Category, CompleteProfileRequest, Language, LanguageResponseModel, SignUpResponseModel, TaskAnswerItem
from src.responses.onboarding_response import (WELCOME_MESSAGE, TUTORIAL_MSG, USER_TYPE_MSG,
                                               PERSONAL_MSG, LANGUAGE_MSG, TASK_TYPE_MSG, ABILITY_MSG, REFERRAL_MSG,
                                               COMPLETION_MSG)

from src.data.video_tutorials import tutorial_videos
from src.services.server.getters_api import get_category_list, get_companies_from_api, get_languages_from_api
from src.states.onboarding import Onboarding


async def get_saved_categories(state: FSMContext = None, user_data=None) -> List[Category]:
    if user_data == None:
        user_data = await state.get_data()

    # categories = user_data.get("categories", None)
    categories = await get_category_list(company_id="689736b55d54dbbfa3da977e")
    return [Category.model_validate(i) for i in categories]


async def get_saved_location(state: FSMContext, user_data=None) -> UserData:
    if user_data == None:
        user_data = await state.get_data()

    return user_data.get("location", None)


async def get_saved_state(state: FSMContext, user_data=None) -> UserData:
    if user_data == None:
        user_data = await state.get_data()

    return user_data.get("state_residence", None)


async def get_full_user_data(state: Optional[FSMContext] = None, user_data: Optional[Dict] = None) -> UserData:
    if user_data == None:
        user_data = await state.get_data()

    fulluserdata = user_data.get("user_data", None)
    if fulluserdata:
        return UserData.model_validate(fulluserdata)
    else:
        return None


async def get_languages(state: FSMContext) -> LanguageResponseModel:
    user_data = await state.get_data()
    fulluserdata = UserData.model_validate(user_data.get("user_data"))
    languages = await get_languages_from_api(fulluserdata.company_id)
    logger.trace(f"Length of Languages: {len(languages.data)}")
    await state.update_data(languages=languages.model_dump())

    return languages


async def get_saved_languages(state: Optional[FSMContext] = None, user_data: Optional[Dict] = None) -> LanguageResponseModel:
    if user_data == None:
        user_data = await state.get_data()

    return LanguageResponseModel.model_validate(user_data.get("languages"))


async def get_selected_languages(state: Optional[FSMContext] = None, user_data: Optional[Dict] = None) -> List[Language]:
    if user_data == None:
        user_data = await state.get_data()

    selected_languages = user_data.get("selected_languages", [])
    ret_selected_languages = []
    for i in selected_languages:
        ret_selected_languages.append(Language.model_validate(i))
    return ret_selected_languages


async def update_selected_languages(state: FSMContext, selected_languages: List[Language]):
    ret_selected_languages = []
    for i in selected_languages:
        ret_selected_languages.append(i.model_dump())

    await state.update_data(selected_languages=ret_selected_languages)


async def show_user_type_selection(message: Message):
    # await message.answer(USER_TYPE_MSG["selection"])
    await message.answer(USER_TYPE_MSG["option"], reply_markup=user_type_kb)


async def send_tutorial(message: Message, state: FSMContext, index: int = 0):
    data = await state.get_data()
    
    await state.update_data(tutorial_index=index)
    await message.answer(tutorial_videos[index], reply_markup=tutorial_nav_kb(index))


async def get_company_id(company_name: str) -> str:
    data = await get_companies_from_api()

    for i in data:
        if company_name == i.name.strip():
            return i.id

    return None


async def init_age_section(message: Message, state: FSMContext):
    await init_onboarding_section(message=message,
                                  state=state,
                                  category="age_range",
                                  section=Onboarding.age_range,
                                  answer="age")


async def init_onboarding_section(message: Message, state: FSMContext, category="age_range", section=Onboarding.age_range, answer="age"):
    user_state = await state.get_data()

    signuplist = SignUpResponseModel.model_validate(
        user_state.get("signuplist"), from_attributes=True)
    await message.answer(PERSONAL_MSG[answer], reply_markup=list_category_kb(signuplist, category))
    await state.set_state(section)
