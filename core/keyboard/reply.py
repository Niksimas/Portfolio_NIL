from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


def get_contact_btn():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Поделиться контактом", request_contact=True))
    builder.row(KeyboardButton(text="Отмена"))
    return builder.as_markup(resize_keyboard=True)
