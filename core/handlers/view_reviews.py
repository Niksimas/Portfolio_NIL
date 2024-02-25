from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.keyboard import inline as kb
from core.handlers.basic import start_call
from core.keyboard.calldata import Reviews
from core.database import work_db as database

router = Router()


@router.callback_query(F.data == "see_review")
async def viewing_reviews(call: CallbackQuery):
    data = database.get_review_data(1)
    try:
        await call.message.edit_text(f"Название проекта:<b> {data['name_project']}</b>\n"
                                     f"Отзыв: {data['text']}\n"
                                     f"Оставил: {data['name']}",
                                     reply_markup=kb.menu_reviews(1))
    except KeyError:
        await call.answer("Отзывов на данный момент нет!")


@router.callback_query(Reviews.filter(F.action == "edit"))
async def callbacks_num_change_fab(call: CallbackQuery, callback_data: Reviews):
    list_id = database.get_project_all_id(callback_data.types)
    num_record = callback_data.id_proj + callback_data.value
    if num_record < 1:
        await start_call(call)
    else:
        project_id = list_id[num_record - 1]
        data = database.get_review_data(project_id)
        if data == {}:
            await call.answer("Больше отзывов нет!")
        else:
            await call.message.edit_text(f"Название проекта:<b> {data['name_project']}</b>\n"
                                         f"Отзыв: {data['text']}\n"
                                         f"Оставил: {data['name']}",
                                         reply_markup=kb.menu_reviews(project_id))
