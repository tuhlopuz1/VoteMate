from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from backend.bot.handlers import router
from backend.core.config import BOT_TOKEN

default_props = DefaultBotProperties(parse_mode="HTML")

bot = Bot(token=BOT_TOKEN, default=default_props)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)
