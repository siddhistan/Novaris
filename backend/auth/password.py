import time

from .database import get_user, update_user
from .config import pwd_context


# Verify password
'''
# Verify user password using Argon2 hashing
# Called in this file only inside authenticate_user() during login
# Compares plain password with stored hash
'''

#parameters are plain_password that user typed and the already stored hash in db 
#the plain password is then hased to check it with the hashed paswsord in db
def verify_password(plain_password, hashed_password):            
    return pwd_context.verify(plain_password, hashed_password) 
    '''this line pwd line does this internally:

         Takes the plain password
         Uses same algorithm (Argon2)
         Re-hashes it
         Compares with stored hash
         It returns true if password is correct else false'''
         
         
         


#emp_id and new password entered by user are sent as parameters here
def set_user_password(emp_id: str, new_password: str):  
    emp_id = emp_id.lower()    #lowercase emp_id
    user = get_user(emp_id)    #load user from database

    # User must exist, if he doesn't exist in db, we return user not found
    if not user:
        return "USER_NOT_FOUND"

    # Password should NOT already exist, if it does, then we say password already set
    if user.get("password_hash"):
        return "ALREADY_SET"

    # Hash new password
    hashed_password = pwd_context.hash(new_password)

    # Store new hashed password in db
    user["password_hash"] = hashed_password

    update_user(emp_id, user)   #save to database

    return "SUCCESS"      #password is set successfully







#user enters his emp_id, old password, and new password which he wants to replace with the old pasword
def change_user_password(emp_id: str, old_password: str, new_password: str):
    emp_id = emp_id.lower()   #lower the emp_id
    user = get_user(emp_id)   #load user from database

    # User must exist, if he doesn't, then we return user not found
    if not user:
        return "USER_NOT_FOUND"

    # Account lock check, if locked, then user is not allowed to change his password
    if user["lock_until"] > time.time():
        return "LOCKED"

    # Password must already be set, if password is not set even one time, then there is nothing to change
    if not user.get("password_hash"):
        return "PASSWORD_NOT_SET"

    # Verify old password, we call the verify function, it executes in this file only
    #it hashes the provided the password and compares it with existing hash, if they match, it returns true, else false
    #if old password doesn't match, we return wrong password
    if not verify_password(old_password, user["password_hash"]):
        return "WRONG_PASSWORD"

    # Hash new password, if verify password returns true
    new_hash = pwd_context.hash(new_password)

    # Update new password in db
    user["password_hash"] = new_hash

    #We invalidate the complete session after password change, basically reset session time and tokens
    user["session_start"] = 0
    user["refresh_token"] = ""
    user["refresh_token_expiry"] = 0

    update_user(emp_id, user)   #save to database

    return "SUCCESS"    #password is successfully changed