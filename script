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
