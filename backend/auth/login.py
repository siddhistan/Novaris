import time

from .database import get_user, update_user
from .password import verify_password
from .config import (
    MAX_FAILED_ATTEMPTS,
    LOCKOUT_BASE_MINUTES,
    LOCKOUT_RESET_HOURS,
)

from .config import pwd_context





# Authenticate user during login
#called from login endpoint
def authenticate_user(emp_id, password):
    emp_id = emp_id.lower()   # moved before get_user
    #loads users
    user = get_user(emp_id)

    if not user:
        return None

    current_time = time.time()  #this gets current time

    # Auto reset after 24 hours
    if user["last_failed_login"] != 0:
        if current_time - user["last_failed_login"] > (LOCKOUT_RESET_HOURS * 3600):
            user["failed_attempts"] = 0
            user["lock_count"] = 0

    # Check if account is locked
    if user["lock_until"] > current_time:
        return "LOCKED"

    #Before checking paswsord we check if user has atleast setup his password once or it is empty in db,
    # if empty then login should fail immediately, we do this to avoid crash
    if not user["password_hash"]:
        return None

    # Check password
    if verify_password(password, user["password_hash"]): 
        # If true is returned, then Correct password → reset everything
        user["failed_attempts"] = 0
        user["lock_count"] = 0
        user["lock_until"] = 0
        user["last_failed_login"] = 0

        update_user(emp_id, user)   # replaced save_users
        return user           #returns user object to main, basically it returns the specific user's data as dictionary

    else:
        # Wrong password
        user["failed_attempts"] += 1
        user["last_failed_login"] = current_time

        # If 4 attempts → warning
        if user["failed_attempts"] == MAX_FAILED_ATTEMPTS-1:
            update_user(emp_id, user)   # replaced save_users
            return "LAST_ATTEMPT"

        # Lock account after 5 failed attempts
        if user["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
            user["lock_count"] += 1
            lock_minutes = LOCKOUT_BASE_MINUTES * (2 ** (user["lock_count"] - 1))
            user["lock_until"] = current_time + (lock_minutes * 60)
            user["failed_attempts"] = 0

            update_user(emp_id, user)   # replaced save_users
            return "LOCKED"

        update_user(emp_id, user)   # replaced save_users
        return None             #go back to main, login fails