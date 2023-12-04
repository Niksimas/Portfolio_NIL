from aiogram.filters import BaseFilter, CommandObject
from aiogram.types import Message

from Bot_TZ.google_doc.googleSheets import get_id_admins


class UserIsAdmin(BaseFilter):
    def __init__(self, *args, **kwargs):
        pass

    async def __call__(self, mess: Message, command: CommandObject) -> bool:
        id_user = str(mess.from_user.id)
        list_admins = get_id_admins()
        return id_user in list_admins
