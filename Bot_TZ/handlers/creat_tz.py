from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import *
from pydantic import ValidationError

from Bot_TZ.google_doc.googleSheets import get_id_responsible, get_id_chat, save_tz
from Bot_TZ.function import check_data
from Bot_TZ.keyboard import general as kb


router = Router()


class CreatTZ(StatesGroup):
    Foto = State()
    Text = State()
    Responsible = State()
    Deadline = State()
    Chat_id = State()
    Check = State()


@router.callback_query(F.data == "creat")
async def start_creat(call: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(call.id)
    await call.message.answer("Отправьте фотографию", reply_markup=kb.foto())
    await call.message.delete()
    await state.set_state(CreatTZ.Foto)


@router.message(CreatTZ.Foto, F.photo)
async def set_photo(mess: Message, state: FSMContext):
    photo_id = mess.photo[-1].file_id
    await state.set_data({"id_photo": photo_id})
    await mess.answer("Фотография сохранена.\nВведите описание технического задания")
    await state.set_state(CreatTZ.Text)


@router.callback_query(CreatTZ.Foto, F.data == "skip_foto")
async def skip_photo(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.set_data({"id_photo": None})
    await call.message.answer("Введите описание технического задания")
    await state.set_state(CreatTZ.Text)


@router.message(CreatTZ.Text)
async def set_text(mess: Message, state: FSMContext):
    text = mess.text
    list_id = get_id_responsible()
    await state.update_data({"text": text, "response": list_id})
    await state.set_state(CreatTZ.Responsible)
    text_mess = ""
    k=1
    for i in list_id:
        text_mess += f"{k}. {i[0]}\n"
    await mess.answer(f"Выберите ответственное лицо: \n{text_mess}\n Введите его номер из списка")


@router.message(CreatTZ.Responsible)
async def set_responsible(mess: Message, state: FSMContext):
    responsible_num = int(mess.text)
    data = (await state.get_data())["response"]
    responsible = data[responsible_num-1]
    await state.update_data({"response": responsible})
    await mess.answer("Ответственное лицо назначено.\nВведите дату дедлайна в формате ДД.ММ.ГГГГ")
    await state.set_state(CreatTZ.Deadline)


@router.message(CreatTZ.Deadline)
async def set_deadline(mess: Message, state: FSMContext):
    data = mess.text
    if check_data(data):
        list_id = get_id_chat()
        await state.update_data({"data": data, "chat": list_id})

        text_mess = ""
        k = 1
        for i in list_id:
            text_mess += f"{k}. {i[0]}\n"

        await mess.answer(f"Дата дедлайна сохранена!\n"
                          f"Выберите чаты для рассылки: \n{text_mess}\n"
                          f"Введите номера чатов через пробел!")
        await state.set_state(CreatTZ.Chat_id)
        return
    await mess.answer("Дата введена неправильно. Введите дату в формате ДД.ММ.ГГГГ\nМинимальный срок - завтрашний день!")


@router.message(CreatTZ.Chat_id)
async def set_chat_id(mess: Message, state: FSMContext):
    chat_num = mess.text.split(" ")
    data = (await state.get_data())["chat"]
    chat=[]
    for i in chat_num:
        chat.append(data[int(i)-1])
    await state.update_data({"chat": chat})
    data_all = await state.get_data()
    await mess.answer("Проверьте ТЗ")
    if data_all["id_photo"] is not None:
        msg = await mess.answer_photo(data_all['id_photo'])
        photo_id = msg.photo[-1].file_id
        await state.update_data({"id_photo": photo_id})
    await mess.answer(f"Описание:\n{data_all['text']}\n"
                      f"Ответственный: {data_all['response'][0]}\n"
                      f"Дедлайн: {data_all['data']}\n"
                      f"Отправляем в чаты: {' '.join([i[0] for i in chat])}",
                      reply_markup=kb.check_tz())
    await state.set_state(CreatTZ.Check)


@router.callback_query(CreatTZ.Check, F.data == "start_mail")
async def save_push_tz(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text("Запущен процесс рассылки!", reply_markup=None)
    data_tz = await state.get_data()
    save_tz(data_tz)
    list_mail = [data_tz["response"][1]] + [i[1] for i in data_tz["chat"]]
    dict_mail = {data_tz["response"][1]: data_tz["response"][0]}
    for j in data_tz["chat"]:
        dict_mail[j[1]]=j[0]
    for i in list_mail:
        try:
            if data_tz["id_photo"] is not None:
                await bot.send_photo(i, data_tz["id_photo"])
            await bot.send_message(i, f"Описание:\n{data_tz['text']}\n"
                                      f"Ответственный: {data_tz['response'][0]}\n"
                                      f"Дедлайн: {data_tz['data']}\n")
        except (TelegramForbiddenError, TelegramBadRequest):
            await call.message.answer(f"В <<{dict_mail[i]}>> ТЗ не было доставлено из-за блокировки бота.")
