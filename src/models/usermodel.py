import pydantic

from pydantic import BaseModel, Field

class UserModel(BaseModel):
    """User model for storing user information.

    Attributes:
        user_id (int): Unique identifier for the user.
        username (str): Username of the user.
        first_name (str): First name of the user.      
        last_name (str): Last name of the user.
        language (str): Preferred language of the user.
        country (str): Country of the user. 
        """
    
    pass