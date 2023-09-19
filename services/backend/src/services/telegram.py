import json
from aiohttp import ClientSession

from settings import get_settings


async def send_message(
    chat_id: str,
    message: str,
    reply_markup: str | dict | None = None,
    token=get_settings().TELEGRAM_BOT_TOKEN
):
    if reply_markup is None:
        reply_markup = {}
    if not isinstance(reply_markup, str):
        reply_markup = json.dumps(reply_markup)
    async with ClientSession() as session:
        async with session.get(
            url=f'https://api.telegram.org/bot{token}/sendMessage',
            params={
                'chat_id': chat_id,
                'text': message,
                'reply_markup': reply_markup
            }
        ) as response:
            return await response.json()
