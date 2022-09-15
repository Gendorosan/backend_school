Приложение упаковано в Docker-compose
Для проверки я оставлю всё это включенным, чтобы не надо было ничего разворачивать.
Можно сразу присылать запросы на "https://final-2011.usr.yandex-academy.ru"
Если вдруг docker-compose будет выключен, то необходимо выполнить следующую команду в папке проекта
sudo docker-compose up -d

Разворачивать вот так:

1. Клонировать репозиторий
git clone https://github.com/Gendorosan/backend_school.git
user: gendorosan
password: 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

2. Создать docker-compose
sudo docker-compose build 
sudo docker-compose up -d

3. Создать таблицы
Далее необходимо подключиться к бд и создать таблицы

sudo psql -h 0.0.0.0 -d MyLittleYandexDisk -U postgres -p 5432
password = ' ' - Пароль пробел

create table if not exists item
(
    id varchar(255),
    type varchar(6),
    url varchar(255),
    parentId varchar(255),
    size int,
    primary key (id)
);

create table if not exists history
(
    id serial,
    itemId varchar(255),
    operation varchar,
    date timestamp,
    primary key (id),
    foreign key (itemId) references item(id)
);

Сервер готов принимать запросы. Вы великолепны
