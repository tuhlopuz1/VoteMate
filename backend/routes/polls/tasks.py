from uuid import UUID

from arq import create_pool
from arq.connections import RedisSettings

from backend.core.config import REDIS_ARQ, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT


async def enqueue_notify_author(chat_id: int, poll_id: UUID, delay: float):
    redis = await create_pool(
        RedisSettings(host=REDIS_HOST, port=REDIS_PORT, database=REDIS_ARQ, password=REDIS_PASSWORD)
    )
    await redis.enqueue_job("notify_author", chat_id, poll_id, delay)


async def enqueue_notify_user(user_id: UUID, poll_id: UUID, delay: float):
    redis = await create_pool(
        RedisSettings(host=REDIS_HOST, port=REDIS_PORT, database=REDIS_ARQ, password=REDIS_PASSWORD)
    )
    await redis.enqueue_job("notify_user", user_id, poll_id, delay)
