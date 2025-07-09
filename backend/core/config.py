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
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_CELERY = os.getenv("REDIS_CELERY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")

if DB_URL:
    DATABASE_URL = DB_URL
else:
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"  # noqa

REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_REDIS = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY}"
logger.info(CELERY_REDIS)

logger.info(DATABASE_URL)
