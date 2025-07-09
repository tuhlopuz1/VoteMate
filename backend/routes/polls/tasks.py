import asyncio

from backend.bot.dispatcher import bot
from backend.core.celery_worker import celery_app


def send_msg_sync(chat_id: int, text: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    loop.run_until_complete(bot.send_message(chat_id=chat_id, text=text))
    loop.close()


@celery_app.task
def notify_author_task(chat_id: int, poll_id: int):
    text = f"Опрос #{poll_id} завершён!"
    send_msg_sync(chat_id, text)
