from typing import Dict
from loguru import logger
from aiogram.fsm.context import FSMContext

from src.handlers.onboarding_handlers.onboarding import get_selected_languages
from src.models.onboarding_models import Category, CompleteProfileRequest, CompleteProfileResponseDict, Language, LanguageResponseModel, Languages, TaskAnswerItem
from src.services.server.auth import complete_user_profile


async def complete_profile(user_data: Dict) -> CompleteProfileResponseDict:
    # Convert answers into TaskAnswerItem list
    logger.trace(user_data)
    task_answer = [
        TaskAnswerItem(
            category_id=answer.get("category_id"),
            category_name=next(
                (cat["name"] for cat in user_data["categories"] if any(
                    q["question"] == answer["question"] for q in cat.get("categoryQuestions", []))),
                ""
            ),
            ques_id=answer.get("ques_id") or answer.get(
                "question_id"),  # handle different keys
            question=answer.get("question"),
            answer=answer.get("answer") if isinstance(
                answer.get("answer"), list) else [answer.get("answer")]
        )
        for answer in user_data["answers"]
    ]

    # Validate categories and extract category names
    data_kind = [i["id"] for i in user_data["categories"]]

    # Get languages and dialects
    selected_languages = await get_selected_languages(user_data=user_data)
    languages = [
        Languages(lang_id=lang.id,
                  dialects=user_data['dialects'].get(lang.name, ""))
        for lang in selected_languages
    ]

    # Construct the complete request object
    complete_profile_data = CompleteProfileRequest(
        referal_code="",
        task_answer=task_answer,
        data_kind=data_kind,
        languages=languages,
        city=user_data.get("region_residence", ""),
        industry=user_data.get("industryid", ""),
        education_level=user_data.get("educationid", ""),
        age_range=user_data.get("ageid", ""),
        gender=user_data.get("genderid", ""),
        city_id=user_data.get("region_id", ""),  # Not provided
        state_origin_id=user_data.get("region_id", ""),  # Not provided
        country_id=user_data.get("location_id", ""),  # Not provided
        state_origin=user_data.get("state_id", ""),
        country=user_data.get("location", ""),
        user_id=user_data["user_data"].get("id", "")  # or use _id if needed
    )

# {
#   "referal_code": "",
#   "task_answer": [
#     {
#       "category_id": "677e14edfc1050ca8c65359d",
#       "category_name": "Audio",
#       "ques_id": "68c2bfef63c9a17d5c38b77e",
#       "question": "Single Question",
#       "answer": [
#         "A"
#       ]
#     },
#     {
#       "category_id": "677e14cafc1050ca8c653599",
#       "category_name": "Text",
#       "ques_id": "68c2c03fecd66ae105ee3021",
#       "question": "Multiple Question",
#       "answer": [
#         "a;ljganha"
#       ]
#     }
#   ],
#   "data_kind": [
#     "677e14edfc1050ca8c65359d",
#     "677e14cafc1050ca8c653599"
#   ],
    # "languages": [
    #     {
    #     "lang_id": "689738fb5d54dbbfa3da99c7",
    #     "dialects": "American",
    #     "proficiency": {
    #         "speaking": "Basic",
    #         "writing": "Basic"
    #     },
    #     "task_types": []
    #     },
    #     {
    #     "lang_id": "689738e55d54dbbfa3da99a8",
    #     "dialects": "Abia",
    #     "proficiency": {
    #         "speaking": "Basic",
    #         "writing": "Basic"
    #     },
    #     "task_types": []
    #     }
    # ],
#   "city": "Ajeromi-Ifelodun",
#   "industry": "689738835d54dbbfa3da993f",
#   "education_level": "689738555d54dbbfa3da9906",
#   "age_range": "6897379d5d54dbbfa3da9856",
#   "gender": "689738075d54dbbfa3da98be",
#   "state_origin": "Lagos",
#   "country": "Nigeria",
#   "city_id": "Ajeromi-Ifelodun",
#   "country_id": "NG",
#   "state_origin_id": "LA",
#   "company_id": "689736b55d54dbbfa3da977e",
#   "user_id": "689739f3c2afef2e724c5de3"
# }

    return await complete_user_profile(profile_data=complete_profile_data,
                                       authorization_token=user_data["user_data"]['token'])
