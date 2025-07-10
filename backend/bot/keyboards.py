from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Следить за голосованиями", callback_data="subscribe"),
        ],
        [
            InlineKeyboardButton(text="Статистика моих голосований", callback_data="statistics"),
        ],
    ]
)
