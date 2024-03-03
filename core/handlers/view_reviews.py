from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from core.keyboard import inline as kb
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
                                     reply_markup=kb.menu_reviews(1, back_btn=False, user_id=call.from_user.id))
        set_statistic("view_reviews", call.from_user.id)
    except KeyError:
        await call.answer("Отзывов на данный момент нет!")
    except TelegramBadRequest:
        await call.message.answer(f"Название проекта:<b> {data['name_project']}</b>\n"
                                     f"Отзыв: {data['text']}\n"
                                     f"Оставил: {data['name']}",
                                     reply_markup=kb.menu_reviews(1, back_btn=False, user_id=call.from_user.id))
        await call.message.delete()
        set_statistic("view_reviews", call.from_user.id)


@router.callback_query(Reviews.filter(F.action == "edit"))
async def viewing_reviews_next_back(call: CallbackQuery, callback_data: Reviews, state: FSMContext):
    await state.clear()
    list_id = database.get_reviews_all_id()
    num_record = callback_data.review_num + callback_data.value
    if num_record < 1:
        await call.answer("Вы достигли начала списка!")
    else:
        try:
            if num_record == len(list_id):
                next_btn = False
            else:
                next_btn = True
            if num_record == 1:
                back_btn = False
            else:
                back_btn = True
            project_id = list_id[num_record - 1]
            data = database.get_review_data(project_id)
            await call.message.edit_text(f"Название проекта:<b> {data['name_project']}</b>\n"
                                         f"Отзыв: {data['text']}\n"
                                         f"Оставил: {data['name']}",
                                         reply_markup=kb.menu_reviews(num_record, user_id=call.from_user.id,
                                                                      back_btn=back_btn, next_btn=next_btn))
            set_statistic("view_reviews", call.from_user.id)
        except IndexError:
            await call.answer("Отзывов больше нет!")
