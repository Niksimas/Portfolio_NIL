from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.filters.state import StateFilter

from Bot.google_doc.googleSheets import save_reviews
from Bot.keyboard import general as kb
from Bot.function import home
from .general import start


router = Router()


class CreatReview(StatesGroup):
    NameProject = State()
    Text = State()
    Photo = State()
    Check = State()


@router.callback_query(F.data == "add_review")
async def viewing_reviews(call: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(call.id)
    await call.message.answer("Укажите название проекта")
    await call.message.delete()
    await state.set_state(CreatReview.NameProject)


@router.message(CreatReview.NameProject)
async def set_name_project(mess: Message, state: FSMContext):
    name = mess.text
    await state.set_data({"name_project": name})
    await mess.answer("Введите текст отзыва")
    await state.set_state(CreatReview.Text)


@router.message(CreatReview.Text)
async def set_text(mess: Message, state: FSMContext):
    text = mess.text
    await state.update_data({"text": text})
    await mess.answer("Если есть фотография прикрепите ее, если нет напишите \"нет\"")
    await state.set_state(CreatReview.Photo)


@router.message(CreatReview.Photo, (F.text == "нет" or F.text == "Нет"))
async def check_up(mess: Message, state: FSMContext):
    await state.set_state(CreatReview.Check)
    data = await state.get_data()
    await mess.answer(f"<b>Название проекта:</b> {data['name_project']}\n"
                      f"{data['text']}\n"
                      f"Оставил: @{mess.from_user.username}\n\n"
                      "Всё верно?", reply_markup=kb.check_up())


@router.message(CreatReview.Photo, F.photo)
async def check_up(mess: Message, state: FSMContext, bot: Bot):
    await state.set_state(CreatReview.Check)
    await bot.download(mess.photo[-1], destination=f"{home}/tmp/{mess.from_user.id}.jpg")
    photo = FSInputFile(f"{home}/tmp/{mess.from_user.id}.jpg")
    msg = await bot.send_photo(mess.from_user.id, photo)
    await state.update_data({"id_photo": msg.photo[-1].file_id})
    data = await state.get_data()
    await mess.answer(f"<b>Название проекта:</b> {data['name_project']}\n"
                      f"{data['text']}\n"
                      f"Оставил: @{mess.from_user.username}\n\n"
                      "Всё верно?", reply_markup=kb.check_up())


@router.callback_query(CreatReview.Check, F.data == "yes")
async def check_yes(call: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.delete()
    data = await state.get_data()
    data["username"] = f"@{call.from_user.username}"
    save_reviews(data)
    await call.answer("Отзыв сохранен!")
    await start(call.message)
    await state.clear()


@router.callback_query(CreatReview.Check, F.data == "no")
async def check_no(call: CallbackQuery, state: FSMContext, bot: Bot):
    print("check_no")
    await bot.answer_callback_query(call.id)
    await call.message.edit_text("Хотите заполнить заново?")
    await state.clear()


@router.callback_query(StateFilter(None), F.data == "yes")
async def check_restart(call: CallbackQuery, state: FSMContext, bot: Bot):
    print("check_restart")
    await call.message.edit_reply_markup(None)
    await viewing_reviews(call, state, bot)


@router.callback_query(StateFilter(None), F.data == "no")
async def check_cancel(call: CallbackQuery):
    print("check_cancel")
    await call.answer("Отменено")
    await start(call.message)