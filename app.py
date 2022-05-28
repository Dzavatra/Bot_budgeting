from aiogram import executor
import asyncio
from loader import dp
from notifications import scheduler
import middlewares, handlers
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, timeout=30)
