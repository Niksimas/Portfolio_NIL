from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest

from core.statistics.basic import set_statistic
from core.database import database as database
from core.keyboard import inline as kb
from core.settings import home, settings, get_chat_id


router = Router()


class CreatReview(StatesGroup):
    NameProject = State()
    Text = State()
    Check = State()


@router.callback_query(CreatReview.Check, F.data == "no")
@router.callback_query(F.data == "add_review")
async def set_name_review(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text("Укажите название проекта", reply_markup=kb.cancel())
    except TelegramBadRequest:
        msg = await call.message.answer("Укажите название проекта", reply_markup=kb.cancel())
        await call.message.delete()
    await state.update_data({"del": msg.message_id})
    await state.set_state(CreatReview.NameProject)


@router.message(CreatReview.NameProject)
async def set_text_review(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    await state.set_data({"name_project": mess.text})
    msg = await mess.answer("Введите текст отзыва")
    await state.update_data({"del": msg.message_id})
    await state.set_state(CreatReview.Text)


@router.message(CreatReview.Text)
async def check_review(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    await state.update_data({"text": mess.text})
    data = await state.get_data()
    await mess.answer(f"<b>Название проекта:</b> {data['name_project']}\nОтзыв: {data['text']}\n"
                      f"Оставил: {mess.from_user.first_name}\n\nВсё верно?",
                      reply_markup=kb.check_up())
    await state.set_state(CreatReview.Check)


@router.callback_query(CreatReview.Check, F.data == "yes")
async def send_verification(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    data["name"] = f"{call.from_user.first_name}"
    review_id = database.save_new_review(data)
    await call.message.edit_text("Отзыв отправлен на модерацию! Благодарим, что уделили нам время!",
                                 reply_markup=kb.start(call.from_user.id))
    await state.clear()
    set_statistic("verify_review", call.from_user.id)
    mess = (f"Название проекта: <b>{data['name_project']}</b>\nОтзыв:\n {data['text']}\n"
            f"Оставил: [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n\n")
    await bot.send_message(get_chat_id(), "Оставлен отзыв!\n\n" + mess, parse_mode="Markdown",
                           reply_markup=kb.check_review_admin(review_id))
