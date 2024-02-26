import asyncio

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramBadRequest

from core.settings import settings, home
from core.keyboard import inline as kbi
from core.database import database

router = Router()

bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')


@router.callback_query(F.data == "admin")
async def menu_admins(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Доступные процессы:", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


# ############################ Верификация отзыва ############################ #

@router.callback_query(F.data.startswith("save_review"))
async def menu_admins(call: CallbackQuery):
    review_id = int(call.data.split("-")[-1])
    database.verification_review(review_id)
    await call.message.edit_reply_markup(reply_markup=kbi.verif_yes())


@router.callback_query(F.data.startswith("save_review"))
async def menu_admins(call: CallbackQuery):
    review_id = int(call.data.split("-")[-1])
    database.deleted_review(review_id)
    await call.message.edit_reply_markup(reply_markup=kbi.verif_no())


@router.callback_query(F.data.in_(["save", "del"]))
async def menu_admins(call: CallbackQuery):
    await call.answer("Все уже сделано, не кипишуй!")


# ############################ Изменить стартовое сообщение ############################ #
class EditStartMess(StatesGroup):
    CheckOldMess = State()
    SetMessage = State()


@router.callback_query(F.data == "edit_start_mess")
async def check_start_mess(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"Сейчас сообщение выглядит так:\n\n{database.get_mess('start')}\n\n"
                                 "Желаете изменить его?", reply_markup=kbi.confirmation())
    await state.set_state(EditStartMess.CheckOldMess)


@router.callback_query(F.data == "yes", EditStartMess.CheckOldMess)
@router.callback_query(F.data == "no", EditStartMess.SetMessage)
async def set_new_start_mess(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(f"Отправьте новое сообщение:", reply_markup=kbi.cancel_admin())
    await state.update_data({"del": msg.message_id})
    await state.set_state(EditStartMess.SetMessage)


@router.message(F.photo, EditStartMess.SetMessage)
async def answer_to_photo(mess: Message):
    await mess.answer("Нельзя установить фотографию! Отправьте только текст!")


@router.message(EditStartMess.SetMessage)
async def check_new_mess(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    await state.update_data({"text": mess.html_text})
    await mess.answer(f"Новое сообщение выглядит теперь так:\n\n{mess.html_text}\n\nСохраняем?",
                      reply_markup=kbi.confirmation())


@router.callback_query(F.data == "yes", EditStartMess.SetMessage)
async def save_new_start_mess(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    database.set_mess("start", data["text"])
    await call.message.edit_text("Новое сообщение сохранено!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


# #############################################################################3 #
@router.callback_query(F.data == "add_admin")
async def add_admin(call: CallbackQuery, bot: Bot):
    await call.message.edit_text("Отправьте новому администратору ссылку:\n"
                                 f"https://t.me/{(await bot.me()).username}?start={call.message.message_id}")
    with open(f"{home}/administrate/code.txt", "w") as f:
        f.write(str(call.message.message_id))


def check_code_admin(code_in: int) -> bool:
    with open(f"{home}/administrate/code.txt", "r+") as f:
        try:
            saved_code = int(f.read())
        except:
            return False
        f.write("a")
    return saved_code == code_in


@router.callback_query(F.data.split("_")[0] == "no", StateFilter(None))
@router.callback_query(F.data == "del_admin")
async def del_admin(call: CallbackQuery):
    await call.message.edit_text("Выберите кого удаляем:", reply_markup=kbi.del_admin(database.get_all_data_admin()))


@router.callback_query(F.data.split("_")[0] == "del", StateFilter(None))
async def del_admin(call: CallbackQuery):
    name = database.get_user(int(call.data.split('_')[-1]))
    await call.message.edit_text(f"Вы уверены в удалении {name}?",
                                 reply_markup=kbi.confirmation(cd_y=f"Yes_{call.data.split('_')[-1]}"))


@router.callback_query(F.data.split("_")[0] == "yes", StateFilter(None))
async def del_admin(call: CallbackQuery):
    database.deleted_admin(int(call.data.split("_")[-1]))
    await call.message.edit_text("Администратор удален!", reply_markup=kbi.admin_menu(call.from_user.id))
