from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.keyboard.inline import state_cancel


subrouter = Router()


@subrouter.message()
async def check_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    builder = state_cancel()
    await message.answer(f"Бот находится в ожидании ответа. Посмотрите историю сообщений для дальнейшего ответа или нажмите кнопку отмены ожидания ниже",reply_markup=builder.as_markup())


@subrouter.callback_query(F.data == "state_cancel")
async def cancel_state(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await callback.answer("Ожидание ответа успешно отменено.")
    await callback.message.delete()