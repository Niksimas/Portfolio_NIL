from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter, Command

from core.keyboard import inline as kb
import core.database.database as database
from core.administrate.basic import check_code_admin
from core.statistics.basic import set_statistic

router = Router()


@router.message(CommandStart(), StateFilter(None))
async def start_mess(message: Message, state: FSMContext):
    await state.clear()
    try:
        if check_code_admin(int(message.text.split(" ")[-1])):
            await message.answer("Поздравляю, вы стали администратором!")
            database.save_new_admin(message.from_user.id, message.from_user.username, message.from_user.first_name)
            return
    except:
        pass
    data_mess = database.get_mess("start")
    if data_mess["photo_id"] is None:
        await message.answer(data_mess["text"], reply_markup=kb.start(message.from_user.id))
    else:
        await message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                   reply_markup=kb.start(message.from_user.id))
    database.save_new_user(message.from_user.id, message.from_user.username)


@router.callback_query(F.data == "start")
async def start_call(call: CallbackQuery, state: FSMContext):
    await state.clear()
    data_mess = database.get_mess("start")
    if data_mess["photo_id"] is None:
        await call.message.answer(data_mess["text"], reply_markup=kb.start(call.from_user.id))
    else:
        await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                        reply_markup=kb.start(call.from_user.id))
    await call.message.delete()


@router.callback_query(F.data == "contacts")
async def contacts(call: CallbackQuery, bot: Bot):
    await bot.answer_callback_query(call.id)
    data_mess = database.get_mess("contact")
    site_mess = database.get_mess("site")
    try:
        await call.message.edit_text(data_mess["text"], reply_markup=kb.site(site_mess["text"], site_mess["photo_id"]))
    except TelegramBadRequest:
        if data_mess["photo_id"] in ["", None]:
            await call.message.answer(data_mess["text"], reply_markup=kb.site(site_mess["text"], site_mess["photo_id"]))
        else:
            await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                            reply_markup=kb.site(site_mess["text"], site_mess["photo_id"]))
        await call.message.delete()
    set_statistic("view_contact", call.from_user.id)

