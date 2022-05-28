from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

import db
from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")
    await message.answer(
        "<b>Открыть основное меню</b> - /menu\n"
        "_________________________________________\n"
        "Для справки используйте\nкоманду /help")
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
