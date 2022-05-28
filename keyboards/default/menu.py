from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить расход'),
            KeyboardButton(text='Недавние расходы')
        ],
        [
            KeyboardButton(text='Сегодняшняя статистика'),
            KeyboardButton(text='Отчёт за неделю'),
            KeyboardButton(text='Отчёт за месяц')
        ],
        [
            KeyboardButton(text='Категории расходов')
        ],
        [
            KeyboardButton(text='Добавить доход'),
            KeyboardButton(text='Последние доходы')
        ]
    ],
    resize_keyboard=True
)
