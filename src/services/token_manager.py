user_tokens = {}  # {telegram_user_id: {"user_id": "", "token": ""}}

def save_user_token(telegram_user_id: int, user_id: str, token: str):

    user_tokens[telegram_user_id] = {
        "user_id": user_id,
        "token": token
    }
    print(f"✅ Token saved for user {telegram_user_id}")

def get_user_token(telegram_user_id: int) -> str:
    
    user_data = user_tokens.get(telegram_user_id, {})
    return user_data.get("token", "")

def get_user_id(telegram_user_id: int) -> str:
  
    user_data = user_tokens.get(telegram_user_id, {})
    return user_data.get("user_id", "")