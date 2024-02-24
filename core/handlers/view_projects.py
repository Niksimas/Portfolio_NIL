from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile

from core.handlers.basic import start_call
from core.settings import settings, home
from core.keyboard import inline as kb
from core.keyboard.calldata import Project
from core.database import work_db as database

router = Router()


@router.callback_query(F.data.in_(["design", "site", "bot"]))
async def viewing_projects(call: CallbackQuery):
    data = database.get_project_data(1, call.data)
    try:
        if data["name_photo"] == "none":
            await call.message.edit_text(f"Название: {data['name_project']}\n"
                                         f"Описание: {data['description']}",
                                         reply_markup=kb.menu_projects(1, call.data))
        else:
            photo = FSInputFile(f"{home}/photo/{data['name_photo']}.jpg")
            await call.message.answer_photo(photo,
                                            caption=f"Название: {data['name_project']}\nОписание: {data['description']}",
                                            reply_markup=kb.menu_projects(1, call.data))
    except KeyError:
        await call.answer("Кейсов на данный момент нет!")


@router.callback_query(Project.filter(F.action == "edit"))
async def callbacks_num_change_fab(call: CallbackQuery, callback_data: Project):
    project_id = callback_data.id_proj + callback_data.value
    if project_id < 1:
        await start_call(call)
    else:
        data = database.get_project_data(project_id, callback_data.types)
        if data == {}:
            await call.answer("Больше кейсов нет!")
        else:
            if data["name_photo"] == "none":
                await call.message.edit_text(f"Название: {data['name_project']}\n"
                                             f"Описание: {data['description']}",
                                             reply_markup=kb.menu_projects(project_id, callback_data.types))
            else:
                photo = FSInputFile(f"{home}/photo/{data['name_photo']}.jpg")
                await call.message.answer_photo(photo,
                                                caption=f"Название: {data['name_project']}\nОписание: {data['description']}",
                                                reply_markup=kb.menu_projects(project_id, callback_data.types))


@router.callback_query(Project.filter(F.action == "like"))
async def like(call: CallbackQuery, bot: Bot, callback_data: Project):
    data = database.get_project_data(callback_data.id_proj, callback_data.types)
    await bot.send_message(settings.bots.chat_id,
                           f"Пользователь:\n"
                           f"Имя: [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n"
                           f"Ссылка: @{call.from_user.username}\n"
                           f"Заинтересовался: {data['name_project']} ({callback_data.types})")
    await call.answer("Запрос отправлен менеджеру!")
