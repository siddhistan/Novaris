import os
from psycopg2 import pool

# Get the connection string from environment variables (provided by Render)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # On Render, we use the DATABASE_URL
    connection_pool = pool.SimpleConnectionPool(
        5,   # min connections
        20,  # max connections
        dsn=DATABASE_URL
    )
else:
    # Fallback for local development
    connection_pool = pool.SimpleConnectionPool(
        5,   # min connections
        20,  # max connections
        host="localhost",
        database="rbac_db",
        user="app_user",
        password="1234"
    )

