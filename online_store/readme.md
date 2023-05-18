Пример интернет магазина с использованием Django

Структура сайта
● Главная страница.
● Каталог с фильтром и сортировкой:
○ Сам каталог товаров.
○ Детальная страница товара, с отзывами.
● Оформление заказа:
○ Корзина.
○ Оформление заказа.
○ Оплата.
● Личный кабинет:
○ Личный кабинет.
○ Профиль.
○ История заказов.
● Административный раздел:
○ Просмотр и редактирование товаров.


Документация по проекту.
Для запуска проекта необходимо:

Установить зависимости:
pip install -r requirements.txt
Выполнить следующие команды:

Команда для создания миграций приложения для базы данных
python manage.py migrate
Команда для запуска приложения:
python manage.py runserver
При создании моделей или их изменении необходимо выполнить следующие команды:
python manage.py makemigrations
python manage.py migrate


Автор
Я!!!