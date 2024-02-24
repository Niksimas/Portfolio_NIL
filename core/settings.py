import os

from decouple import config
from dataclasses import dataclass

import gspread
from google.oauth2.service_account import Credentials

# Путь от корня системы до папки core например:
# D:\Programing\Flow_Work\core
home = os.path.dirname(__file__)

@dataclass
class Bots:
    bot_token: str
    admin_id: int
    chat_id: int
    # admin_id_2: int

@dataclass
class Settings:
    bots: Bots
    # db_user: str
    # db_password: str


def get_settings():
    return Settings(
        bots=Bots(
            bot_token=config("token"),
            admin_id=int(config("admin_id")),
            chat_id=int(config("chat_id"))
        ),
        # db_user=config("DB_USER"),
        # db_password=config("DB_PASSWORD")
    )


settings = get_settings()

scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(f'{home}/cred.json')
client = gspread.authorize(credentials.with_scopes(scope))
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1ZdLjtdhlsD3B1wVDQFRfTo3NpvqGyudoitUJLcBuSNo/edit#gid=0')
