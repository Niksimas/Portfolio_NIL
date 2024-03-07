import os
import asyncio
import logging
import datetime as dt

from decouple import config
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from core.handlers import main_router
from core.reminder.general import scheduler
from core.administrate import router_admin
from core.settings import settings, get_chat_id

home = os.path.dirname(__file__)

if not os.path.exists(f"{home}/logging"):
    os.makedirs(f"{home}/logging")
if not os.path.exists(f"{home}/core/statistics/data"):
    os.makedirs(f"{home}/core/statistics/data")


# Для отладки локально разкоментить
logging.basicConfig(level=logging.INFO)
#
# #Для отладки локально закоментить
# logger = logging.getLogger()
# logger.setLevel(logging.WARNING)
# handler = logging.FileHandler(f"{home}/logging/{dt.date.today()}.log", "a+", encoding="utf-8")
# handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
# logger.addHandler(handler)
#
# logging.debug("Сообщения уровня DEBUG, необходимы при отладке ")
# logging.info("Сообщения уровня INFO, полезная информация при работе программы")
# logging.warning("Сообщения уровня WARNING, не критичны, но проблема может повторится")
# logging.error("Сообщения уровня ERROR, программа не смогла выполнить какую-либо функцию")
# logging.critical("Сообщения уровня CRITICAL, серьезная ошибка нарушающая дальнейшую работу")

token = config("token")
bot = Bot(token, parse_mode="HTML", disable_web_page_preview=True)
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(main_router, router_admin)


@dp.message(Command(commands=["stops159"]))
async def stop(message: types.Message):
    await message.answer("Все сценарии работы выключены!")
    await bot.close()
    exit(1)


async def on_startup():
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(1235360344, "Бот запущен")
    return


# get_chat_id()
async def on_shutdown():
    await bot.send_message(1235360344, "Бот выключен")
    await dp.storage.close()
    return


dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
