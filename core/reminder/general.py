from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.statistics.basic import clean_statistic

from core.google_doc.googleSheets import upload_statistics

scheduler = AsyncIOScheduler(timezone="Asia/Novosibirsk")


@scheduler.scheduled_job("cron", hour=0, minute=0)
async def clean_stat():
    upload_statistics()
    clean_statistic()

