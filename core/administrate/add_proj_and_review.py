import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile

from core.settings import home
from core.database import database
from core.keyboard import inline as kbi

subrouter = Router()


class AddProject(StatesGroup):
    TypeProject = State()
    SetName = State()
    SetDescription = State()
    CheckProject = State()


@subrouter.callback_query(F.data == "no", AddProject.CheckProject)
@subrouter.callback_query(F.data == "add_project" or F.data == "add_review")
async def menu_add_project(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text("Выберите тип проекта:", reply_markup=kbi.type_project())
    except TelegramBadRequest:
        await call.message.answer("Выберите тип проекта:", reply_markup=kbi.type_project())
        await call.message.delete()
    await state.set_state(AddProject.TypeProject)


@subrouter.callback_query(F.data.in_(["add_bot", "add_site", "add_design"]), AddProject.TypeProject)
async def set_name_project(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("Напишите название проекта:", reply_markup=kbi.cancel_admin())
    await state.update_data({"type": call.data.split("_")[-1], "del": msg.message_id})
    await state.set_state(AddProject.SetName)


@subrouter.message(AddProject.SetName)
async def set_description_project(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    msg = await mess.answer("Прикрепите фотографию (по желанию) и напишите описание проекта с нужным форматированием",
                            reply_markup=kbi.cancel_admin())
    await state.update_data({"name": mess.html_text, "del": msg.message_id})
    await state.set_state(AddProject.SetDescription)


@subrouter.message(AddProject.SetDescription)
async def check_new_project(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    await state.update_data({"description": mess.html_text})
    data = await state.get_data()
    if mess.photo is not None:
        file_id = mess.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        destination = f'{home}/photo/{file_id}.jpg'
        await bot.download_file(file_info.file_path, destination)
        photo = FSInputFile(destination)
        msg = await mess.answer_photo(photo=photo,
                                      caption=f"Название проекта: {data['name']}\n"
                                              f"Описание: \n{mess.html_text}\n\nСохраняем?",
                                      reply_markup=kbi.confirmation())
        await state.update_data({"text": mess.html_text, "name_photo": msg.photo[-1].file_id})
        if os.path.exists(destination):
            os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
    else:
        await mess.answer(f"Название проекта: {data['name']}\nОписание:\n{mess.html_text}\n\nСохраняем?",
                          reply_markup=kbi.confirmation())
        await state.update_data({"text": mess.html_text, "name_photo": None})
    await state.set_state(AddProject.CheckProject)


@subrouter.callback_query(F.data == "yes", AddProject.CheckProject)
async def save_new_project(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    database.save_new_project(data)
    await state.clear()
    await call.message.answer("Проект сохранен!", reply_markup=kbi.admin_menu(call.from_user.id))
    await call.message.delete()


# ###################################### Добавление отзыва ########################################################## #
class AddReview(StatesGroup):
    SetNameProj = State()
    SetDescription = State()
    SetNameUser = State()
    CheckReview = State()


@subrouter.callback_query(F.data == "add_review_admin")
@subrouter.callback_query(F.data == "no", AddReview.CheckReview)
async def set_name_proj_in_review(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text("Напишите название проекта: ", reply_markup=kbi.cancel_admin())
    except TelegramBadRequest:
        msg = await call.message.answer("Напишите название проекта:", reply_markup=kbi.cancel_admin())
        await call.message.delete()
    await state.update_data({"del": msg.message_id})
    await state.set_state(AddReview.SetNameProj)


@subrouter.message(AddReview.SetNameProj)
async def set_text_review(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    msg = await mess.answer("Напишите текст отзыва: ", reply_markup=kbi.cancel_admin())
    await state.update_data({"name_project": mess.html_text, "del": msg.message_id})
    await state.set_state(AddReview.SetDescription)


@subrouter.message(AddReview.SetDescription)
async def set_username_review(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    msg = await mess.answer("Напишите кто оставил отзыв: ", reply_markup=kbi.cancel_admin())
    await state.update_data({"text": mess.html_text, "del": msg.message_id})
    await state.set_state(AddReview.SetNameUser)


@subrouter.message(AddReview.SetNameUser)
async def check_new_review(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    await state.update_data({"name_user": mess.text})
    data = await state.get_data()
    await mess.answer(f"Название проекта: {data['name_project']}\n"
                      f"Отзыв: \n{data['text']}\n"
                      f"Оставил: {data['name_user']}", reply_markup=kbi.confirmation())
    await state.set_state(AddReview.CheckReview)


@subrouter.message(AddReview.SetNameUser)
async def save_new_review(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id_review = database.save_new_review(data)
    database.verification_review(id_review)
    await call.message.edit_text("Отзыв сохранен!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()
