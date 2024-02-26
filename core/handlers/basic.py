from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter

from core.keyboard import inline as kb
import core.database.database as database
from core.administrate.basic import check_code_admin


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
    await message.answer(database.get_mess("start"), reply_markup=kb.start(message.from_user.id))
    database.save_new_user(message.from_user.id, message.from_user.username)


@router.callback_query(F.data == "start")
async def start_call(call: CallbackQuery):
    try:
        await call.message.edit_text(database.get_mess("start"), reply_markup=kb.start(call.from_user.id))
    except TelegramBadRequest:
        await call.message.answer(database.get_mess("start"), reply_markup=kb.start(call.from_user.id))
        await call.message.delete()


@router.callback_query(F.data == "contacts")
async def contacts(call: CallbackQuery, bot: Bot):
    await bot.answer_callback_query(call.id)
    await call.message.edit_text(database.get_mess("contact"), reply_markup=kb.site(database.get_mess("site")))
