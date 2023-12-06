from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from Bot.google_doc.googleSheets import get_record
from Bot.keyboard import general as kb
from .general import start

router = Router()


@router.callback_query(F.data == "projects")
async def viewing_projects(call: CallbackQuery, bot: Bot):
    await bot.answer_callback_query(call.id)
    data = get_record(1, "project")
    await call.message.answer_photo(data[1], caption=f"{data[2]}\n\n{data[3]}", reply_markup=kb.menu_projects(1))
    await call.message.delete()


@router.callback_query(F.data.split("_")[0] == "pback")
async def viewing_reviews(call: CallbackQuery, bot: Bot):
    try:
        num = int(call.data.split("_")[-1])-1
        data = get_record(num, "project")
        await call.message.answer_photo(data[1], caption=f"{data[2]}\n\n{data[3]}", reply_markup=kb.menu_projects(num))
        await bot.answer_callback_query(call.id)
        await call.message.delete()
    except (IndexError, TelegramBadRequest):
        await call.message.delete()
        await start(call.message)


@router.callback_query(F.data.split("_")[0] == "pnext")
async def viewing_projects(call: CallbackQuery, bot: Bot):
    try:
        num = int(call.data.split("_")[-1])+1
        data = get_record(num, "project")
        await call.message.answer_photo(data[1], caption=f"{data[2]}\n\n{data[3]}", reply_markup=kb.menu_projects(num))
        await bot.answer_callback_query(call.id)
        await call.message.delete()
    except (IndexError, TelegramBadRequest):
        await call.answer("Проектов больше нет :(")


@router.callback_query(F.data.split("_")[0] == "plike")
async def like(call: CallbackQuery, bot: Bot):
    await bot.answer_callback_query(call.id)
    num = int(call.data.split("_")[-1])
    data = get_record(num, "project")
    await bot.send_message("-1002074447703", f"Пользователь: @{call.from_user.username}\n"
                                      f"Заинтересовался проектом\n"
                                      f"{data[2]}")
    await call.answer("Запрос отправлен менеджеру!")
