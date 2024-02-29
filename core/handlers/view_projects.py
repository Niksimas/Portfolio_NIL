from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto

from core.keyboard import inline as kb
from core.settings import settings, home, get_chat_id
from core.keyboard.calldata import Project
from core.database import database as database
from core.statistics.basic import set_statistic

router = Router()


@router.callback_query(F.data.in_(["design", "site", "bot"]))
async def viewing_projects(call: CallbackQuery):
    data = database.get_project_data(1, call.data)
    try:
        message = f"Название: {data['name_project']}\nОписание: {data['description']}"
        if data["name_photo"] == "none":
            await call.message.edit_text(message, reply_markup=kb.menu_projects(1, call.data))
        else:
            await call.message.delete()
            photo = FSInputFile(f"{home}/photo/{data['name_photo']}.jpg")
            await call.message.answer_photo(photo, caption=message,
                                            reply_markup=kb.menu_projects(1, call.data, back_btn=False))
            set_statistic(f"view_project_{call.data}")
    except KeyError:
        await call.answer("Кейсов на данный момент нет!")


@router.callback_query(Project.filter(F.action == "edit"))
async def callbacks_num_change_fab(call: CallbackQuery, callback_data: Project):
    list_id = database.get_project_all_id(callback_data.types)
    num_record = callback_data.id_proj + callback_data.value
    if num_record < 1:
        await call.answer("Вы достигли начала списка!")
    else:
        try:
            project_id = list_id[num_record-1]
            if num_record == len(list_id):
                next_btn = False
            else:
                next_btn = True
            if num_record == 1:
                back_btn = False
            else:
                back_btn = True
            data = database.get_project_data(project_id, callback_data.types)
            message = f"Название: {data['name_project']}\nОписание: {data['description']}"
            if data["name_photo"] == "none":
                try:
                    await call.message.edit_text(message, reply_markup=kb.menu_projects(num_record, callback_data.types,
                                                                                        back_btn, next_btn))
                except TelegramBadRequest:
                    await call.message.answer(message, reply_markup=kb.menu_projects(num_record, callback_data.types,
                                                                                     back_btn, next_btn))
                    await call.message.delete()
            else:
                photo = FSInputFile(f"{home}/photo/{data['name_photo']}.jpg")
                try:
                    await call.message.edit_media(InputMediaPhoto(media=photo, caption=message),
                                                  reply_markup=kb.menu_projects(num_record, callback_data.types,
                                                                                back_btn, next_btn))
                except TelegramBadRequest:
                    await call.message.answer_photo(photo, caption=message,
                                                    reply_markup=kb.menu_projects(num_record, callback_data.types,
                                                                                  back_btn, next_btn))
                    await call.message.delete()
            set_statistic(f"view_project_{callback_data.types}")
        except IndexError:
            await call.answer("Кейсов больше нет!")


@router.callback_query(Project.filter(F.action == "like"))
async def like(call: CallbackQuery, bot: Bot, callback_data: Project):
    data = database.get_project_data(callback_data.id_proj, callback_data.types)
    await bot.send_message(get_chat_id(),
                           f"Пользователь:\n"
                           f"Имя: [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n"
                           f"Ссылка: @{call.from_user.username}\n"
                           f"Заинтересовался: {data['name_project']} ({callback_data.types})", parse_mode="Markdown")
    await call.answer("Запрос отправлен менеджеру!")
