import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile

from core.settings import home
from core.database import database
from core.keyboard import inline as kbi
from core.handlers import basic as hand_base
from core.keyboard.calldata import Project, Reviews
from core.handlers.view_projects import viewing_projects_next_back
from core.handlers.view_reviews import viewing_reviews_next_back

subrouter = Router()


# ############################################### Удаление проекта ################################################## #
@subrouter.callback_query(Project.filter(F.action == "deleted"))
async def check_deleted_project(call: CallbackQuery, callback_data: Project):
    data = database.get_project_data(callback_data.id_proj, callback_data.types)
    try:
        await call.message.edit_caption(caption=f"Название: {data['name_project']}\nОписание: {data['description']}\n\n"
                                                f"Вы уверены в удалении?",
                                        reply_markup=kbi.del_record(yes_data=Project(types=callback_data.types, action="yes_del", id_proj=callback_data.id_proj,
                                                                num_proj=callback_data.num_proj, value=-1),
                                            cancel_data=Project(types=callback_data.types, action="edit",
                                                                num_proj=callback_data.num_proj, value=0)))
    except TelegramBadRequest:
        await call.message.edit_text(f"Название: {data['name_project']}\nОписание: {data['description']}\n\n"
                                     f"Вы уверены в удалении?",
                                        reply_markup=kbi.del_record(
                                            yes_data=Project(types=callback_data.types, action="yes_del", id_proj=callback_data.id_proj,
                                                             num_proj=callback_data.num_proj, value=-1),
                                            cancel_data=Project(types=callback_data.types, action="edit",
                                                                num_proj=callback_data.num_proj, value=0)))


@subrouter.callback_query(Project.filter(F.action == "yes_del"))
async def del_project(call: CallbackQuery, callback_data: Project, state: FSMContext):
    data = database.get_project_data(callback_data.id_proj, callback_data.types)
    if os.path.exists(f"{home}/photo/{data['name_photo']}.jpg"):
        os.remove(f"{home}/photo/{data['name_photo']}.jpg")
    database.deleted_project(callback_data.id_proj)
    if callback_data.num_proj <= 1:
        await call.answer("Последний кейс удален!")
        await hand_base.start_call(call, state)
    else:
        await call.answer("Кейс удален!")
        await viewing_projects_next_back(call, callback_data)


# ############################################### Изменение проекта ################################################## #
class EditProject(StatesGroup):
    CheckOldMess = State()
    SetPhoto = State()
    SetText = State()


@subrouter.callback_query(Project.filter(F.action == "modify"))
async def modify_project_menu(call: CallbackQuery, callback_data: Project, state: FSMContext):
    data = database.get_project_data(callback_data.id_proj, callback_data.types)
    try:
        await call.message.edit_caption(caption=f"Название: {data['name_project']}\nОписание: {data['description']}\n\n"
                                                f"Что вы хотите изменить?",
                                        reply_markup=kbi.edit_project(callback_data))
    except TelegramBadRequest:
        await call.message.edit_text(f"Название: {data['name_project']}\nОписание: {data['description']}\n\n"
                                     f"Что вы хотите изменить?",
                                     reply_markup=kbi.edit_project(callback_data))
    await state.set_state(EditProject.CheckOldMess)
    await state.update_data({"type": callback_data.types, "id_proj": callback_data.id_proj,
                             "num_proj": callback_data.num_proj})


