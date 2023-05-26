import asyncio
import os
from typing import Sequence
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import markdown as md
from multiprocessing.pool import ThreadPool
from concurrent.futures.thread import ThreadPoolExecutor

from .parser import Parser
from .exceptions import *
from .logger import logger, console, log_twice


load_dotenv()   # keys from .env file

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot)

pool = ThreadPool(processes=10)
executor_pool = ThreadPoolExecutor()

users = set()


def find_place(query: Sequence[str], article: str) -> str:
    """Return message with the position of the good."""
    if not article.isdigit():
        return "Артикул должен состоять из целых чисел."

    parser = Parser(
        required=article,
        sort="popular",
        search="%20".join(query),

    )
    find_thread = pool.apply_async(func=parser.execute)
    position = find_thread.get()
    message = md.text(
        md.text(f"Това с артикулом {md.hstrikethrough(article)} не найден. {md.hbold('Возможные причины:')}\n"),
        md.text("1) Введен несуществующий артикул"),
        md.text(f"2) Товар находится слишком далеко в поисковой выборке ({parser.LIMIT}+ страниц)"),
        sep='\n'
    )
    for pos in position:
        if pos is not None:
            block, page = pos
            message = md.text(
                md.text(f"Това с артикулом {article} найден. Его положение:\n"),
                md.text(f"Место: {md.hbold(block)}"),
                md.text(f"Страница: {md.hbold(page)}"),
                sep='\n'
            )
            break

    return message


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Начальное сообщение"""
    log_twice("info", f"Got /start: {message}")
    username = message['from']['username']
    text = md.text(
        md.text(f"Добрый день, {md.hbold(username)}!\n"),
        md.text("Вы можете воспользоваться моими услугами трекинга товаров на площадке Wildberries."),
        md.text("Требуемый формат: [поисковый запрос] [артикул]"),
        sep='\n'
    )
    await message.answer(text, parse_mode=types.ParseMode.HTML)


@dp.message_handler()
async def search(message: types.Message):
    """Ручка поиска позиции товара в поисковой выдаче."""
    log_twice("info", f"Got message: {message}")
    text = message['text']
    match text.split():
        case [_]:
            await message.reply("Требуемый формат: [поисковый запрос] [артикул]")
        case [*search_query, article]:
            user_id = message['from']['id']
            if user_id in users:    # пользователь уже послал запрос
                await message.reply("Ваш предыдущий запрос еще не обработан! Подождите немного.")
            else:
                try:
                    users.add(user_id)      # пользователь добавляется в множество обрабатываемых пользователей

                    await message.reply("Идет поиск...")
                    loop = asyncio.get_running_loop()
                    msg = await loop.run_in_executor(executor_pool, find_place, search_query, article)
                    await message.reply(msg, parse_mode=types.ParseMode.HTML)

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


def run_forever() -> None:
    log_twice("info", "Bot started!")
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True
    )


if __name__ == '__main__':
    run_forever()
