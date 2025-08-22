import aiohttp
import asyncio

async def get_countries_from_api():
    url = "https://apiauth.datacollect.equalyz.ai/api/v1/user/auth/country"
    
    try:
        print("🌍 Fetching countries from API...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extraire juste les noms des pays
                    countries = []
                    if data.get("data"):
                        for country in data["data"]:
                            country_name = country.get("name")
                            if country_name:
                                countries.append(country_name)
                    
                    print(f"✅ Got {len(countries)} countries from API")
                    return countries
                    
                else:
                    print(f"❌ API returned status {response.status}")
                    return get_fallback_countries()
                    
    except Exception as e:
        print(f"❌ Error fetching countries: {e}")
        return get_fallback_countries()
    


async def get_states_from_api(country_name: str):
    
    # fetch isoCode --> country code   
    countries_url = "https://apiauth.datacollect.equalyz.ai/api/v1/user/auth/country"
    country_code = None
    
    try:
        print(f"🏛️ Fetching states for {country_name}...")
        
        # Étape 1: Trouver le code du pays
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
                    print(f"❌ Country code not found for: {country_name}")
                    return get_fallback_states(country_name)
                
                states_url = f"https://apiauth.datacollect.equalyz.ai/api/v1/user/auth/state?countryCode={country_code}"
                
                async with session.get(states_url) as states_response:
                    if states_response.status == 200:
                        states_data = await states_response.json()
                        
                        if states_data.get("data"):
                            states = []
                            for state in states_data["data"]:
                                state_name = state.get("name")
                                if state_name:
                                    states.append(state_name)
                            
                            print(f"✅ Got {len(states)} states for {country_name}")
                            return states if states else ["Other"]
                        else:
                            print(f"📋 No states found for {country_name}")
                            return ["Other"]
                    else:
                        print(f"❌ States API returned status {states_response.status}")
                        return get_fallback_states(country_name)
                        
    except Exception as e:
        print(f"❌ Error fetching states: {e}")
        return get_fallback_states(country_name)
    

async def get_languages_from_api():

    company_id = "67ffa9f7247f6d8ea50939c9"  # default on EqualyzCrowd -- change later 
    url = f"https://apiauth.datacollect.equalyz.ai/api/v1/user/auth/language?company_id={company_id}"
    
    try:
        print("🗣️ Fetching languages from API...")
        
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
                        
                        print(f"✅ Got {len(languages)} languages from API")
                        return languages
                    else:
                        print("📋 No languages data in API response")
                        return get_fallback_languages()
                        
                else:
                    print(f"❌ Languages API returned status {response.status}")
                    return get_fallback_languages()
                    
    except Exception as e:
        print(f"❌ Error fetching languages: {e}")
        return get_fallback_languages()



async def get_dialects_from_api(language_name: str):
    try:
        print(f"🗣️ Fetching dialects for {language_name}...")
        
        # Step 1: Get language ID from name (same logic as get_states_from_api)
        languages = await get_languages_from_api()
        language_id = None
        
        for lang in languages:
            if lang["name"].lower() == language_name.lower():
                language_id = lang["id"]
                break
        
        if not language_id:
            print(f"❌ No ID found for language: {language_name}")
            return ["Not listed here"]
        
        # Step 2: Call dialect API with the ID
        url = "https://apiauth.datacollect.equalyz.ai/api/v1/user/auth/dialect_list"
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
                                
                                print(f"✅ Got {len(dialects)} dialects for {language_name}")
                                return dialects
                        
                        # If we get here, language not found in response
                        print(f"❌ Language {language_name} not found in API response")
                        return ["Not listed here"]
                    else:
                        print("📋 No dialects data in API response")
                        return ["Not listed here"]
                else:
                    error_text = await response.text()
                    print(f"❌ Error {response.status}: {error_text}")
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

