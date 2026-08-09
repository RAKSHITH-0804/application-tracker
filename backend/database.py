import os
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager

# Simple .env loader to avoid external dependencies
def load_env():
    # Look for .env in the project directory
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        os.path.join(os.getcwd(), ".env"),
        ".env"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()
            break

# Load environment variables
load_env()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment or .env file.")

# Initialize the connection pool (1 min connection, 10 max connections)
# Using ThreadedConnectionPool since FastAPI runs endpoints in threadpools.
pool = ThreadedConnectionPool(1, 10, dsn=DATABASE_URL)

@contextmanager
def get_db_connection():
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        pool.putconn(conn)
