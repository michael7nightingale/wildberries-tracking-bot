# wildberries-tracking-bot
Трекер положения товара в поисковой выборке Wildberries.

## Возможности 
Несет в себе единственный функционал: отслеживание позиции (место и страница) товара по его артикулу в поисковой выборке Wildberries.
Это может пригодиться, чтобы узнать, попадает ваш товар в топ выборки, или нет.

## Стэк
- __Python >= 3.10 (used pattern matching)__
- selenium
- aiogram
- bs4
- asyncio
- rich

Установить зависимостей: 
```
pip install -r requiremenets.txt 
```

## Запуск бота

```
python main.py
```

## Ограничения в использовании
- Вам потребуется свой токен дял доступа к боту (мой находится в моем .env файле);
- От запроса к запросу выборка меняется, поэтому трудно угадатьЮ, будет ди там ваш товар.;
- Количество просматриваемых страниц выборки по данному запросу ограничено (от 1 до Parser.LIMIT (default=30));
- Очень высокая нагрузка на Python, поскольку простыми requests не воспользоваться (нужно промотать страницу для отображения информации). Отсюда множество потоков и коллекторов.;

(Selenium - единственное, что могло помочь в такой непростой задаче. Я долго мучался в поисках решения, это показалось наиболее оптимальным.)