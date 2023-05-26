from abc import ABC, abstractmethod
from multiprocessing.pool import ThreadPool
from threading import Event
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time

from .exceptions import *


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
        self._options: Options = Options()
        self._options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self._options.headless = True    # without opening the browser window

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
        driver = webdriver.Chrome(options=self._options)
        actions = ActionChains(driver)
        driver.get(url)
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

        except AttributeError:      # NoneType has no attribute .find_all()
            pass
        finally:
            return 0

    def find(self, page) -> tuple | None:
        if not self._event.is_set():
            url = f"https://www.wildberries.ru/catalog/0/search.aspx?page={page}&sort={self._sort}&search={self._search}"
            soup_gen = self.get_soup(url)
            soup = next(soup_gen)   # yield soup
            next(soup_gen)  # closing driver
            position = self.find_article_match(soup=soup)
            # print(position)
            if position:
                self._event.set()
                print(position, page)
                return position, page

        return None

    def execute(self) -> list[tuple | None]:
        """Running the searching process. Very high cost."""
        self._pool = ThreadPool(processes=10)
        self._threads = [
            self._pool.apply_async(self.find, (page, ))
            for page in range(1, self.LIMIT + 1)
        ]

        results = [th.get() for th in self._threads]
        return results


if __name__ == '__main__':

    pars = Parser(
        required="137296322",
        sort="popular",
        search="мармелад"
    )
    pars.execute()

