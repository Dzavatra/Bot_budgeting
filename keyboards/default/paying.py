from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

paying = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Наличные'),
            KeyboardButton(text='Безналичный расчет')
        ]
    ],
    resize_keyboard=True
)