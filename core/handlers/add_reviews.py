from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message


from core.statistics.basic import set_statistic
from core.database import database as database
from core.keyboard import inline as kb
from core.settings import home, settings


router = Router()


class CreatReview(StatesGroup):
    NameProject = State()
    Text = State()
    Check = State()


@router.callback_query(F.data == "add_review")
async def viewing_reviews(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Укажите название проекта")
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
    data = await state.get_data()
    await mess.answer(f"<b>Название проекта:</b> {data['name_project']}\nОтзыв: {data['text']}\n"
                      f"Оставил: {mess.from_user.first_name}\n\nВсё верно?",
                      reply_markup=kb.check_up())
    await state.set_state(CreatReview.Check)


@router.callback_query(CreatReview.Check, F.data == "yes")
async def check_yes(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    data["name"] = f"{call.from_user.first_name}"
    review_id = database.save_new_review(data)
    await call.message.edit_text("Отзыв отправлен на модерацию! Благодарим, что уделили нам время!",
                                 reply_markup=kb.start(call.from_user.id))
    await state.clear()
    set_statistic("verify_review")
    mess = (f"Название проекта: <b>{data['name_project']}</b>\nОтзыв:\n {data['text']}\n"
            f"Оставил: [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n\n")
    await bot.send_message(settings.bots.chat_id, "Оставлен отзыв!\n\n" + mess, parse_mode="Markdown",
                           reply_markup=kb.check_review_admin(review_id))
