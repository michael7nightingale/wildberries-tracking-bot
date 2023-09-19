import asyncio
from celery import Celery
from asgiref.sync import async_to_sync

from settings import get_settings
from internal.tasks import parsing_task_proxy


class AsyncCelery(Celery):
    """
    Celery inherit class to enter async context on initializing.
    """

    def on_init(self):
        """Configurate on init celery instance function."""
        loop = asyncio.new_event_loop()     # create event loop for running coroutines
        asyncio.set_event_loop(loop)


app = AsyncCelery(__name__,  backend='amqp', broker='amqp://')
app.config_from_object(get_settings(), namespace='CELERY')


@app.task
def parsing_task(title: str, article: str, chat_id: str) -> None:
    async_to_sync(parsing_task_proxy)(title, article, chat_id)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Sets up celery periodic tasks."""
