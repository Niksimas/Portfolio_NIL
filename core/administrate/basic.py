import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile

from core.database import database
from core.keyboard import inline as kbi
from core.settings import settings, home, set_chat_id
from core.statistics.basic import set_statistic
from core.google_doc.googleSheets import load_user

router = Router()

bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')


@router.callback_query(F.data == "admin")
@router.callback_query(F.data == "no")
async def menu_admins_call(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text("Доступные процессы: ", reply_markup=kbi.admin_menu(call.from_user.id))
    except TelegramBadRequest:
        await call.message.answer("Доступные процессы: ", reply_markup=kbi.admin_menu(call.from_user.id))
        await call.message.delete()
    await state.clear()


@router.callback_query(F.data == "new_chat")
async def manual_new_chat_admin(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Для того чтобы сменить или настроить чат для администраторов, необходимо:\n"
                                 "1. Создать чат\n"
                                 "2. Включить, а затем выключить в новом чате темы\n"
                                 "3. Добавить туда вашего бота\n"
                                 "4. Выдать боту права администратора\n"
                                 "5. Скопировать и отправить команду в новый чат /new_chat_admins",
                                 reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


@router.message(Command("new_chat_admins"), F.chat.type == "supergroup")
async def set_new_chat_admin(mess: Message):
    set_chat_id(mess.chat.id)
    await mess.answer("Новый чат установлен! Не забудьте добавить в него всех администраторов!")


# ############################ Верификация отзыва ############################ #

@router.callback_query(F.data.startswith("save_review"))
async def veryfi_review_ok(call: CallbackQuery):
    review_id = int(call.data.split("-")[-1])
    database.verification_review(review_id)
    await call.message.edit_reply_markup(reply_markup=kbi.verif_yes())
    set_statistic("verify_review_ok", call.from_user.id)


@router.callback_query(F.data.startswith("del_review"))
async def veryfi_review_not_ok(call: CallbackQuery):
    review_id = int(call.data.split("-")[-1])
    database.deleted_review(review_id)
    await call.message.edit_reply_markup(reply_markup=kbi.verif_no())


@router.callback_query(F.data.in_(["save", "del"]))
async def veryfi_review_olds(call: CallbackQuery):
    await call.answer("Все уже сделано, не кипишуй!")


# ############################ Изменить стартовое сообщение ############################ #
class EditStartMess(StatesGroup):
    CheckOldMess = State()
    SetMessage = State()


@router.callback_query(F.data == "edit_start_mess")
async def check_start_mess(call: CallbackQuery, state: FSMContext):
    data_mess = database.get_mess('start')
    if data_mess["photo_id"] is None:
        await call.message.edit_text(f"Сейчас сообщение выглядит так:\n\n{data_mess['text']}\n\n"
                                     "Желаете изменить его?", reply_markup=kbi.confirmation())
    else:
        await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                        reply_markup=kbi.confirmation())
        await call.message.delete()
    await state.set_state(EditStartMess.CheckOldMess)


@router.callback_query(F.data == "yes", EditStartMess.CheckOldMess)
@router.callback_query(F.data == "no", EditStartMess.SetMessage)
async def set_new_start_mess(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text(f"Отправьте новое сообщение (с фотографией и/или форматированием текста):",
                                           reply_markup=kbi.cancel_admin())
    except TelegramBadRequest:
        await call.message.delete()
        msg = await call.message.answer(f"Отправьте новое сообщение (с фотографией и/или форматированием текста):",
                                        reply_markup=kbi.cancel_admin())
    await state.update_data({"del": msg.message_id})
    await state.set_state(EditStartMess.SetMessage)


@router.message(EditStartMess.SetMessage)
async def check_new_mess(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass

    if mess.photo is None:
        await state.update_data({"text": mess.html_text})
        await mess.answer(f"Новое сообщение выглядит теперь так:\n\n{mess.html_text}\n\nСохраняем?",
                          reply_markup=kbi.confirmation())
    else:
        file_id = mess.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        destination = f'{home}/photo/{file_id}.jpg'
        await bot.download_file(file_info.file_path, destination)
        photo = FSInputFile(destination)
        msg1 = await mess.answer("Новое сообщение выглядит теперь так:")
        msg = await mess.answer_photo(photo=photo,
                                      caption=f"{mess.html_text}\n\nСохраняем?",
                                      reply_markup=kbi.confirmation())
        if os.path.exists(destination):
            os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
        await state.update_data({"text": mess.html_text, "photo_id": msg.photo[-1].file_id, "del": msg1.message_id})


@router.callback_query(F.data == "yes", EditStartMess.SetMessage)
async def save_new_start_mess(call: CallbackQuery, state: FSMContext):
    try:
        del_mess = (await state.get_data())["del"]
        await bot.delete_message(call.from_user.id, del_mess)
    except (KeyError, TelegramBadRequest):
        pass
    await call.message.delete()
    data_old = database.get_mess("start")
    if os.path.exists(f"{home}/photo/{data_old['photo_id']}.jpg"):
        os.remove(f"{home}/photo/{data_old['photo_id']}.jpg")
    data = await state.get_data()
    try:
        database.set_mess("start", data["text"], data["photo_id"])
    except KeyError:
        database.set_mess("start", data["text"])
    await call.message.answer("Новое сообщение сохранено!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


# ################################ Добавление удаление администраторов ############################################ #
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
async def del_admin_menu(call: CallbackQuery):
    await call.message.edit_text("Выберите кого удаляем:", reply_markup=kbi.del_admin(database.get_all_data_admin()))


@router.callback_query(F.data.split("_")[0] == "del", StateFilter(None))
async def check_del_admin(call: CallbackQuery):
    name = database.get_user_name(int(call.data.split('_')[-1]))
    await call.message.edit_text(f"Вы уверены в удалении {name}?",
                                 reply_markup=kbi.confirmation(cd_y=f"Yes_{call.data.split('_')[-1]}"))


@router.callback_query(F.data.split("_")[0] == "yes", StateFilter(None))
async def del_admin(call: CallbackQuery):
    database.deleted_admin(int(call.data.split("_")[-1]))
    await call.message.edit_text("Администратор удален!", reply_markup=kbi.admin_menu(call.from_user.id))


# ########################################### Пользователи ##########################################################
# @router.callback_query(F.data == "users", StateFilter(None))
# async def users_info(call: CallbackQuery):
#     data = database.get_all_id_user()
#     mess_out = "Пользователи бота\n"
#     if len(data) >= 5:
#         max_record = 5
#     else:
#         max_record = len(data)
#     for i in range(1, max_record + 1):
#         tpm_data = database.get_data_user(data[-i])
#         tmp = f"{i}. @{tpm_data['link']} - {tpm_data['date_reg']}\n"
#         mess_out += tmp
#     mess_out += (f"\n Общее число пользователей: {len(data)}\n\n"
#                  "Чтобы получить всех пользователей заполните форму заявки")
#     await call.message.edit_text(mess_out, reply_markup=kbi.blocking())


@router.callback_query(F.data == "users", StateFilter(None))
async def del_admin(call: CallbackQuery):
    await call.message.edit_text("Ожидайте загрузки данных!")
    load_user()
    await call.message.edit_text("Данные о пользователях загружены в таблицу:\n"
                                 "https://docs.google.com/spreadsheets/d/1lnam7Vl7DQBTb-8Dna3wRe_w2IUQrECtgf4kSNo-QCM/edit#gid=0")


# ###################################### Изменить контакты ################################################ #
class EditContact(StatesGroup):
    CheckOldMess = State()
    SetMessage = State()


@router.callback_query(F.data == "edit_contact_mess")
async def check_contact_mess(call: CallbackQuery, state: FSMContext):
    data_mess = database.get_mess('contact')
    if data_mess["photo_id"] is None:
        await call.message.edit_text(f"Сейчас сообщение выглядит так:\n\n{data_mess['text']}\n\n"
                                     "Желаете изменить его?", parse_mode="html", reply_markup=kbi.confirmation())
    else:
        await call.message.answer_photo(data_mess["photo_id"], caption=data_mess["text"],
                                        reply_markup=kbi.confirmation())
        await call.message.delete()
    await state.set_state(EditContact.CheckOldMess)


@router.callback_query(F.data == "yes", EditContact.CheckOldMess)
@router.callback_query(F.data == "no", EditContact.SetMessage)
async def set_new_contact_mess(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text(f"Отправьте новое сообщение (с фотографией и/или форматированием текста):",
                                           reply_markup=kbi.cancel_admin())
    except TelegramBadRequest:
        await call.message.delete()
        msg = await call.message.answer(f"Отправьте новое сообщение (с фотографией и/или форматированием текста):",
                                        reply_markup=kbi.cancel_admin())
    await state.update_data({"del": msg.message_id})
    await state.set_state(EditContact.SetMessage)


@router.message(EditContact.SetMessage)
async def check_new_contact_mess(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass

    if mess.photo is None:
        await state.update_data({"text": mess.html_text})
        await mess.answer(f"Новое сообщение выглядит теперь так:\n\n{mess.html_text}\n\nСохраняем?",
                          reply_markup=kbi.confirmation())
    else:
        file_id = mess.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        destination = f'{home}/photo/{file_id}.jpg'
        await bot.download_file(file_info.file_path, destination)
        photo = FSInputFile(destination)
        msg1 = await mess.answer("Новое сообщение выглядит теперь так:")
        msg = await mess.answer_photo(photo=photo,
                                      caption=f"{mess.html_text}\n\nСохраняем?",
                                      reply_markup=kbi.confirmation())
        if os.path.exists(destination):
            os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
        await state.update_data({"text": mess.html_text, "photo_id": msg.photo[-1].file_id, "del": msg1.message_id})


@router.callback_query(F.data == "yes", EditContact.SetMessage)
async def save_new_contact_mess(call: CallbackQuery, state: FSMContext):
    try:
        del_mess = (await state.get_data())["del"]
        await bot.delete_message(call.from_user.id, del_mess)
    except (KeyError, TelegramBadRequest):
        pass
    await call.message.delete()
    data = await state.get_data()
    try:
        database.set_mess("contact", data["text"], data["photo_id"])
    except KeyError:
        database.set_mess("contact", data["text"])
    await call.message.answer("Новое сообщение сохранено!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


# ###################################### Изменить кнопку контактов ################################################ #
class EditContactBtn(StatesGroup):
    CheckOldMess = State()
    SetMessage = State()


@router.callback_query(F.data == "edit_contact_btn")
async def check_data_btn(call: CallbackQuery, state: FSMContext):
    data_mess = database.get_mess('site')
    await call.message.edit_text(f"Сейчас кнопка настроена так:\n\n"
                                 f"Текст: {data_mess['text']}\n"
                                 f"Ссылка: {data_mess['photo_id']}\n\n"
                                 "Желаете изменить его?",
                                 reply_markup=kbi.confirmation(txt_y="Ссылку", txt_n="Текст", cd_y="link", cd_n="text"))
    await state.set_state(EditContact.CheckOldMess)
    await state.update_data({"link": data_mess['photo_id'], "text": data_mess['text']})


@router.callback_query(F.data == "no", EditContactBtn.SetMessage)
@router.callback_query(F.data == "link" or F.data == "text", EditContactBtn.CheckOldMess)
async def set_new_data_btn(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(f"Отправьте новые данные", reply_markup=kbi.cancel_admin())
    await state.set_state(EditContactBtn.SetMessage)
    await state.update_data({"del": msg.message_id, "type": call.data})


@router.message(EditContactBtn.SetMessage)
async def check_new_data_btn(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    data = await state.get_data()
    data[data['type']] = mess.text
    await mess.answer(f"Новые данные для кнопки:\n\n"
                      f"Текст: {data['text']}\n"
                      f"Ссылка: {data['link']}\n"
                      f"Сохраняем?",
                      reply_markup=kbi.confirmation())
    await state.update_data(data)


@router.callback_query(F.data == "yes", EditContactBtn.SetMessage)
async def save_new_data_btn(call: CallbackQuery, state: FSMContext):
    try:
        del_mess = (await state.get_data())["del"]
        await bot.delete_message(call.from_user.id, del_mess)
    except (KeyError, TelegramBadRequest):
        pass
    await call.message.delete()
    data = await state.get_data()
    database.set_mess("contact", data["text"], data["link"])
    await call.message.answer("Новое сообщение сохранено!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()
