from abc import ABC, abstractmethod
from multiprocessing.pool import ThreadPool
from threading import Event
from aiogram.utils import markdown as md

from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time


class BaseParser(ABC):
    """Базовый класс парсера страниц."""
    __slots__ = ("_required", "_sort", "_search", "_threads",
                 "_pool", "_request_parameters", "_event", "_options")    # оптимизация работы с экземплярами класса
    LIMIT: int

    def __init__(self,
                 required: str,
                 search: str,
                 sort: str
                 ):
        # request features
        self._required: str = required
        self._sort: str = sort
        self._search = search
        # threads features
        self._threads: list = []
        self._pool: ThreadPool | None = None
        self._event: Event = Event()
        self._request_parameters: list = []
        # selenium features
        # self._options: Options = Options()
        # self._options.add_experimental_option('excludeSwitches', ['enable-logging'])

    @abstractmethod
    def get_soup(self, url) -> BeautifulSoup:
        """Scroll the page_source and return soup object."""
        pass

    @abstractmethod
    def find_article_match(self, soup: BeautifulSoup) -> int:
        """Looks for all articles in the soup object. Find the self._required."""
        pass

    @abstractmethod
    def find(self, page: int) -> tuple | None:
        """Subtask of the execute method. Gives the result of the separate page."""
        pass

    @abstractmethod
    def execute(self) -> list[tuple | None]:
        """Running the searching process. Very high cost."""
        pass


class Parser(BaseParser):
    """Класс парсера страниц."""
    __slots__ = ()  # наследуется от базового класса

    LIMIT = 30

    def get_soup(self, url) -> BeautifulSoup:
        """Scroll the page_source and return soup object."""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # ua = UserAgent()
        # user_agent = ua.random
        # options.add_argument(f'--user-agent={user_agent}')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print(0)
        actions = ActionChains(driver)
        print(123)
        driver.get(url)
        print(12123123)
        time.sleep(2)

        for _ in range(40):
            actions.send_keys(Keys.END)
            actions.perform()
            time.sleep(0.03)

        yield BeautifulSoup(driver.page_source, "lxml")
        yield driver.close()

    def find_article_match(self, soup: BeautifulSoup) -> int:
        try:
            items = (i.get('data-nm-id') for i in soup.find('div', class_='product-card-list').find_all('article'))
            for pos, item in enumerate(items, 1):
                if item == self._required:
                    return pos

        except AttributeError as e:
            raise e
            # NoneType has no attribute .find_all()
            pass
        finally:
            return 0

    def find(self, page) -> tuple | None:
        print(f"Page: {page}")
        if not self._event.is_set():
            url = f"https://www.wildberries.ru/catalog/0/search.aspx?page={page}&sort={self._sort}&search={self._search}"
            print(url)
            soup_gen = self.get_soup(url)
            soup = next(soup_gen)   # yield soup
            next(soup_gen)  # closing driver
            position = self.find_article_match(soup=soup)
            print(position)
            if position:
                self._event.set()
                print(position, page)
                return position, page

        return None

    def execute(self) -> list[tuple | None]:
        """Running the searching process. Very high cost."""
        self._pool = ThreadPool(processes=10)
        # self._threads = [
        #     self._pool.apply_async(self.find, (page, ))
        #     for page in range(1, self.LIMIT + 1)
        # ]
        self.find(1)
        results = [th.get() for th in self._threads]
        return results


def find_place(title: str, article: str) -> str:
    """Return message with the position of the good."""
    pool = ThreadPool()
    if not article.isdigit():
        return "Артикул должен состоять из целых чисел."

    parser = Parser(
        required=article,
        sort="popular",
        search=title.replace("", "%20")
    )
    find_thread = pool.apply_async(func=parser.execute)
    position = find_thread.get()
    message = md.text(
        md.text(f"Товар с артикулом {md.hstrikethrough(article)} не найден. {md.hbold('Возможные причины:')}\n"),
        md.text("1) Введен несуществующий артикул"),
        md.text(f"2) Товар находится слишком далеко в поисковой выборке ({parser.LIMIT}+ страниц)"),
        sep='\n'
    )
    for pos in position:
        if pos is not None:
            block, page = pos
            message = md.text(
                md.text(f"Товар с артикулом {article} найден. Его положение:\n"),
                md.text(f"Место: {md.hbold(block)}"),
                md.text(f"Страница: {md.hbold(page)}"),
                sep='\n'
            )
            break

    return message


if __name__ == '__main__':
    Parser(
        search="джинсы%20мужские",
        sort="popular",
        required="154746993"
    ).execute()
