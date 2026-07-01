import hashlib
import secrets
import time

from backend.shared_cons import connection_pool

from .database import update_user, get_user
from .jwt_handler import create_access_token
from .config import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    ABSOLUTE_SESSION_EXPIRE_DAYS,
)




#Creating Refresh Token, called from login endpoint
def create_refresh_token(emp_id: str):
    emp_id = emp_id.lower()
    user = get_user(emp_id)
    if not user:
        return None

    refresh_token = secrets.token_urlsafe(32)  #generates random token string
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()  #hashes the token using this algo
    
    current_time = time.time()  #gets current time
    
    refresh_token_expiry = current_time + (REFRESH_TOKEN_EXPIRE_DAYS *24 *60 *60)  #creates refresh expiry time
    
    user["refresh_token"] = refresh_token_hash            #hash and its expiry time is stored in db
    user["refresh_token_expiry"] = refresh_token_expiry

    update_user(emp_id, user)  #saves the db

    return refresh_token    #returns the refresh token to main





#Function to refresh the access token, called from refresh end point

def refresh_access_token(refresh_token: str):
    refresh_token_hash = hashlib.sha256(
        refresh_token.encode()
    ).hexdigest()                                       #verifies whether existing refresh token is valid or not

    current_time = time.time()
    conn = connection_pool.getconn()

    try:
        cur = conn.cursor()

        # Lock the matching row until token rotation is complete.
        cur.execute(
            """
            SELECT emp_id, role, lock_until,
                   refresh_token_expiry, session_start
            FROM users
            WHERE refresh_token = %s
            FOR UPDATE
            """,
            (refresh_token_hash,)
        )

        row = cur.fetchone()

        if not row:
            conn.rollback()
            return None

        (
            emp_id,
            role,
            lock_until,
            refresh_token_expiry,
            session_start,
        ) = row

        if lock_until > current_time:
            conn.rollback()
            return None

        if not session_start:
            conn.rollback()
            return None

        absolute_expiry = (
            session_start
            + ABSOLUTE_SESSION_EXPIRE_DAYS * 24 * 60 * 60
        )

        if current_time > absolute_expiry:
            conn.rollback()
            return None

        if refresh_token_expiry < current_time:
            conn.rollback()
            return None

        access_token = create_access_token({
            "sub": emp_id,
            "role": role,
            "session_start": session_start,
        })

        new_refresh_token = secrets.token_urlsafe(32)

        new_refresh_token_hash = hashlib.sha256(
            new_refresh_token.encode()
        ).hexdigest()

        new_expiry = (
            current_time
            + REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        cur.execute(
            """
            UPDATE users
            SET refresh_token = %s,
                refresh_token_expiry = %s
            WHERE emp_id = %s
              AND refresh_token = %s
            """,
            (
                new_refresh_token_hash,
                new_expiry,
                emp_id,
                refresh_token_hash,
            )
        )

        if cur.rowcount != 1:
            conn.rollback()
            return None

        conn.commit()

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        connection_pool.putconn(conn)
    