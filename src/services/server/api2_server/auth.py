import logging
from typing import Optional
import aiohttp

from src.config import BASE_URL_V2
from src.models.api2_models.telegram import LoginModel, RegisterModel, TelegramStatusModel

logger = logging.getLogger(__name__)

async def register_user(user_data: RegisterModel) -> Optional[RegisterModel]:
    register_url = f"{BASE_URL_V2}/telegram/register"
    
    try:
        async with aiohttp.ClientSession() as session:
            data = user_data.model_dump()
            async with session.post(register_url, json=data) as response:
                register_result = await response.json()
                
                if response.status == 200:
                    return RegisterModel.model_validate(register_result['data'])
                else:
                    logger.error(f"Registration failed: {register_result.get('message', 'Unknown error')}")
                    return None
    except Exception as e:
        logger.error(f"Exception during registration: {str(e)}")
        return None
    

async def user_login(user_data: LoginModel) -> dict:
    """Authenticate user with email and password asynchronously using aiohttp.

    Args:
        email (str): User's email.
        password (str): User's password.

    Returns:
        Optional[LoginResponse]: User details if authentication is successful; None otherwise.
    """
    url = f"{BASE_URL_V2}/telegram/login"
    payload = user_data.model_dump()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                response_text = await response.text()
                if response.status == 200:
                    login_result = await response.json()
                    return login_result.get("data", {})
                else:
                    logger.error(f"HTTP error during login: {response.status} - {response_text}")
                    return {}
        except Exception as e:
            logger.error(f"Exception during login: {str(e)}")
            return {}