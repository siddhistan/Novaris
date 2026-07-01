import hashlib

from backend.shared_cons import connection_pool

from .database import update_user



#Implementing the logout feature 
def logout_user(refresh_token: str):
    

    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest() #we hash the incoming token provided by user, cuz refresh token is stored as a hash in db also and we are gonna compare it

    # Connect to database
    conn = connection_pool.getconn()
    try:
        cur = conn.cursor()

        # Find user using refresh token
        cur.execute("SELECT * FROM users WHERE refresh_token = %s", (refresh_token_hash,))   #here, we check if incoming refresh token hash exists in db or not
        row = cur.fetchone()

        cur.close()
    finally:
        connection_pool.putconn(conn)

    if not row:
        return False

    emp_id = row[0]

    user = {
        "name": row[1],
        "password_hash": row[2],
        "role": row[3],
        "failed_attempts": row[4],
        "lock_until": row[5],
        "lock_count": row[6],
        "last_failed_login": row[7],
        "refresh_token": row[8],
        "refresh_token_expiry": row[9],
        "session_start": row[10]
    }

    user["refresh_token"] = ""                       #invalidating refresh token
    user["refresh_token_expiry"] = 0                 #setting its expiry time to 0
    user["session_start"] = 0                        #killing the prev session

    update_user(emp_id, user)                        #saving in db

    return True                                      #true means logout succeeded
