import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.settings import home
from core.database.database import get_all_id_photo
from core.statistics.basic import clean_statistic
from core.google_doc.googleSheets import upload_statistics

scheduler = AsyncIOScheduler(timezone="Asia/Novosibirsk")


@scheduler.scheduled_job("cron", hour=0, minute=0)
async def clean_stat():
    upload_statistics()
    clean_statistic()


@scheduler.scheduled_job("cron", hour=0, minute=0)
async def clear_photo():
    all_photo_id = get_all_id_photo()
    for i in os.listdir(path=f"{home}/photo"):
        if i.split(".")[0] not in all_photo_id:
            os.remove(f"{home}/photo/{i}")
