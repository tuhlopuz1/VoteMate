import asyncio
import secrets
import string
from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from backend.bot.keyboards import main_keyboard
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll
from backend.models.poll_analyzer import PollVisualizer
from backend.models.redis_adapter import redis_adapter

router = Router()


# Состояния для FSM
class PollStates(StatesGroup):
    WAITING_FOR_POLL_NAME = State()


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

    await message.answer(
        "Если хотите, то можете нажать на одну из выбранных кнопок, "
        "чтобы следить за результатами созданных вами голосований или "
        "получить статистику по какому-либо голосованию.",
        reply_markup=main_keyboard,
    )


@router.callback_query(F.data == "watch_polls")
async def watch_polls_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Пока ничего не закончилось еще, мы уведомим вас, когда закончится какое-либо голосование!"
    )
    # Запускаем фоновую задачу проверки голосований
    asyncio.create_task(check_polls_periodically(callback.message))


async def check_polls_periodically(message: types.Message):
    """Периодическая проверка окончания голосований"""
    while True:
        try:
            all_polls = await adapter.get_all(Poll)
            for poll in all_polls:
                if poll.end_date and poll.end_date < datetime.now():
                    await message.answer(
                        f'✅ Голосование "{poll.title}" закончилось!\n'
                        f"Всего голосов: {poll.votes_count}\n\n"
                        "Чтобы получать уведомления о других голосованиях, нажмите /watch_polls"
                    )
                    # Помечаем голосование как обработанное, чтобы не уведомлять повторно
                    poll.end_date = None
                    await adapter.update(poll)

            # Проверяем каждые 5 минут
            await asyncio.sleep(300)
        except Exception as e:
            print(f"Ошибка при проверке голосований: {e}")
            await asyncio.sleep(60)  # Ждем перед повторной попыткой


@router.message(Command("watch_polls"))
async def watch_polls_command(message: types.Message):
    await message.answer("Вы будете получать уведомления о завершении голосований!")
    asyncio.create_task(check_polls_periodically(message))


@router.callback_query(F.data == "statistics")
async def statistics_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите название голосования, чтобы узнать статистику по нему.")
    # Устанавливаем состояние ожидания названия голосования
    await state.set_state(PollStates.WAITING_FOR_POLL_NAME)


@router.message(PollStates.WAITING_FOR_POLL_NAME)
async def handle_poll_name(message: types.Message, state: FSMContext):
    poll_name = message.text.strip()
    poll = await adapter.get_by_value(Poll, "name", poll_name)
    if poll:
        # Преобразуем poll в dict, если это ORM-объект
        poll_dict = {
            "id": str(poll.id),
            "name": poll.title,
            "votes_count": poll.votes_count,
            "user_id": poll.user_id,
            "user_username": poll.user_username,
            "description": poll.description,
            "options": poll.options,  # убедитесь, что это dict вида {"Вариант": число}
        }
        visualizer = PollVisualizer(poll_dict)
        chart_path = visualizer.generate_visual_report()
        with open(chart_path, "rb") as photo:
            await message.answer_photo(photo, caption=f'Статистика для голосования "{poll_name}"')
    else:
        await message.answer("Голосование с таким названием не найдено.")
    await state.clear()
