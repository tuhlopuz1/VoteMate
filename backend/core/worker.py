import asyncio
import os

from aiogram.types import FSInputFile
from arq.connections import RedisSettings

from backend.bot.dispatcher import bot
from backend.core.config import REDIS_ARQ, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.poll_analyzer import PollVisualizer


async def startup(ctx):
    print("Worker started")


async def shutdown(ctx):
    print("Worker stopping")


async def notify_author(ctx, chat_id: int, poll_id: str, delay: float):
    await asyncio.sleep(delay)
    poll = await adapter.get_by_id(Poll, poll_id)
    user = await adapter.get_by_value(User, "telegram_id", chat_id)
    if not user[0].notifications:
        return None
    if poll.is_notified:
        return None
    if poll.votes_count == 0:
        await bot.send_message(
            chat_id=chat_id,
            text=f"Ваш опрос {poll.name} завершился, но к сожалению в нём никто не проголосовал",
        )
        return None
    poll_obj = {
        "id": poll.id,
        "name": poll.name,
        "votes_count": poll.votes_count,
        "user_id": poll.user_id,
        "user_username": poll.user_username,
        "description": poll.description,
        "options": poll.options,
    }
    visualizer = PollVisualizer(poll_obj)
    graph = visualizer.generate_visual_report()
    file = FSInputFile(graph)
    await bot.send_photo(
        chat_id=chat_id, photo=file, caption=f"Ваш опрос {poll.name} завершён! Вот его статистика:"
    )
    os.remove(graph)
    await adapter.update_by_id(Poll, poll_id, {"is_notified": True})
    return None


class WorkerSettings:
    redis_settings = RedisSettings(
        host=REDIS_HOST, port=REDIS_PORT, database=REDIS_ARQ, password=REDIS_PASSWORD
    )
    functions = [notify_author]
    on_startup = startup
    on_shutdown = shutdown
