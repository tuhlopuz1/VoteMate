import asyncio
import os

from backend.bot.dispatcher import bot
from backend.core.celery_worker import celery_app
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll
from backend.models.poll_analyzer import PollVisualizer


def send_msg_sync(chat_id: int, path: str, text: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    loop.run_until_complete(bot.send_photo(chat_id=chat_id, photo=open(path, "rb"), caption=text))
    os.remove(path)
    loop.close()


async def get_poll_by_id(poll_id: int):
    poll = await adapter.get_by_id(Poll, poll_id)
    return poll


@celery_app.task
def notify_author_task(chat_id: int, poll_id: int):

    poll = asyncio.run(get_poll_by_id(poll_id))

    poll_obj = {
        "id": poll.id,
        "name": poll.name,
        "votes_count": poll.votes_count,
        "user_id": poll.user_id,
        "user_username": poll.user_username,
        "description": poll.description,
        "options": poll.options,
    }

    visualiser = PollVisualizer(poll_obj)
    path = visualiser.generate_visual_report()
    send_msg_sync(chat_id, path, f"Ваш опрос {poll.name} - завершён! вот его статистика:")
