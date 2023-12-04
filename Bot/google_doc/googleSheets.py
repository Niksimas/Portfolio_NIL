import gspread
from google.oauth2.service_account import Credentials
from Project.function import home

scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(f'{home}/google_doc/cred.json')
client = gspread.authorize(credentials.with_scopes(scope))
# Открытие таблицы
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1_NhE6p260SB2P0Zo66sNuAvPsWD2GhGT1uqAM7HNOZc')

# sheet = client.open('Your Sheet Name')
# Выбор листа по индексу (начиная с 0) или названию
# worksheet = sheet.worksheet("global")


def get_record(num_record: int, name_list: str) -> list:
    worksheet = sheet.worksheet(name_list)
    data = worksheet.get(f"A{num_record+1}:D{num_record+1}")
    return data[0]

# worksheet = sheet.worksheet('Your Worksheet Name')
# # Запись данных в пустую ячейку в один столбец
# data = 'Hello World!'  # Данные для записи
# column_index = 1  # Индекс столбца, в котором нужно записать данные (начиная с 1)
#
# # Получение последней заполненной ячейки в столбце
# last_cell = worksheet.findall("")[-1]
#
# # Получение координат следующей пустой ячейки в столбце
# next_empty_cell = (last_cell.row + 1, column_index)
#
# # Запись данных в следующую пустую ячейку
# worksheet.update_cell(next_empty_cell[0], next_empty_cell[1], data)

# print(get_record(3,"project"))
