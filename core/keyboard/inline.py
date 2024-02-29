from .calldata import Project, Reviews

from core.settings import settings
from core.database.database import get_all_id_admin

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start(user_id) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🤖 Боты", callback_data="bot"),
            InlineKeyboardButton(text="🖥 Сайты", callback_data="site"),
            InlineKeyboardButton(text="🎨 Дизайн", callback_data="design"),
         ],
        [
            InlineKeyboardButton(text="💬 Посмотреть отзывы", callback_data=f"see_review"),
            InlineKeyboardButton(text="📝 Оставить отзыв", callback_data=f"add_review")
        ],
        [InlineKeyboardButton(text="📝 Оставить заявку", callback_data="form")],
        [InlineKeyboardButton(text="📌 Контакты", callback_data="contacts")]
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Администратору', callback_data="admin")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def site(link: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🖥 Наш сайт", url=link)],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="start")]
               ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_projects(num_records: int, type_p: str,
                  back_btn: bool = True, next_btn: bool = True) -> InlineKeyboardMarkup:

    if back_btn:
        mess_back = "⬅️ Назад"
    else:
        mess_back = "✖️✖️✖️"
    if next_btn:
        mess_next = "Далее ➡️"
    else:
        mess_next = "✖️✖️✖️"
    buttons = [
        [InlineKeyboardButton(text="❤️ Нравится",
                              callback_data=Project(types=type_p, action="like", id_proj=num_records).pack())],
        [
            InlineKeyboardButton(text=mess_back,
                                 callback_data=Project(types=type_p, action="edit", id_proj=num_records, value=-1).pack()),
            InlineKeyboardButton(text="🏠 В меню", callback_data="start"),
            InlineKeyboardButton(text=mess_next,
                                 callback_data=Project(types=type_p, action="edit", id_proj=num_records, value=1).pack())
        ]
    ]
    builder = InlineKeyboardBuilder(buttons)
    return builder.as_markup()


def menu_reviews(review_id: int, back_btn: bool = True, next_btn: bool = True) -> InlineKeyboardMarkup:
    if back_btn:
        mess_back = "⬅️ Назад"
    else:
        mess_back = "✖️✖️✖️"
    if next_btn:
        mess_next = "Далее ➡️"
    else:
        mess_next = "✖️✖️✖️"

    buttons = [
        [
            InlineKeyboardButton(text=mess_back, callback_data=Reviews(action="edit", review_id=review_id, value=-1).pack()),
            InlineKeyboardButton(text=mess_next, callback_data=Reviews(action="edit", review_id=review_id, value=1).pack())
        ],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="start")]
    ]
    builder = InlineKeyboardBuilder(buttons)
    return builder.as_markup()


def check_up() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🟢 Да", callback_data="yes"),
            InlineKeyboardButton(text="🔴 Нет", callback_data="no")
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def check_review_admin(id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🟢 сохранить", callback_data=f"save_review-{id}"),
            InlineKeyboardButton(text="🔴 удалить", callback_data=f"del_review-{id}")
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def verif_yes():
    buttons = [[InlineKeyboardButton(text="Сохранено! ✅", callback_data="save")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def verif_no():
    buttons = [[InlineKeyboardButton(text="Удалено! ❌", callback_data="del")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def admin_menu(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🔊 Рассылка сообщений по пользователям", callback_data="notif")],
        [InlineKeyboardButton(text="💬 Изменить стартовое сообщение", callback_data="edit_start_mess")],
        [InlineKeyboardButton(text="📱 Изменить контакты", callback_data="edit_contact_mess")],
        [InlineKeyboardButton(text="📊 Просмотр статистики", callback_data="view_statistics")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="users")]
    ]
    if user_id == settings.bots.admin_id:
        buttons.append([InlineKeyboardButton(text="Добавить админа", callback_data="add_admin"),
                        InlineKeyboardButton(text="Удалить админа", callback_data="del_admin")])
    buttons.append([InlineKeyboardButton(text="В меню", callback_data="start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def confirmation(txt_y: str = "🟢 Да", txt_n: str = "🔴 Нет", cd_y: str = "yes", canc_data: str = "admin"):
    buttons = [
        [
            InlineKeyboardButton(text=txt_y, callback_data=cd_y),
            InlineKeyboardButton(text=txt_n, callback_data="no")
        ],
        [InlineKeyboardButton(text="Отмена", callback_data=canc_data)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def state_cancel() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Отменить действие", callback_data="state_cancel"))
    return builder


def cancel_admin():
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="admin")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def del_admin(admins: dict):
    buttons = []
    for i in admins:
        buttons.append([InlineKeyboardButton(text=i["username"], callback_data=f"del_{i['user_id']}")])
    buttons.append([InlineKeyboardButton(text="Отмена", callback_data="admin")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_choose_city_buttons_stat(n: int, city: list):
    n -= 1
    n *= 6
    builder = InlineKeyboardBuilder()
    for i in range(6):
        if n + i <= len(city) - 1:
            button = InlineKeyboardButton(
                text=city[n + i],
                callback_data=f"city_{n + i}")
        else:
            button = InlineKeyboardButton(
                text="➖",
                callback_data=f"none")
        if (n + i) % 3 == 0 or (n + i) % 3 == 3:
            builder.row(button)
        else:
            builder.add(button)
    builder.row(InlineKeyboardButton(
        text="<--",
        callback_data=f"city_back")
    )
    builder.add(InlineKeyboardButton(
        text="Отмена",
        callback_data=f"cancel_form")
    )
    builder.add(InlineKeyboardButton(
        text="-->",
        callback_data=f"city_next")
    )
    return builder.as_markup()


def custom_btn(text: str, cldata: str):
    buttons = [[InlineKeyboardButton(text=text, callback_data=cldata)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cancel():
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="start")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def blocking():
    buttons = [
        [InlineKeyboardButton(text="Заполнить форму", callback_data="fill_form")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="admin")]
               ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def finish_form():
    buttons = [
        [InlineKeyboardButton(text="Наш сайт", url="https://nil-agency.ru/")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="admin")]
               ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
