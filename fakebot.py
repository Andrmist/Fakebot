import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from dotenv import load_dotenv
from os import getenv

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

bad_channels = [
    "boris_rozhin",
    "grey_zone",
    "go338",
    "omonmoscow",
    "wingsofwar",
    "chvkmedia",
    "hackberegini",
    "mig41",
    "pezdicide",
    "SergeyKolyasnikov",
    "MedvedevVesti",
    "SIL0VIKI",
    "balkanossiper",
    "pl_syrenka",
    "brussinf",
    "lady_north",
    "sex_drugs_kahlo",
    "usaperiodical",
    "russ_orientalist",
    "vladlentatarsky @neoficialniybezsonov",
    "rybar",
    "milinfolive"
]


@dp.message_handler(commands=["start", "info"])
async def start(message: types.Message):
    await message.answer("Вітаю! Цей бот фільтрує ваш чат від каналів, які містять інформацію про наші війська, а також проросійські канали, які поширюють фейки та дезінформацію\nСписок каналів, що ми блокуємо: /list\nЯкщо ви знаєте більше каналів, відсилайте @Andrmist")


@dp.message_handler(commands=["list"])
async def list(message: types.Message):
    await message.answer("Список каналів:\n" + "\n".join([f"- @{channel}" for channel in bad_channels]))


@dp.message_handler()
async def on_bad_forward(message: types.Message):
    if message.is_forward() and message.forward_from_chat.username in bad_channels:
        await message.reply(
            "❗️УВАГА️❗️\nЦей канал публікує інформацію про наші війська, а також може містити дезінформацію!\nПосилання на канал, щоб поскаржитися: @" + message.forward_from_chat.username)
        await message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
