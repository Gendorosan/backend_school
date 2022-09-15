Бэкенд приложения MyLittleYandexDisk, написанный на aiohttp

Тяжелый жизненный путь пришедшего к нам в гости http запроса начинается с файла routes.py, 
который отвечает за прием http запросов и переправляет их в handler.py.
Данные запроса достаются и отправляются в файл validation_check.py, дальше, если входные данные валидны,
мы уходим в файл database.py, который отвечает за взаимодействия приложения с базой данных

В файле database.py есть 5 главных функций, которые вызываются напрямую из handlers.py

1.import_items
2.delete_element
3.get_nodes
4.get_items_updated_in_last_day
5.get_item_history

Я постарался сделать код как можно красивее, поэтому в этих 5 функциях нет прямого обращения к базе данных,
мы обращаемся к бд в остальных 20 функциях)

Наша база данных состоит из двух табличек - item и history, что позволяет нам хранить всю историю любого элемента
В каждой функции, которая как-то изменяет записи в базе данных вызывается функция create_history,
записывает эти изменения. При удалении файла мы стираем его историю.

Приложение упаковано в Docker-compose Для проверки я оставлю всё это включенным, чтобы не надо было ничего разворачивать.
Можно сразу присылать запросы на "https://final-2011.usr.yandex-academy.ru"
Если вдруг docker-compose будет выключен, то необходимо выполнить следующую команду в папке проекта

sudo docker-compose up -d

Разворачивать вот так:

Клонировать репозиторий git clone https://github.com/Gendorosan/backend_school.git
user: gendorosan

password: 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

Создать docker-compose 
sudo docker-compose build 
sudo docker-compose up -d

Создать таблицы Далее необходимо подключиться к бд и создать таблицы

sudo psql -h 0.0.0.0 -d MyLittleYandexDisk -U postgres -p 5432

password = ' ' - Пароль пробел (без кавычек)

create table if not exists item ( id varchar(255), type varchar(6), url varchar(255), parentId varchar(255), size int, primary key (id) );

create table if not exists history ( id serial, itemId varchar(255), operation varchar, date timestamp, primary key (id), foreign key (itemId) references item(id) );

Сервер готов принимать запросы. Вы великолепны
