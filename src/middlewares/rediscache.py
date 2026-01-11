import json
import redis
from functools import wraps
from typing import get_type_hints

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def pydantic_fallback():
    def decorator(func):
        # Get the return type hint (e.g., UserProfile)
        type_hints = get_type_hints(func)
        return_type = type_hints.get('return')

        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"fallback:{func.__name__}:{args}:{kwargs}"
            
            try:
                # 1. Try Live Server
                result = func(*args, **kwargs)
                
                # 2. Success: Store as JSON string
                # .model_dump_json() is the standard Pydantic v2 method
                r.set(cache_key, result.model_dump_json())
                return result

            except Exception as e:
                print(f"Live server failed: {e}. Checking Redis...")
                
                # 3. Fallback: Get from Redis
                cached_data = r.get(cache_key)
                if cached_data and return_type:
                    # 4. Reconstruct the Pydantic model
                    data_dict = json.loads(str(cached_data))
                    return return_type.model_validate(data_dict)
                
                raise e # No cache available, re-raise original error
        return wrapper
    return decorator