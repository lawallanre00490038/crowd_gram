from typing import List
import aiohttp
from src.config import BASE_URL
import logging

from src.models.company_models import CompanyInfo

logger = logging.getLogger(__name__)

async def get_companies_from_api() -> List[CompanyInfo]:
    url = f"{BASE_URL}/user/auth/company_list"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return [CompanyInfo(**item) for item in data['data']['result']] 
                else:
                    logging.error(f"Something is wrong {response.json()}")
                    return get_fallback_countries()
                    
    except Exception as e:
        logging.error(f"Exception occured {e}")
        return get_fallback_countries()

async def get_countries_from_api():
    url = f"{BASE_URL}/user/auth/country"
    
    try:
       
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                
                if response.status == 200:
                    data = await response.json()
                  
                    countries = []
                    if data.get("data"):
                        for country in data["data"]:
                            country_name = country.get("name")
                            if country_name:
                                countries.append(country_name)
                
                    return countries
                    
                else:
        
                    return get_fallback_countries()
                    
    except Exception as e:
        return get_fallback_countries()
    
async def get_states_from_api(country_name: str):
    
    # fetch isoCode --> country code   
    countries_url = f"{BASE_URL}/user/auth/country"
    country_code = None
    
    try:
        
        async with aiohttp.ClientSession() as session:
            async with session.get(countries_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("data"):
                        for country in data["data"]:
                            if country.get("name", "").lower() == country_name.lower():
                                country_code = country.get("isoCode")
                                break
                
                if not country_code:
                    return get_fallback_states(country_name)
                
                states_url = f"{BASE_URL}/user/auth/state?countryCode={country_code}"
                
                async with session.get(states_url) as states_response:
                    if states_response.status == 200:
                        states_data = await states_response.json()
                        
                        if states_data.get("data"):
                            states = []
                            for state in states_data["data"]:
                                state_name = state.get("name")
                                if state_name:
                                    states.append(state_name)
                    
                            return states if states else ["Other"]
                        else:
                        
                            return ["Other"]
                    else:
                    
                        return get_fallback_states(country_name)
                        
    except Exception as e:
    
        return get_fallback_states(country_name)
    
async def get_languages_from_api():

    company_id = "67ffa9f7247f6d8ea50939c9"  # default on EqualyzCrowd -- change later 
    url = f"{BASE_URL}/user/auth/language?company_id={company_id}"
    
    try:
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("data"):
                        languages = []
                        for lang in data["data"]:
                            lang_name = lang.get("name")
                            lang_id = lang.get("_id") or lang.get("id")
                            if lang_name:
                                languages.append({
                                    "name": lang_name,
                                    "id": lang_id
                                })
                        
                        return languages
                    else:
                        return get_fallback_languages()
                        
                else:
                    return get_fallback_languages()
                    
    except Exception as e:
        print(f"❌ Error fetching languages: {e}")
        return get_fallback_languages()

async def get_dialects_from_api(language_name: str):
    try:
        print(f" Fetching dialects for {language_name}...")

        languages = await get_languages_from_api()
        language_id = None
        
        for lang in languages:
            if lang["name"].lower() == language_name.lower():
                language_id = lang["id"]
                break
        
        if not language_id:
            return ["Not listed here"]  
        
        url = f"{BASE_URL}/user/auth/dialect_list"
        payload = {"language_ids": [language_id]}  # Pass as list
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                print(f"📊 API Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("data"):
                        # Find dialects for our specific language
                        for lang in data["data"]:
                            if lang.get("name") == language_name:
                                dialects = lang.get("dialects", [])
                                if not dialects:
                                    dialects = ["Not listed here"]
                                else:
                                    if "Not listed here" not in dialects:
                                        dialects.append("Not listed here")
                               
                                return dialects
                        
                    
                        return ["Not listed here"]
                    else:
                        return ["Not listed here"]
                else:
                    error_text = await response.text()
                    return ["Not listed here"]
                    
    except Exception as e:
        print(f"❌ Error fetching dialects for {language_name}: {e}")
        return ["Not listed here"]

#Helper
async def get_language_names():
    languages_data = await get_languages_from_api()
    return [lang["name"] for lang in languages_data]

def get_fallback_languages():

    print("📋 Using fallback languages list")
    return [
        {"name": "English", "id": "english"},
        {"name": "French", "id": "french"},
        {"name": "Fulani", "id": "fulani"},
        {"name": "Hausa", "id": "hausa"},
        {"name": "Hindi", "id": "hindi"},
        {"name": "Igbo", "id": "igbo"},
        {"name": "Pidgin", "id": "pidgin"},
        {"name": "Punjabi", "id": "punjabi"},
        {"name": "Shona", "id": "shona"},
        {"name": "Swahili", "id": "swahili"},
        {"name": "Yoruba", "id": "yoruba"}
    ]


def get_fallback_states(country_name: str):
  
    print(f"📋 Using fallback states for {country_name}")
    
    fallback_states = {
        "Nigeria": ["Lagos", "Abuja", "Kano", "Rivers", "Ogun", "Other"],
        "Ghana": ["Greater Accra", "Ashanti", "Northern", "Western", "Other"],
        "Kenya": ["Nairobi", "Mombasa", "Nakuru", "Kisumu", "Other"]
    }
    
    return fallback_states.get(country_name, ["Other"])

     

def get_fallback_countries():
   
    print("📋 Using fallback countries list")
    return [
        "Nigeria", "Ghana", "Kenya", "South Africa", "Uganda", 
        "Tanzania", "Rwanda", "Cameroon", "Egypt", "Morocco"
    ]

