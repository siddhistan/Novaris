from fastapi import Request

from .jwt_handler import verify_token
from .database import get_user


# Returns the currently authenticated user using the access token cookie
def get_current_user(request: Request):
    
    print(request.cookies)

    # Read the access token sent automatically by the browser
    access_token = request.cookies.get("access_token")

    # Cookie missing
    if not access_token:
        return None

    # Verify JWT
    payload = verify_token(access_token)

    # Invalid or expired JWT
    if not payload:
        return None

    # Extract employee ID from JWT payload
    emp_id = payload["sub"]

    # Fetch latest user information from the database
    user = get_user(emp_id)

    # User no longer exists
    if not user:
        return None

    return user