@subrouter.callback_query(F.data == "photo", EditProject.CheckOldMess)
async def modify_photo_project(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    msg = await call.message.answer("Отправьте новую фотографию: ",
                              reply_markup=kbi.cancel_record(Project(types=data["type"], action="edit", id_proj=data["id_proj"],
                                                             num_proj=data["num_proj"], value=0)))
    await state.set_state(EditProject.SetPhoto)
    await state.update_data({"del": msg.message_id})


@subrouter.message(F.media_group_id, EditProject.SetPhoto)
async def warning_media_group(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data = await state.get_data()
    try:
        b = data["group_id"]
        if b != mess.media_group_id:
            await state.update_data({"group_id": mess.media_group_id})
            msg = await mess.answer("Можно прикрепить только одну фотографию",
                              reply_markup=kbi.cancel_record(Project(types=data["type"], action="edit", id_proj=data["id_proj"],
                                                                     num_proj=data["num_proj"], value=0)))
            await state.update_data({"del": msg.message_id})
    except KeyError:
        await state.update_data({"group_id": mess.media_group_id})
        msg = await mess.answer("Можно прикрепить только одну фотографию",
                          reply_markup=kbi.cancel_record(Project(types=data["type"], action="edit", id_proj=data["id_proj"],
                                                                 num_proj=data["num_proj"], value=0)))
        await state.update_data({"del": msg.message_id})


@subrouter.message(F.photo, EditProject.SetPhoto)
async def save_photo_project(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data = await state.get_data()
    data_proj = database.get_project_data(data["id_proj"], data["type"])
    file_id = mess.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    destination = f'{home}/photo/{file_id}.jpg'
    await bot.download_file(file_info.file_path, destination)
    photo = FSInputFile(destination)
    msg = await mess.answer_photo(photo=photo,
                                  caption=f"Название проекта: {data_proj['name_project']}\n"
                                          f"Описание: \n{data_proj['description']}\n\nСохраняем?",
                                  reply_markup=kbi.confirmation_project(data['type'], data['id_proj'], data['num_proj']))
    await state.update_data({"name_photo": msg.photo[-1].file_id, "name_project": data_proj['name_project'], "description": data_proj['description']})


@subrouter.callback_query(Project.filter(F.action == "yes_mod"))
async def save_modification_project(call: CallbackQuery, callback_data: Project, state: FSMContext):
    data = await state.get_data()
    data_old = database.get_project_data(data["id_proj"], data["type"])
    if os.path.exists(f"{home}/photo/{data_old['name_photo']}.jpg"):
        os.remove(f"{home}/photo/{data_old['name_photo']}.jpg")
    database.update_project(data)
    await viewing_projects_next_back(call, callback_data, state)


@subrouter.callback_query(F.data.in_(["name_project", "description"]), EditProject.CheckOldMess)
async def set_new_data_project(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    msg = await call.message.answer("Отправьте новые данные: ",
                              reply_markup=kbi.cancel_record(Project(types=data["type"], action="edit", id_proj=data["id_proj"],
                                                             num_proj=data["num_proj"], value=0)))
    await state.set_state(EditProject.SetText)
    await state.update_data({"del": msg.message_id, "type_mess": call.data})


@subrouter.message(EditProject.SetText)
async def check_new_data_project(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data = await state.get_data()
    data_proj = database.get_project_data(data["id_proj"], data["type"])
    data_proj[data['type_mess']] = mess.text
    if data_proj["name_photo"] in [None, ""]:
        msg = await mess.answer(f"Название проекта: {data_proj['name_project']}\n"
                                f"Описание: \n{data_proj['description']}\n\nСохраняем?",
                                reply_markup=kbi.confirmation_project(data['type'], data['id_proj'], data['num_proj']))
    else:
        msg = await mess.answer_photo(photo=data_proj['name_photo'],
                                      caption=f"Название проекта: {data_proj['name_project']}\n"
                                              f"Описание: \n{data_proj['description']}\n\nСохраняем?",
                                      reply_markup=kbi.confirmation_project(data['type'], data['id_proj'], data['num_proj']))
    await state.update_data({"name_photo": msg.photo[-1].file_id, "name_project": data_proj['name_project'], "description": data_proj['description']})


# ############################################### Удаление отзыва ################################################## #
@subrouter.callback_query(Reviews.filter(F.action == "deleted"))
async def check_del_review(call: CallbackQuery, callback_data: Reviews):
    list_id = database.get_reviews_all_id()
    data = database.get_review_data(list_id[callback_data.review_num-1])
    await call.message.edit_text(f"Название проекта:<b> {data['name_project']}</b>\n"
                                 f"Отзыв: {data['text']}\n"
                                 f"Оставил: {data['name']}\n\n"
                                 f"Вы уверены в удалении?",
                                 reply_markup=kbi.del_record(
                                     yes_data=Reviews(action="yes_del", review_num=callback_data.review_num, value=-1),
                                     cancel_data=Reviews(action="edit", review_num=callback_data.review_num, value=0)))


@subrouter.callback_query(Reviews.filter(F.action == "yes_del"))
async def del_review(call: CallbackQuery, callback_data: Reviews, state: FSMContext):
    list_id = database.get_reviews_all_id()
    database.deleted_review(list_id[callback_data.review_num-1])
    if callback_data.review_num <= 1:
        await call.answer("Последний кейс удален!")
        await hand_base.start_call(call, state)
    else:
        await call.answer("Кейс удален!")
        await viewing_reviews_next_back(call, callback_data)


# ############################################### Изменение отзыва ################################################## #
class EditReview(StatesGroup):
    CheckOldMess = State()
    SetText = State()


@subrouter.callback_query(Reviews.filter(F.action == "modify"))
async def modify_menu_review(call: CallbackQuery, callback_data: Reviews, state: FSMContext):
    list_id = database.get_reviews_all_id()
    data = database.get_review_data(list_id[callback_data.review_num - 1])
    await call.message.edit_text(f"Название проекта:<b> {data['name_project']}</b>\n"
                                 f"Отзыв: {data['text']}\n"
                                 f"Оставил: {data['name']}\n\n"
                                 f"Что вы хотите изменить?",
                                 reply_markup=kbi.edit_review(callback_data))
    await state.set_state(EditProject.CheckOldMess)
    await state.update_data({"review_num": callback_data.review_num, "review_id": list_id[callback_data.review_num - 1]})


@subrouter.callback_query(Reviews.filter(F.action == "yes_mod"))
async def save_modification_review(call: CallbackQuery, callback_data: Reviews, state: FSMContext):
    data = await state.get_data()
    database.update_review(data)
    await viewing_reviews_next_back(call, callback_data, state)


@subrouter.callback_query(F.data.in_(["name_project", "text", "name"]), EditProject.CheckOldMess)
async def set_new_data_review(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = await call.message.edit_text("Отправьте новые данные: ",
                                    reply_markup=kbi.cancel_record(Reviews(action="edit", review_num=data["review_num"],
                                                                           value=0)))
    await state.set_state(EditReview.SetText)
    await state.update_data({"del": msg.message_id, "type_mess": call.data})


@subrouter.message(EditReview.SetText)
async def check_new_data_review(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data = await state.get_data()
    data_proj = database.get_review_data(data["review_num"])
    data_proj[data['type_mess']] = mess.text
    await mess.answer(f"Название проекта:<b> {data_proj['name_project']}</b>\n"
                                 f"Отзыв: {data_proj['text']}\n"
                                 f"Оставил: {data_proj['name']}\n\nСохраняем?",
                            reply_markup=kbi.confirmation_review(data['review_num']))
    await state.update_data(data_proj)
