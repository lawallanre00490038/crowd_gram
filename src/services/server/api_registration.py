import aiohttp
from src.services.server.auth import user_login
from src.services.token_manager import save_user_token

async def register_user(user_data: dict, telegram_user_id: int):
    
    register_url = "https://apiauth.datacollect.equalyz.ai/api/v1/user/auth/register"
    register_data = {
        "name": user_data.get("auth_name", ""),
        "password": user_data.get("auth_password", "") or user_data.get("password", ""),
        "company_id": "67ffa9f7247f6d8ea50939c9", #change later!!
        "os_type": "Windows"    #default for now change later...
    }
    
    if user_data.get("auth_email"):
        register_data["email"] = user_data["auth_email"]
    if user_data.get("auth_phone"):
        register_data["phone_number"] = user_data["auth_phone"]
    if user_data.get("auth_country_code"):
        register_data["country_code"] = user_data["auth_country_code"]
    

    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(register_url, json=register_data) as response:
                register_result = await response.json()
                
                if response.status == 200 and register_result.get("message") == "Account Created Successfully":
                    user_id = register_result.get("data", {}).get("_id")  # Utiliser _id
                    
                    identifier = user_data.get("auth_email") or user_data.get("auth_phone", "")
                    password = register_data["password"]
                    
                    login_response = user_login(identifier, password)
                    
                    if login_response and login_response.data:
                        token = login_response.data.token if hasattr(login_response.data, 'token') else ""
                        
                        # Sauvegarder le token globalement
                        save_user_token(telegram_user_id, user_id, token)
                        
                        return {"success": True, "user_id": user_id, "token": token}
                    else:
                        return {"success": False, "error": "Registration OK but login failed"}
                else:
                    return {"success": False, "error": register_result.get("message", "Registration failed")}
                    
    except Exception as e:
        return {"success": False, "error": str(e)}