import datetime as dt

from core.statistics.basic import get_statistic
from core.settings import home, sheet
from core.database import database


def upload_statistics():
    worksheet = sheet.worksheet("Statistic")
    data = get_statistic()
    worksheet.append_row([dt.date.strftime(dt.date.today(), '%d.%m.%Y'),
                          data["record_new"], data["record_cancel"], data["record_done"]])


def load_user():
    worksheet = sheet.worksheet("user")
    worksheet.clear()
    records = database.get_all_data_user()
    heading = ["user_id", "link", "is admin", "name", "date registration"]
    worksheet.append_row(heading)
    for i in records:
        worksheet.append_row(i)