from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from Bot.google_doc.googleSheets import get_record
from Bot.keyboard import general as kb
from .general import start
router = Router()


# №_record	id_foto	name_project	text	username
@router.callback_query(F.data == "see_review")
async def viewing_reviews(call: CallbackQuery, bot: Bot):
    await bot.answer_callback_query(call.id)
    data = get_record(1, "review")
    await call.message.answer_photo(data[1])
    await call.message.answer(f"<b>Название проекта:</b> {data[2]}\n"
                              f"{data[3]}\n"
                              f"Оставил: {data[4]}\n\n",
                              reply_markup=kb.menu_reviews(1))
    await call.message.delete()


@router.callback_query(F.data.split("_")[0] == "rback")
async def viewing_reviews(call: CallbackQuery, bot: Bot):
    try:
        await bot.answer_callback_query(call.id)
        num = int(call.data.split("_")[-1])-1
        data = get_record(num, "review")
        try:
            await call.message.answer_photo(data[1])
        except TelegramBadRequest:
            pass
        await call.message.answer(f"<b>Название проекта:</b> {data[2]}\n"
                                  f"{data[3]}\n"
                                  f"Оставил: {data[4]}\n\n",
                                  reply_markup=kb.menu_reviews(num))
        try:
            await bot.delete_message(call.message.chat.id, call.message.message_id - 1)
        except TelegramBadRequest:
            pass
        await call.message.delete()
    except (IndexError, TelegramBadRequest):
        try:
            await bot.delete_message(call.message.chat.id, call.message.message_id - 1)
        except TelegramBadRequest:
            pass
        await call.message.delete()
        await start(call.message)


@router.callback_query(F.data.split("_")[0] == "rnext")
async def viewing_projects(call: CallbackQuery, bot: Bot):
    try:
        num = int(call.data.split("_")[-1])+1
        data = get_record(num, "review")
        try:
            await call.message.answer_photo(data[1])
        except TelegramBadRequest:
            pass
        await call.message.answer(f"<b>Название проекта:</b> {data[2]}\n"
                                  f"{data[3]}\n"
                                  f"Оставил: {data[4]}\n\n",
                                  reply_markup=kb.menu_reviews(num))
        await bot.answer_callback_query(call.id)
        try:
            await bot.delete_message(call.message.chat.id, call.message.message_id - 1)
        except TelegramBadRequest:
            pass
        await call.message.delete()
    except (IndexError, TelegramBadRequest):
        await call.answer("Отзывов больше нет :(")
