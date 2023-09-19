import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import markdown as md
from multiprocessing.pool import ThreadPool
from concurrent.futures.thread import ThreadPoolExecutor

from connectors import create_user, create_parsing
from settings import get_settings
from exceptions import *
from logger import logger, console, log_twice


bot = Bot(token=get_settings().TOKEN)
dp = Dispatcher(bot)

pool = ThreadPool(processes=10)
executor_pool = ThreadPoolExecutor()

users = set()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Начальное сообщение"""
    log_twice("info", f"Got /start: {message}")
    username = message['from']['username']
    text = md.text(
        md.text(f"Добрый день, {md.hbold(username)}!\n"),
        md.text("Вы можете воспользоваться моими услугами трекинга товаров на площадке Wildberries."),
        md.text("Требуемый формат: *поисковый запрос* *артикул* (без знака `*`)"),
        sep='\n'
    )
    await create_user(chat_id=str(message.chat.id))
    await message.answer(text, parse_mode=types.ParseMode.HTML)


@dp.message_handler()
async def search(message: types.Message):
    """Ручка поиска позиции товара в поисковой выдаче."""
    log_twice("info", f"Got message: {message}")
    text = message['text']
    match text.split():
        case [_]:
            await message.reply("Требуемый формат: *поисковый запрос* *артикул* (без знака `*`)")
        case [*search_query, article]:
            user_id = message['from']['id']
            if user_id in users:    # пользователь уже послал запрос
                await message.reply("Ваш предыдущий запрос еще не обработан! Подождите немного.")
            else:

                try:
                    users.add(user_id)      # пользователь добавляется в множество обрабатываемых пользователей

                    await message.reply("Идет поиск...")
                    await create_parsing(" ".join(search_query), article, message)
                except Exception404:        # если не спарсился список продуктов
                    await message.reply(
                        md.text(
                            md.text("Браузер не нашел ничего по запросу:"),
                            md.text(md.hstrikethrough(" ".join(search_query))),
                            sep='\n'
                        ), parse_mode=types.ParseMode.HTML
                    )
                except Exception as e:
                    log_twice("error", str(e))
                    await message.reply("Возникла непредвиденная ошибка. Техническая поддержка оповещена.")
                finally:
                    users.remove(user_id)    # пользователь удаляется из множества обрабатываемых пользователей
