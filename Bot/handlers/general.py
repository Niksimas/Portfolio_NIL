from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from Bot.keyboard import general as kb

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    photo = "AgACAgIAAxkDAAM1ZWcc-u7acwQ0YKVZnj-w-CuD4LoAArvPMRsCPTlL1fL_i0-77SIBAAMCAAN5AAMzBA"
    # photo = FSInputFile(f"{home}/support_file/start.jpg")
    await message.answer_photo(photo,
                               caption="Наша компания 10 лет на рынке строительства недвижимости.\n"
                                       " Строительство домов из бруса/камня/комбинированные",
                               reply_markup=kb.start())


@router.callback_query(F.data == "contacts")
async def contacts(call: CallbackQuery, bot: Bot):
    await bot.answer_callback_query(call.id)
    await call.message.answer(
        "Home House\nНаходимся в городе Новосибирск\nУл. Семьи Шамшиных, 18\nКонтакты:"
        "\n<a href='tel:+79139009000'>+7-(913)-900-90-00</a>",
        reply_markup=kb.site())


# @router.message()
# async def id_foto(mess: Message, bot: Bot):
#     await bot.download(mess.photo[-1], destination=f"{home}/tmp/1.jpg")
#     photo = FSInputFile(f"{home}/tmp/1.jpg")
#     msg = await bot.send_photo(mess.from_user.id, photo)
#     await mess.answer(msg.photo[-1].file_id)


@router.message(Command("chat_id"))
async def id_foto(mess: Message):
    await mess.answer(f"Telegram ID для чата: {mess.chat.id}")
