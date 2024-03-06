from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from core.handlers import basic as hand_base
from core.keyboard import reply as rep
from core.keyboard import inline as kbi
from core.settings import settings

subrouter = Router()


class FormUnblocking(StatesGroup):
    FIO = State()
    Phone = State()
    City = State()
    CheckMessage = State()


@subrouter.message(FormUnblocking.Phone, F.text == "Отмена")
async def cancel_form(mess: Message, state: FSMContext):
    await mess.answer("Заполнение формы отменено!", reply_markup=ReplyKeyboardRemove())
    await hand_base.start_mess(mess, state)


@subrouter.callback_query(F.data == "no", FormUnblocking.CheckMessage)
@subrouter.callback_query(F.data == "fill_form")
async def set_username(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("Отправь мне ваше ФИО!",  reply_markup=kbi.cancel())
    await state.update_data({"del": msg.message_id})
    await state.set_state(FormUnblocking.FIO)
    return


@subrouter.message(FormUnblocking.FIO)
async def set_phone(mess: Message, state: FSMContext, bot: Bot):
    try:
        msg_del = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.from_user.id, msg_del, reply_markup=None)
    except: pass
    await state.set_data({"fio": mess.text})
    await mess.answer("Благодарю! Нажмите на кнопку, чтобы я запомнил ваш номер телефона",
                      reply_markup=rep.get_contact_btn())
    await state.set_state(FormUnblocking.Phone)
    return


@subrouter.message(FormUnblocking.Phone)
async def set_city(mess: Message, state: FSMContext):
    try:
        await state.update_data({"phone": mess.contact.phone_number})
    except AttributeError:
        await mess.answer("Я не смог определить номер телефона, пожалуйста, нажмите на кнопку")
    await state.set_state(FormUnblocking.CheckMessage)
    await mess.answer("Телефон сохранен!", reply_markup=ReplyKeyboardRemove())
    msg = await mess.answer("Укажите свой город", reply_markup=kbi.cancel())
    await state.update_data({"del": msg.message_id})
    await state.set_state(FormUnblocking.City)
    return


@subrouter.message(FormUnblocking.City)
async def check_form(mess: Message, state: FSMContext, bot: Bot):
    await state.update_data({"city": mess.text})
    try:
        msg_del = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.from_user.id, msg_del, reply_markup=None)
    except: pass
    data = await state.get_data()
    await mess.answer("Проверьте форму:\n\n"
                      f"ФИО: {data['fio']}\n"
                      f"Телефон: {data['phone']}\n"
                      f"Город: {data['city']}\n\n"
                      f"Все верно?", reply_markup=kbi.confirmation())
    await state.set_state(FormUnblocking.CheckMessage)


@subrouter.callback_query(FormUnblocking.CheckMessage, F.data == "yes")
async def check_form(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text("Спасибо за информацию, наш менеджер с вами свяжется!",
                                 reply_markup=kbi.finish_form())
    data = await state.get_data()
    await bot.send_message(settings.bots.chat_nil_id,
                           f"Заявка от бота портфолио другой компании!\n"
                           f"ФИО: {data['fio']}\n"
                           f"Телефон: {data['phone']}\n"
                           f"Город: {data['city']}\n\n")
    await state.clear()
    return
