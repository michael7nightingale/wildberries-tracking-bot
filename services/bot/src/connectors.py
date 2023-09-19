from datetime import timedelta, datetime

from aiogram.types import Message
from aiohttp import ClientSession
from jose import jwt

from settings import get_settings


def encode_token(chat_id: str, settings=get_settings()) -> str:
    token_data = {
        'exp': datetime.now() + timedelta(minutes=settings.EXPIRE_MINUTES),
        'id': chat_id
    }
    return jwt.encode(
        claims=token_data,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


class CustomClientSession(ClientSession):

    def _request(self, method: str, url: str, **kwargs):
        settings = get_settings()
        url = settings.API_BASE_URL + url
        if kwargs.get("headers") is None:
            kwargs['headers'] = {}
        kwargs['headers']['token'] = settings.TELEGRAM_CONTEXT_KEY
        return super()._request(method, url, **kwargs)


async def create_user(chat_id: str):
    async with CustomClientSession() as session:
        async with session.post("users", json={"chat_id": chat_id}) as response:
            return await response.json()


async def create_parsing(title: str, article: str, message: Message):
    data = {
        "title": title,
        "article": article
    }
    async with CustomClientSession(headers={"authorization": encode_token(str(message.chat.id))}) as session:
        async with session.post("parsing", json=data) as response:
            return await response.json()
