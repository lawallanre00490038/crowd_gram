import logging
from typing import Optional
import aiohttp

from src.config import BASE_URL_V2
from src.models.api2_models.telegram import LoginModel, RegisterModel, TelegramStatusModel, LoginResponseDict, RegisterResponseDict, LoginResponseModel

logger = logging.getLogger(__name__)

async def register_user(user_data: RegisterModel) -> RegisterResponseDict:
    register_url = f"{BASE_URL_V2}/telegram/register"
    
    try:
        async with aiohttp.ClientSession() as session:
            data = user_data.model_dump()
            async with session.post(register_url, json=data) as response:
                register_result = await response.json()
                
                if response.status == 200:
                    base_info = RegisterModel.model_validate(register_result)
                    return {'success': True, 'error': '', 'base_info': base_info}
                else:
                    logger.error(f"Registration failed: {register_result.get('message', 'Unknown error')}")
                    return {'success': False, 'error': register_result.get('message', 'Unknown error'), 'base_info': None}
    except Exception as e:
        logger.error(f"Exception during registration: {str(e)}")
        return {'success': False, 'error': str(e), 'base_info': None}


async def user_login(user_data: LoginModel) -> LoginResponseDict:
    """Authenticate user with email and password asynchronously using aiohttp.

    Args:
        email (str): User's email.
        password (str): User's password.

    Returns:
        Optional[LoginResponse]: User details if authentication is successful; None otherwise.
    """
    url = f"{BASE_URL_V2}/telegram/login"
    # payload = user_data.model_dump()
    params = {"email": user_data.email, "password": user_data.password}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                login_result = await response.json()
                if response.status == 200:
                    base_info = LoginResponseModel.model_validate(login_result)
                    return {'success': True, 'error': '', 'base_info': base_info}
                else:
                    logger.error(f"HTTP error during login: {response.status} - {login_result}")
                    return {'success': False, 'error': login_result.get('message', 'Unknown error'), 'base_info': None}
        except Exception as e:
            logger.error(f"Exception during login: {str(e)}")
            return {'success': False, 'error': str(e), 'base_info': None}
        

async def get_user_details(user_email: str) -> Optional[LoginResponseModel]:
    """Get the details of a user by their email.

    Args:
        user_email (str): The email of the user.

    Returns:
        Optional[LoginResponseModel]: The user details if found, None otherwise.
    """
    url = f"{BASE_URL_V2}/telegram/me"
    params = {"email": user_email}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                response_result = await response.json()
                if response.status == 200:
                    return LoginResponseModel.model_validate(response_result)
                else:
                    logger.error(f"HTTP error during user details retrieval: {response.status} - {response_result}")
                    return None
        except Exception as e:
            logger.error(f"Exception during user details retrieval: {str(e)}")
            return None