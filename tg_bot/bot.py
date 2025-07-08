import asyncio
import random
from string import ascii_letters

import aiogram
from aiogram.filters.command import Command

bot = aiogram.Bot()
router = aiogram.Router()


async def generate_auth_token():
    random.shuffle(ascii_letters)
    return ascii_letters[:6]


print(asyncio.run(generate_auth_token))


@router.message(Command("/start"))
async def give_token(message: aiogram.types.Message):
    pass
