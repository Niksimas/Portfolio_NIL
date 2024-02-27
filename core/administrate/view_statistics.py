import datetime as dt

from aiogram import Router, F
from aiogram.types import CallbackQuery


from core.keyboard import inline as kbi
from core.statistics.basic import get_statistic

router = Router()


@router.callback_query(F.data == "view_statistics")
async def menu_admins(call: CallbackQuery):
    data = get_statistic()
    await call.message.edit_text(f"Статистика за {dt.date.strftime(dt.date.today(), '%d.%m.%Y')}\n"
                                 f"👤 Новые люди: {data['new_user']}\n\n"
                                 "Просмотры: \n "
                                 f"🤖 боты: {data['view_project_bot']}\n" 
                                 f"🖥 сайты: {data['view_project_site']}\n"
                                 f"🎨 дизайн: {data['view_project_design']}\n"
                                 f"📌 контакты: {data['view_contact']}\n\n"
                                 f"💭 Новые отзывы: {data['verify_review']}\n"
                                 f"💬 Подтвержденные отзывы: {data['verify_review_ok']}\n",
                                 reply_markup=kbi.custom_btn("Назад", "admin"))


# from core.handlers.courier import scheduler
from core.google_doc.googleSheets import upload_statistics

# @scheduler.scheduled_job("cron", hour=23, minute=58)
# async def upload_stat():
#     for i in city_info:
#         upload_statistics(i["Город"], i["chat id"])
#         clean_statistic(i["chat id"])
