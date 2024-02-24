import os
import asyncio
import logging
from decouple import config
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from core.administrate import router_admin
from core.handlers import main_router
from core.settings import settings

home = os.path.dirname(__file__)

if not os.path.exists(f"{home}/logging"):
    os.makedirs(f"{home}/logging")
if not os.path.exists(f"{home}/core/statistics/data"):
    os.makedirs(f"{home}/core/statistics/data")


logging.basicConfig(level=logging.INFO)

token = config("token")
bot = Bot(token, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(main_router, router_admin)


@dp.message(Command(commands=["stops159"]))
async def stop(message: types.Message):
    await message.answer("Все сценарии работы выключены!")
    await bot.close()
    exit(1)


async def on_startup():
    await bot.delete_webhook()
    await bot.send_message(settings.bots.admin_id, "Бот <b>запущен</b>")
    await bot.delete_webhook(drop_pending_updates=True)
    return


async def on_shutdown():
    await bot.send_message(settings.bots.admin_id, "Бот выключен")
    await dp.storage.close()
    return


dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
