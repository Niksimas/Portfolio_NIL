from typing import Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Посмотреть отзывы", callback_data=f"see_review")],
        [InlineKeyboardButton(text="Оставить отзыв", callback_data=f"add_review")],
        [InlineKeyboardButton(text="Проекты", callback_data="projects")],
        [InlineKeyboardButton(text="Контакты", callback_data="contacts")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_reviews(num_file: Union[int, str]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Назад", callback_data=f"rback_{num_file}"),
            InlineKeyboardButton(text="В меню", callback_data="start"),
            InlineKeyboardButton(text="Далее", callback_data=f"rnext_{num_file}")
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_projects(num_records) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Назад", callback_data=f"pback_{num_records}"),
            InlineKeyboardButton(text="В меню", callback_data=f"start"),
            InlineKeyboardButton(text="Далее", callback_data=f"pnext_{num_records}")
        ],
        [
            InlineKeyboardButton(text="Нравиться", callback_data=f"plike_{num_records}"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def site() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Наш сайт", url="https://home-house.ru")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def check_up() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="no")
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
