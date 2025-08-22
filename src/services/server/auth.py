import logging
import requests
from src.config import BASE_URL
from src.models.auth_models import LoginResponse

logger = logging.getLogger(__name__)

def user_login(email: str, password: str) -> LoginResponse:
    """Authenticate user with email and password.

    Args:
        email (str): User's email.
        password (str): User's password.
    Returns:    
        UserDetails: If authentication is successful, returns user details.
    """
    # Here you would typically check the email and password against a database.
    # For demonstration purposes, let's assume the following credentials are valid.
    url = f"{BASE_URL}/user/auth/login"

    payload = {
        "email": email,
        "password": password
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        logging.info("User authenticated successfully.")
        return LoginResponse.model_validate(response.json())
    else:
        logging.error(f"Authentication failed: {response.status_code}, {response.text}")
        return None


