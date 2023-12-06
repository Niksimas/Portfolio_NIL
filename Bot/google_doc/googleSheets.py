import gspread
from google.oauth2.service_account import Credentials
from Bot.function import home

scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(f'{home}/google_doc/cred.json')
client = gspread.authorize(credentials.with_scopes(scope))
# Открытие таблицы
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1_NhE6p260SB2P0Zo66sNuAvPsWD2GhGT1uqAM7HNOZc')


def get_record(num_record: int, name_list: str) -> list:
    worksheet = sheet.worksheet(name_list)
    data = worksheet.get_all_values()[1:]
    last_num_record = num_record-1
    if last_num_record < 0:
        return []
    return data[num_record-1]


def save_reviews(data: dict):
    worksheet = sheet.worksheet("review")
    num_record = len(worksheet.get_all_values())
    try:
        list_row = [num_record, data["id_photo"], data["name_project"], data["text"], data["username"]]
    except KeyError:
        list_row = [num_record, "", data["name_project"], data["text"], data["username"]]
    worksheet.append_row(list_row)
    return num_record