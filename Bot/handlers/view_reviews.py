from aiogram import Router, F, Bot
from aiogram.types import FSInputFile, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from Project.google_doc.googleSheets import get_record
from Project.function import home
from Project.keyboard import general as kb
from .general import start
router = Router()


@router.callback_query(F.data.split("_")[0] == "rback")
async def viewing_reviews(call: CallbackQuery, bot: Bot):
    try:
        num = int(call.data.split("_")[-1])-1
        data = get_record(num, "review")
        await call.message.answer_photo(data[1], reply_markup=kb.menu_reviews(num))
        await bot.answer_callback_query(call.id)
        await call.message.delete()
    except (IndexError, TelegramBadRequest):
        await call.message.delete()
        await start(call.message)


@router.callback_query(F.data.split("_")[0] == "rnext")
async def viewing_projects(call: CallbackQuery, bot: Bot):
    try:
        num = int(call.data.split("_")[-1])+1
        data = get_record(num, "review")
        await call.message.answer_photo(data[1], reply_markup=kb.menu_reviews(num))
        await bot.answer_callback_query(call.id)
        await call.message.delete()
    except (IndexError, TelegramBadRequest):
        await call.answer("Отзывов больше нет :(")
