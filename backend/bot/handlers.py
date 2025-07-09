import secrets
import string

from aiogram import Router, types
from aiogram.filters import Command

from backend.models.redis_adapter import redis_adapter

router = Router()


def generate_secure_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


@router.message(Command("start"))
async def handle_start(message: types.Message):
    existing_code = await redis_adapter.get(f"telegram-id:{message.chat.id}")
    if existing_code:
        await message.answer(f"Ваш код: {existing_code}")
    else:
        code = generate_secure_code()
        await redis_adapter.set(f"telegram-id:{message.chat.id}", code, expire=600)
        await redis_adapter.set(f"telegram-code:{code}", message.chat.id, expire=600)
        await message.answer(f"Ваш код: {code}")
