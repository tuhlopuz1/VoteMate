import logging
import os

from dotenv import load_dotenv

load_dotenv("config/.env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Environment loaded")

DB_URL = os.getenv("DB_URL")
RANDOM_SECRET = os.getenv("RANDOM_SECRET")
FASTAPI_HOST = os.getenv("FASTAPI_HOST")
FASTAPI_PORT = os.getenv("FASTAPI_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DBNAME = os.getenv("POSTGRES_DBNAME")
DEFAULT_AVATAR_URL = os.getenv("DEFAULT_AVATAR_URL")

if DB_URL:
    DATABASE_URL = DB_URL
else:
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"  # noqa

logging.info(DATABASE_URL)
