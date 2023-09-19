from services.parser import find_place
from services.telegram import send_message


async def parsing_task_proxy(title: str, article: str, chat_id: str) -> None:
    message = find_place(title, article)
    await send_message(chat_id=chat_id, message=message)
