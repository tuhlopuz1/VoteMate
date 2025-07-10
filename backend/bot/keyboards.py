from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Уведомления о завершении моих голосований", callback_data="subscribe"
            ),
        ],
        [
            InlineKeyboardButton(text="Статистика моих голосований", callback_data="statistics"),
        ],
    ]
)
