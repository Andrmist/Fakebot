import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ContentType
from aiogram.utils.exceptions import ChatNotFound, RetryAfter
from asyncio import sleep
from old_list import most_trustable_list
from telethon import TelegramClient, events
import re

from dotenv import load_dotenv
from os import getenv

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = int(getenv("TELEGRAM_API_ID"))
api_hash = getenv("TELEGRAM_API_HASH")

client = TelegramClient('fetch_bad_channels', api_id, api_hash)
client.start()


async def get_bad_channels():
    res = most_trustable_list
    async for message in client.iter_messages('@stoprussiachannel'):
        if message.text and "БЛОКУЄМО" in message.text:
            link = re.search(r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
                            message.text)
            res.append(link.group(1)[1:])
    return res


@dp.message_handler(commands=["start", "info"])
async def start(message: types.Message):
    await message.answer(
        "Вітаю! Цей бот фільтрує ваш чат від каналів, які містять інформацію про наші війська, а також проросійські "
        "канали, які поширюють фейки та дезінформацію\nСписок каналів, що ми блокуємо: /list\nЯкщо ви знаєте більше "
        "каналів, відсилайте @Andrmist")


@dp.message_handler(commands=["list"])
async def list_channels(message: types.Message):
    await message.answer("Список каналів:\n" + "\n".join([f"- {'@' if not channel[0] == '+' else 'https://t.me/'}{channel}" for channel in await get_bad_channels()]))


@dp.message_handler(commands=["test"])
async def test(message: types.Message):
    res = []
    for channel in await get_bad_channels():
        for attempt in range(5):
            try:
                logging.log(logging.INFO, f"Checking @{channel}")
                is_exists = await bot.get_chat(f"{'@' if not channel[0] == '+' else ''}{channel}")
                if is_exists and channel not in res:
                    res.append(channel)
            except ChatNotFound:
                logging.log(logging.WARN, f"@{channel} not found :c")
            except RetryAfter as e:
                logging.log(logging.WARN, f"flood, retrying in {e.timeout}")
                await sleep(e.timeout)
                continue
            finally:
                await sleep(1)
                break
    await message.answer('[\n' + "\n".join(f"\"{a}\",\n" for a in res) + "\n]")


@dp.message_handler(content_types=ContentType.ANY)
async def on_bad_forward(message: types.Message):
    # print(message.text)
    if message.is_forward() and message.forward_from_chat.username in await get_bad_channels():
        await message.reply(
            "❗️УВАГА️❗️\nЦей канал публікує інформацію про наші війська, а також може містити дезінформацію!\nПосилання на канал, щоб поскаржитися: @" + message.forward_from_chat.username + "\nЯкщо цей канал знаходиться тут помилково, звертатися до @Andrmist")
        await message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
