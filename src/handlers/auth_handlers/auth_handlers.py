from src.handlers.onboarding_handlers.onboarding import get_company_id
from src.models.auth_models import LoginResponseDict, UserRegisterRequest, VerifyPasswordInput
from src.services.server.auth import register_user, verify_otp


async def user_signup(user_data) -> LoginResponseDict:
    company = user_data.get('company')
    company_id = await get_company_id(company) 

    print(company_id)

    if not company_id:
        raise ValueError("Company not found")
    
    auth_phone = user_data.get("auth_phone", "")
    user_info = UserRegisterRequest(country_code=auth_phone[:3], 
                        phone_number=auth_phone[3:],
                        email=user_data.get("email", None),
                        os_type="telegram",
                        company_id=company_id,
                        password=user_data.get("password"),name= user_data.get("auth_name"))
    
    user_response = await register_user(user_info)
    
    return user_response

async def user_verify_otp(user_data, inputed_otp) -> LoginResponseDict:
    auth_phone = user_data.get("auth_phone", "")

    user_info = VerifyPasswordInput(password=user_data.get("password"),
                               otp = inputed_otp, 
                               phone_number=auth_phone[3:],
                        email=user_data.get("email", None))
    
    user_response = await verify_otp(user_info)
    
    return user_response