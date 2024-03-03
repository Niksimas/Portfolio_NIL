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
            InlineKeyboardButton(text="💭 Оставить отзыв", callback_data=f"add_review")
        ],
        [InlineKeyboardButton(text="📝 Оставить заявку", callback_data="form")],
        [InlineKeyboardButton(text="📌 Контакты", callback_data="contacts")]
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Администратору', callback_data="admin")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def site(text: str, link: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=text, url=link)],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="start")]
               ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_projects(num_records: int, type_p: str,  user_id: int, id_proj: int,
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
                              callback_data=Project(types=type_p, action="like", num_proj=num_records,).pack())],
        [
            InlineKeyboardButton(text=mess_back,
                                 callback_data=Project(types=type_p, action="edit", num_proj=num_records, value=-1).pack()),
            InlineKeyboardButton(text="🏠 В меню", callback_data="start"),
            InlineKeyboardButton(text=mess_next,
                                 callback_data=Project(types=type_p, action="edit", num_proj=num_records, value=1).pack())
        ]
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([
            InlineKeyboardButton(text='⭐️ Изменить', callback_data=Project(types=type_p, action="modify", num_proj=num_records, id_proj=id_proj).pack()),
            InlineKeyboardButton(text='⭐️ Удалить', callback_data=Project(types=type_p, action="deleted", num_proj=num_records, id_proj=id_proj).pack()),
        ])
    builder = InlineKeyboardBuilder(buttons)
    return builder.as_markup()


def menu_reviews(review_num: int, user_id: int, back_btn: bool = True, next_btn: bool = True) -> InlineKeyboardMarkup:
    if back_btn:
        mess_back = "⬅️ Назад"
    else:
        mess_back = "✖️✖️✖️"
    if next_btn: mess_next = "Далее ➡️"
    else: mess_next = "✖️✖️✖️"

    buttons = [
        [
            InlineKeyboardButton(text=mess_back, callback_data=Reviews(action="edit", review_num=review_num, value=-1).pack()),
            InlineKeyboardButton(text=mess_next, callback_data=Reviews(action="edit", review_num=review_num, value=1).pack())
        ],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="start")]
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([
            InlineKeyboardButton(text='⭐️ Изменить',
                                 callback_data=Reviews(action="modify", review_num=review_num).pack()),
            InlineKeyboardButton(text='⭐️ Удалить',
                                 callback_data=Reviews(action="deleted", review_num=review_num).pack()),
        ])
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
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="users")],
        [InlineKeyboardButton(text="💬 Изменить стартовое сообщение", callback_data="edit_start_mess")],
        [InlineKeyboardButton(text="🔊 Рассылка сообщений по пользователям", callback_data="notif")],
        [InlineKeyboardButton(text="📱 Изменить контакты", callback_data="edit_contact_mess")],
        [InlineKeyboardButton(text="🔗 Изменить кнопку перехода на сайт", callback_data="edit_contact_btn")],
        [InlineKeyboardButton(text="📊 Просмотр статистики", callback_data="view_statistics")],
        [InlineKeyboardButton(text="🔁 Сменить чат администраторов", callback_data="new_chat")],
        [
            InlineKeyboardButton(text="+📂 Добавить проект", callback_data="add_project"),
            InlineKeyboardButton(text="+💬 Добавить отзыв", callback_data="add_review_admin")
        ],
    ]
    if user_id == settings.bots.admin_id:
        buttons.append([InlineKeyboardButton(text="Добавить админа", callback_data="add_admin"),
                        InlineKeyboardButton(text="Удалить админа", callback_data="del_admin")])
    buttons.append([InlineKeyboardButton(text="В меню", callback_data="start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def confirmation(txt_y: str = "🟢 Да", txt_n: str = "🔴 Нет", cd_y: str = "yes", cd_n: str = "no", canc_data: str = "admin"):
    buttons = [
        [
            InlineKeyboardButton(text=txt_y, callback_data=cd_y),
            InlineKeyboardButton(text=txt_n, callback_data=cd_n)
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
    for i in admins.keys():
        buttons.append([InlineKeyboardButton(text=admins[i], callback_data=f"del_{i}")])
    buttons.append([InlineKeyboardButton(text="Отмена", callback_data="admin")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


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


def type_project():
    buttons = [
        [
            InlineKeyboardButton(text="🤖 Боты", callback_data="add_bot"),
            InlineKeyboardButton(text="🖥 Сайты", callback_data="add_site"),
            InlineKeyboardButton(text="🎨 Дизайн", callback_data="add_design"),
        ],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="admin")]
               ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def del_record(yes_data: Project | Reviews, cancel_data: Project | Reviews) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Да", callback_data=yes_data.pack())],
        [InlineKeyboardButton(text="Отмена", callback_data=cancel_data.pack())]
    ]
    builder = InlineKeyboardBuilder(buttons)
    return builder.as_markup()


def edit_project(calldata: Project) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Фотографию", callback_data="photo")],
        [InlineKeyboardButton(text="Название", callback_data="name_project")],
        [InlineKeyboardButton(text="Описание", callback_data="description")],
        [InlineKeyboardButton(text="Отмена", callback_data=Project(types=calldata.types, action="edit", num_proj=calldata.num_proj, value=0).pack())]
    ]
    builder = InlineKeyboardBuilder(buttons)
    return builder.as_markup()


def cancel_record(calldata: Project | Reviews):
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data=calldata.pack())]]
    builder = InlineKeyboardBuilder(buttons)
    return builder.as_markup()


def confirmation_project(type: str, id_proj: int, num_proj:  int):
    buttons = [
        [
            InlineKeyboardButton(text="🟢 Да", callback_data=Project(types=type, action="yes_mod", num_proj=num_proj, id_proj=id_proj, value=0).pack()),
            InlineKeyboardButton(text="🔴 Нет", callback_data=Project(types=type, action="modify", num_proj=num_proj, id_proj=id_proj).pack())
        ],
        [InlineKeyboardButton(text="Отмена", callback_data=Project(types=type, action="edit", num_proj=num_proj, value=0).pack())]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def confirmation_review(review_num: int):
    buttons = [
        [
            InlineKeyboardButton(text="🟢 Да", callback_data=Reviews(action="yes_mod", review_num=review_num, value=0).pack()),
            InlineKeyboardButton(text="🔴 Нет", callback_data=Reviews(action="modify", review_num=review_num).pack())
        ],
        [InlineKeyboardButton(text="Отмена", callback_data=Reviews(action="edit", review_num=review_num, value=0).pack())]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def edit_review(calldata: Reviews) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Название проекта", callback_data="name_project")],
        [InlineKeyboardButton(text="Отзыв", callback_data="text")],
        [InlineKeyboardButton(text="Кто оставил отзыв", callback_data="name")],
        [InlineKeyboardButton(text="Отмена", callback_data=Reviews(action="edit", review_num=calldata.review_num, value=0).pack())]
    ]
    builder = InlineKeyboardBuilder(buttons)
    return builder.as_markup()