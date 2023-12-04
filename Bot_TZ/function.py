import os
import datetime as dt
home = os.path.dirname(__file__)  # Тут сохраняется путь до рабочей папки
admins = [1235360344]  # Список админов


def check_data(data_str: str) -> bool:
    try:
        data_list = [int(i) for i in data_str.split(".")]
        data = dt.date(data_list[-1], data_list[1], data_list[0])
        if data <= dt.date.today():
            return False
        return True
    except (TypeError, ValueError):
        return False
