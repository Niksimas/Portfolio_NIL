import asyncio
import logging
from decouple import config
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import *
from function import admins

logging.basicConfig(level=logging.INFO)

token = config("token", default="000")
bot = Bot(token, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(general.router)
dp.include_router(creat_tz.router)


@dp.message(Command(commands=["stops159"]))
async def stop(message: types.Message):
    await message.answer("Все сценарии работы выключены!")
    await bot.close()
    exit(1)


async def on_startup():
    await bot.delete_webhook()
    await bot.send_message(admins[0], "Бот запущен")
    await bot.delete_webhook(drop_pending_updates=True)
    return


async def on_shutdown():
    await bot.send_message(admins[0], "Бот выключен")
    await dp.storage.close()
    return


dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
