from loguru import logger
from typing import Optional
import requests
import aiohttp

from src.config import BASE_URL
from src.models.auth_models import BaseUserData, LoginResponse, LoginResponseDict, SignupResponseDict, UserData, UserRegisterRequest, VerifyPasswordInput
from src.models.onboarding_models import CompleteProfileRequest, CompleteProfileResponseDict
from src.services.token_manager import save_user_token


async def register_user(user_data: UserRegisterRequest) -> SignupResponseDict:
    register_url = f"{BASE_URL}/user/auth/register"

    try:
        async with aiohttp.ClientSession() as session:
            if user_data.phone_number == "":
                data = user_data.model_dump(
                    exclude={"country_code", "phone_number"})
            elif user_data.email == None:
                data = user_data.model_dump(exclude={"email"})

            data["checkbox"] = ["checked"]

            async with session.post(register_url, json=data) as response:
                register_result = await response.json()

                if response.status == 200 and register_result.get("message") == "Account Created Successfully":

                    base_info = BaseUserData.model_validate(
                        register_result['data'])

                    return {"success": True, "error": "", "base_info": base_info}
                else:
                    return {"success": False, "error": register_result.get("message", "Registration failed"), "base_info": {}}

    except Exception as e:
        return {"success": False, "error": str(e), "base_info": {}}


async def user_login(email: str, password: str) -> LoginResponseDict:
    """Authenticate user with email and password asynchronously using aiohttp.

    Args:
        email (str): User's email.
        password (str): User's password.

    Returns:
        Optional[LoginResponse]: User details if authentication is successful; None otherwise.
    """
    url = f"{BASE_URL}/user/auth/login"
    payload = {
        "email": email,
        "password": password
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                response_text = await response.text()

                # Attempt to parse JSON response
                try:
                    response_data = await response.json()
                except aiohttp.ContentTypeError as e:
                    logging.error(f"Invalid JSON response: {response_text}")
                    return {"success": False, "error": e, "base_info": {}}

                # print(response_data)
                if response.status == 200:
                    logging.info("User authenticated successfully.")
                    return {"success": True, "error": "", "base_info": UserData.model_validate(response_data['data'])}
                else:
                    logging.error(
                        f"Authentication failed: {response.status}, {response_text}")
                    return {"success": False, "error": f"Authentication failed: {response.status}, {response_text}", "base_info": {}}
        except aiohttp.ClientError as exc:
            logging.error(f"HTTP request error: {str(exc)}")
            return None


async def verify_otp(user_info: VerifyPasswordInput) -> Optional[LoginResponse]:
    """Verify OTP

    Args:
        email (str): User's email.
        password (str): User's password.

    Returns:
        Optional[LoginResponse]: User details if authentication is successful; None otherwise.
    """
    url = f"{BASE_URL}/user/auth/verify_otp"

    if user_info.phone_number == "":
        data = user_info.model_dump(exclude={"country_code", "phone_number"})
    elif user_info.email == None:
        data = user_info.model_dump(exclude={"email"})

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data) as response:
                response_text = await response.text()

                # Attempt to parse JSON response
                try:
                    response_data = await response.json()
                except aiohttp.ContentTypeError as e:
                    logging.error(f"Invalid JSON response: {response_text}")
                    return {"success": False, "error": e, "base_info": {}}

                if response.status == 200:
                    logging.info("User authenticated successfully.")
                    return {"success": True, "error": "", "base_info": UserData.model_validate(response_data['data'])}
                else:
                    logging.error(
                        f"Authentication failed: {response.status}, {response_text}")
                    return {"success": False, "error": f"Authentication failed: {response.status}, {response_text}", "base_info": {}}

        except aiohttp.ClientError as exc:
            logging.error(f"HTTP request error: {str(exc)}")
            return {"success": False, "error": exc, "base_info": {}}


async def complete_user_profile(
    profile_data: CompleteProfileRequest,
    authorization_token: str
) -> CompleteProfileResponseDict:
    complete_profile_url = f"{BASE_URL}/user/auth/complete_profile"

    headers = {
        "Authorization": f"Bearer {authorization_token}",
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            data = profile_data.model_dump()
            print(data)
            print(authorization_token)

            async with session.post(complete_profile_url, json=data, headers=headers) as response:
                result = await response.json()

                if response.status == 200 and result.get("message") == "Profile Completed Successfully":
                    base_info = BaseUserData.model_validate(result["data"])
                    return {"success": True, "error": "", "base_info": base_info}
                else:
                    return {"success": False, "error": result.get("message", "Profile completion failed"), "base_info": {}}

    except Exception as e:
        return {"success": False, "error": str(e), "base_info": {}}
