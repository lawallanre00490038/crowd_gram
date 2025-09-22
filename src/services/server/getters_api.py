from typing import List
import aiohttp
from src.config import BASE_URL
import logging

from src.models.onboarding_models import Category, CompanyInfo, CountryModel, LanguageResponseModel, SignUpResponseModel, StateModel

logger = logging.getLogger(__name__)

async def get_signup_list(company_id) -> SignUpResponseModel:
    url = f"{BASE_URL}/user/auth/signup_list"
    params = {"company_id":company_id, "field":"All"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return SignUpResponseModel.model_validate(data) 
                else:
                    logging.error(f"Something is wrong {response.json()}")
                    return get_fallback_countries()
                    
    except Exception as e:
        logging.error(f"Exception occured {e}")

async def get_category_list(company_id: str) -> List[Category]:
    url = f"{BASE_URL}/user/auth/category_list"
    cat_list = list()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"company_id": company_id}) as response:
                
                if response.status == 200:
                    data = await response.json()
                    for i in data['data']:
                        cat_list.append(Category.model_validate(i))
                else:
                    logging.error(f"Something is wrong {response.json()}")
    except Exception as e:
        logging.error(f"Exception occured {e}")
    return cat_list


async def get_companies_from_api() -> List[CompanyInfo]:
    url = f"{BASE_URL}/user/auth/company_list"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if response.status == 200:
                    return [CompanyInfo(**item) for item in data['data']['result']] 
                else:
                    print(response)
                    logging.error(f"Something is wrong {data}")
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
                        return [CountryModel.model_validate(i) for i in data.get("data")]
                
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
                            states = [StateModel.model_validate(i) for i in states_data.get("data")]
                            return states
                        else:
                            return []
                    else:
                    
                        return get_fallback_states(country_name)
                        
    except Exception as e:
    
        return get_fallback_states(country_name) 
    

async def get_region_from_api(country_code: str, state_code: str):
    async with aiohttp.ClientSession() as session:

        states_url = f"{BASE_URL}/user/auth/city?countryCode={country_code}&stateCode={state_code}"
        
        async with session.get(states_url) as states_response:
            if states_response.status == 200:
                states_data = await states_response.json()
                
                if states_data.get("data"):
                    return [i['name'] for i in states_data["data"]]
                else:
                
                    return ["Other"]
                
async def get_languages_from_api(company_id):

    url = f"{BASE_URL}/user/auth/language?company_id={company_id}"
    empty = {}
    try:
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return LanguageResponseModel(message=data['message'],
                                          data = data['data'])
                    # return LanguageResponseModel.model_validate(data)
                        
                else:
                    return get_fallback_languages()
                    
    except Exception as e:
        print(f"❌ Error fetching languages: {e}")
        return get_fallback_languages()

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

