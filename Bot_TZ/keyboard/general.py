from typing import Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Создать ТЗ", callback_data="creat")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def check_tz() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text='Все верно', callback_data=f"start_mail"),
            InlineKeyboardButton(text="Есть косяк", callback_data=f"creat")
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def foto() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text='Пропустить', callback_data="skip_foto")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
