import asyncio

from datetime import timedelta
from aiogram.exceptions import *
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import State, StatesGroup

import core.keyboard.inline as kbi
from core.database import database

subrouter = Router()


class NotificationProcess(StatesGroup):
    SetMessage = State()
    SetPhoto = State()
    SetPeople = State()
    CheckMessage = State()
    StartNotification = State()


@subrouter.callback_query(F.data == "no", NotificationProcess.CheckMessage)
@subrouter.callback_query(F.data == "notif")
async def start_notification(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("Отправь мне текст сообщения которое надо разослать!",
                                       reply_markup=kbi.cancel_admin())
    await state.update_data({"del": msg.message_id})
    await state.set_state(NotificationProcess.SetMessage)
    return


@subrouter.message(NotificationProcess.SetMessage)
async def set_message(mess: types.Message, state: FSMContext, bot: Bot):
    try:
        msg_del = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.from_user.id, msg_del, reply_markup=None)
    except:
        pass
    await state.set_data({"text": mess.html_text})
    await mess.answer("Текст сохранён! Будем добавлять фотографию?",
                      reply_markup=kbi.confirmation())
    return


@subrouter.callback_query(F.data == "yes", NotificationProcess.SetMessage)
async def set_photo_yes(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(NotificationProcess.SetPhoto)
    await call.message.edit_text("Отправьте изображение!\n<b>(Необходимо отправить только ОДНУ фотографию)</b>",
                                 reply_markup=kbi.cancel_admin())
    return


@subrouter.message(F.media_group_id, NotificationProcess.SetPhoto)
async def save_photo_front(mess: Message, state: FSMContext):
    data = await state.get_data()
    try:
        b = data["group_id"]
    except KeyError:
        await state.update_data({"group_id": mess.media_group_id})
        await mess.answer("Можно загрузить только одну фотографию!")


@subrouter.message(NotificationProcess.SetPhoto)
async def set_photo(mess: types.Message, state: FSMContext, bot: Bot):
    photo = mess.photo
    if photo is None:
        await mess.answer("Вы не прислали фотографию. Отправьте изображение как фотографию!")
        return
    try:
        msg_del = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.from_user.id, msg_del, reply_markup=None)
    except:
        pass
    await state.update_data({"id_photo": photo[-1].file_id})

    data = await state.get_data()
    try:
        msg1 = await mess.answer_photo(data["id_photo"])
        msg2 = await mess.answer(data["text"])
        await state.update_data({"del1": msg1.message_id, "del2": msg2.message_id})
    except:
        msg1 = await mess.answer(data["text"])
        await state.update_data({"del1": msg1.message_id})
    await mess.answer("Если все верно, то я начинаю рассылку: ",
                              reply_markup=kbi.confirmation())
    await state.set_state(NotificationProcess.CheckMessage)


@subrouter.callback_query(F.data == "yes", NotificationProcess.CheckMessage)
async def start_notif(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.delete_message(call.from_user.id, data["del1"])
        await bot.delete_message(call.from_user.id, data["del2"])
    except:
        pass
    user_id = database.get_all_id_user()
    await call.message.edit_text("Рассылка начата! После окончания я вышлю вам итоги!\n"
                                 "Рассылка может занимать долгое время, так как на каждого "
                                 "пользователя тратится по 2 секунды\n"
                                 f"Ожидаемое время рассылки: {timedelta(seconds=len(user_id)*2)}")
    result = {"notif_t": 0, "notif_f": 0}
    for i in user_id:
        await asyncio.sleep(2)
        try:
            try:
                await bot.send_photo(chat_id=i, photo=data["id_photo"])
                await bot.send_message(chat_id=i, text=data["text"],
                                       disable_web_page_preview=True)
            except KeyError:
                await bot.send_message(chat_id=i, text=data["text"],
                                       disable_web_page_preview=True)
            result["notif_t"] += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            result["notif_f"] += 1
    await call.message.answer(f"Вот итоги рассылки: \n"
                              f"{result['notif_t']} пользователей получили сообщение\n"
                              f"{result['notif_f']} пользователей не получили сообщение.")
    await state.clear()
    return
