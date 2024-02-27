from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.keyboard import inline as kb
from core.handlers.basic import start_call
from core.keyboard.calldata import Reviews
from core.database import database as database
from core.statistics.basic import set_statistic

router = Router()


@router.callback_query(F.data == "see_review")
async def viewing_reviews(call: CallbackQuery):
    list_id = database.get_reviews_all_id()
    data = database.get_review_data(list_id[0])
    try:
        await call.message.edit_text(f"Название проекта:<b> {data['name_project']}</b>\n"
                                     f"Отзыв: {data['text']}\n"
                                     f"Оставил: {data['name']}",
                                     reply_markup=kb.menu_reviews(1))
        set_statistic("view_reviews")
    except KeyError:
        await call.answer("Отзывов на данный момент нет!")


@router.callback_query(Reviews.filter(F.action == "edit"))
async def callbacks_num_change_fab(call: CallbackQuery, callback_data: Reviews):
    list_id = database.get_reviews_all_id()
    num_record = callback_data.review_id + callback_data.value
    if num_record < 1:
        await start_call(call)
    else:
        try:
            project_id = list_id[num_record - 1]
            data = database.get_review_data(project_id)
            await call.message.edit_text(f"Название проекта:<b> {data['name_project']}</b>\n"
                                         f"Отзыв: {data['text']}\n"
                                         f"Оставил: {data['name']}",
                                         reply_markup=kb.menu_reviews(num_record))
            set_statistic("view_reviews")
        except IndexError:
            await call.answer("Отзывов больше нет!")
