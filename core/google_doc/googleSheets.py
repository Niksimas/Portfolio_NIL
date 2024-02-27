import datetime as dt

from core.statistics.basic import get_statistic
from core.settings import home, sheet


def upload_statistics(city_name: str):
    worksheet = sheet.worksheet("Statistic")
    data = get_statistic()
    worksheet.append_row([dt.date.strftime(dt.date.today(), '%d.%m.%Y'),
                          city_name, data["record_new"], data["record_cancel"], data["record_done"]])
