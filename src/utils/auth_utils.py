import re

from src.responses.auth_response import PASSWORD_MSG

#email validation function
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

#validate format 
def validate_phone_format(phone: str) -> bool:
    """Validation plus stricte avec codes pays"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    # verif pattern
    pattern = r'^\+\d{1,4}\d{6,12}$'
    
    if not re.match(pattern, phone):
        return False
    
    # 10-15 after +
    phone_digits = phone[1:]
    return 10 <= len(phone_digits) <= 15

def format_phone(phone: str) -> str:
    return phone.strip().replace(" ", "").replace("-", "") 

def validate_password(password: str) -> tuple[bool, list[str]]:
    errors = []

    if len(password) < 8:
        errors.append(PASSWORD_MSG["long_characters"])
    
    if not re.search(r"[A-Z]", password):
        errors.append(PASSWORD_MSG["uppercase"])
    
    if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\"\\|,.<>/?`~]", password):
        errors.append(PASSWORD_MSG["special_character"])
    
    if not re.search(r"\d", password):
        errors.append(PASSWORD_MSG["password"])

    is_valid = len(errors) == 0
    return is_valid, errors