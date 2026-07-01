from backend.shared_cons import connection_pool

## This function fetches user data from PostgreSQL and returns it as a dictionary
'''# THis function is the bridge between the api and the db
# Called from multiple endpoints (/login, /ask) and auth functions
# Returns data as a dictionary (username → user details)'''

def get_user(emp_id):
    
    conn = connection_pool.getconn()    #reusing an existing db connection
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE emp_id = %s", (emp_id,))  #executes sql queries and can be used to fetch their results in tuple format
        row = cur.fetchone()   #fetch one row, since emp_id is unique, we fetch one row(all his details are in that row)
        cur.close()  #close cursor, returns connection to pool
    finally:
        connection_pool.putconn(conn)

    if not row:      #if user not found
        return None
    
    #returns data again in json format
    return {
        "emp_id": row[0],  
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



# Update specific user fields in PostgreSQL database
# Called after modifying user data (login, failed attempts, tokens, etc.)
def update_user(emp_id, user):
    

    # Connect to PostgreSQL database
    conn = connection_pool.getconn()

    try:
        # Create cursor to execute SQL queries
        cur = conn.cursor()

        # Update user data in DB using SQL UPDATE query
        # We only update fields that can change during runtime
        cur.execute("""
            UPDATE users SET
                failed_attempts = %s,
                lock_until = %s,
                lock_count = %s,
                last_failed_login = %s,
                refresh_token = %s,
                refresh_token_expiry = %s,
                session_start = %s,
                password_hash = %s
            WHERE emp_id = %s
        """, (
            user["failed_attempts"],          # number of failed login attempts
            user["lock_until"],               # account lock expiry timestamp
            user["lock_count"],               # number of times account was locked
            user["last_failed_login"],        # last failed login time
            user.get("refresh_token"),        # hashed refresh token
            user.get("refresh_token_expiry"), # refresh token expiry time
            user.get("session_start"),        # session start time
            user["password_hash"],            # password hash (for set/change password)
            emp_id                            # identify which user to update
        ))

        # Save changes permanently in database
        conn.commit()

        # Close cursor and connection to free resources
        cur.close()

    finally:
        connection_pool.putconn(conn)  #returns connection to pool and prevents leaks
