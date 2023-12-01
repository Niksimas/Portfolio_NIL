from typing import Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Отзывы", callback_data="review")],
        [InlineKeyboardButton(text="Проекты", callback_data="projects")],
        [InlineKeyboardButton(text="Контакты", callback_data="contacts")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_reviews(num_file: Union[int, str]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Назад", callback_data=f"rback_{num_file}"),
            InlineKeyboardButton(text="Далее", callback_data=f"rnext_{num_file}")
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_projects(num_records) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Назад", callback_data=f"pback_{num_records}"),
            InlineKeyboardButton(text="Нравиться", callback_data=f"plike_{num_records}"),
            InlineKeyboardButton(text="Далее", callback_data=f"pnext_{num_records}")
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def site() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Наш сайт", url="https://home-house.ru")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

