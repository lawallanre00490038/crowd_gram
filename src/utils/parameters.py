# parameters.py
from enum import Enum

# This Enum defines the parameter names for user data in the FSM context.
class UserParams(Enum):
    LOGIN_IDENTIFIER = "login_identifier"
    TASK_INFO = "task_info"