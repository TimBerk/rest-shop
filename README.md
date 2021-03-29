# Интернет-магазин

REST API сервис для интернет-магазина по доставке конфет "Сласти от всех напастей".

Требования
===

- Poetry 1.1+
- Python 3.7+
- Django 3+

Установка
===

- Установка зависимостей для питона `poetry install`
- Применение миграций `make migrate`

## Built With

* [Django](https://www.djangoproject.com/) -  web framework written in Python.
* [Django environ’s](https://django-environ.readthedocs.io/en/latest/) - Django-environ allows to utilize 12factor inspired environment variables to configure Django application.
* [Django REST](https://www.django-rest-framework.org/) - a powerful and flexible toolkit for building Web APIs.
* [DRF YASG](https://drf-yasg.readthedocs.io/en/stable/readme.html) - Generate real Swagger/OpenAPI 2.0 specifications from a Django Rest Framework API.
* [Mysqlclient](https://pypi.org/project/mysqlclient/) - Library for work MySQLdb.
* [Gunicorn](https://pypi.org/project/gunicorn/) - Gunicorn ‘Green Unicorn’ is a Python WSGI HTTP Server for UNIX.

### Dev depends

* [FlakeHell](https://flakehell.readthedocs.io/) - supports all flake8 plugins, formatters, and configs.
* [Black](https://pypi.org/project/black/) - python code formatter.
* [Faker](https://faker.readthedocs.io/en/master/) - generate fake data.


## Poetry команды

* **poetry install** - использовать lock-файл для установки всех зависимостей.
* **poetry add [package-name]** - добавить новую зависимость и установить ее в текущем виртуальном окружении.
* **poetry add -D [package-name]** - добавить новую dev-зависимость и установить ее в текущем виртуальном окружении.
* **poetry remove [package-name]** - удалить пакет из виртуальной среды.
* **poetry remove -D [package-name]** - удалить dev-пакет из виртуальной среды.

## Make команды

* **run** - запуск сервера разработки.
* **migrate** - синхронизация состояние базы данных с текущим состоянием моделей и миграций.
* **lint** - проверка правильности кода.
* **shell** - запуск интерактивного интерпретатора.
* **static** - инициализация статических файлов.
* **get-fixtures** - запись списка используемых данных в проекте.
* **fixtures** - запись необходимых данных для проекта.
