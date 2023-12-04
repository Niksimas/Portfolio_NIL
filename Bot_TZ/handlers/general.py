from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from Bot_TZ.keyboard import general as kb
from Bot_TZ.filters.filters import UserIsAdmin

router = Router()


@router.message(CommandStart(), UserIsAdmin())
async def start(message: Message):
    await message.answer("Заполнте ваше ТЗ", reply_markup=kb.start())


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("У вас не достаточно прав(")


@router.message(Command("chat_id"))
async def id_foto(mess: Message):
    await mess.answer(f"Telegram ID чата: {mess.chat.id}")


@router.message(Command("my_id"))
async def id_foto(mess: Message):
    await mess.answer(f"Telegram ID пользователя: {mess.from_user.id}")
