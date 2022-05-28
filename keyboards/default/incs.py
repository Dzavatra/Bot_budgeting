from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

incs = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Зарплата'),
            KeyboardButton(text='Аванс')
        ],
        [
            KeyboardButton(text='Приход'),
            KeyboardButton(text='Возврат')
        ],
        [
            KeyboardButton(text='Займ'),
            KeyboardButton(text='Дивиденды')
        ],
        [
            KeyboardButton(text='Подарок'),
            KeyboardButton(text='Другое')
        ]
    ],
    resize_keyboard=True
)