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
SUPABASE_API = os.getenv("SUPABASE_API")
SUPABASE_URL = os.getenv("SUPABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = os.getenv("REDIS_DB")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if DB_URL:
    DATABASE_URL = DB_URL
else:
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"  # noqa

REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

logging.info(DATABASE_URL)
