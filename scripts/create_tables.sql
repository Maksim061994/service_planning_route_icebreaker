create table edges
(
    id             integer
        constraint edges_pk
            unique,
    start_point_id integer,
    end_point_id   integer,
    length         double precision,
    rep_id         integer,
    status         integer
);

alter table edges owner to test;
alter table edges owner to ss;

create table ice_map
(
    longitude  real,
    latitude   real,
    ice_height real,
    date       date
);

alter table ice_map owner to ss;

create table icebreakers
(
    id integer generated always as identity constraint icebreakers_pk unique,
    name_icebreaker  varchar constraint icebreakers_pk_2 unique,
    speed            real,
    class_icebreaker varchar,
    start_position   varchar
);
alter table icebreakers owner to ss;

create table orders
(
    id              integer generated always as identity
        constraint orders_pk
            unique,
    name_ship       varchar
        constraint orders_pk_2
            unique,
    class_ship      varchar,
    speed           real,
    point_start     varchar
        constraint orders_points_point_name_fk
            references points (point_name),
    point_end       varchar
        constraint orders_points_point_name_fk_2
            references points (point_name),
    date_start_swim date,
    status          integer default 0 not null
);

comment on column orders.status is 'Статус исполнения заявки (0-обрабатывается; 1-взята в работу; 2-исполнена)';
alter table orders owner to ss;

create table points
(
    id         integer
        constraint points_pk_2
            unique,
    latitude   double precision,
    longitude  double precision,
    point_name varchar
        constraint points_pk
            unique,
    rep_id     integer
);

alter table points
    owner to test;


alter table points owner to ss;


CREATE TABLE route_orders (
    id SERIAL PRIMARY KEY,
    time INT NOT NULL,
    grid_coords INT[],
    geo_coords FLOAT8[],
    edge_id INT NOT NULL,
    status INT CHECK (status IN (0, 1, 2)),
    speed FLOAT8,
    assigned_icebreaker INT,
    order_id INT NOT NULL,
    FOREIGN KEY (edge_id) REFERENCES edges(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE route_icebreakers (
    id SERIAL PRIMARY KEY,
    time INT NOT NULL,
    grid_coords INT[],
    geo_coords FLOAT8[],
    status INT CHECK (status IN (0, 1, 2)),
    speed FLOAT8,
    assigned_ships INT[],
    icebreaker_id INT NOT NULL,
    FOREIGN KEY (icebreaker_id) REFERENCES icebreakers(id)
);

CREATE TABLE parameters
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL
);

CREATE TABLE ice_map
(
    row_index INT NOT NULL,
    column_index INT NOT NULL,
    date DATE NOT NULL,
    lat FLOAT8 NOT NULL,
    lon FLOAT8 NOT NULL,
    value FLOAT8,
    PRIMARY KEY (row_index, column_index, date)
);

CREATE INDEX idx_date
ON ice_map (date);

CREATE TABLE graph_ships
(
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    points_start_id INT NOT NULL,
    points_end_id INT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    type INT CHECK(type IN (0, 1)) NOT NULL,
    time_swim FLOAT8 NOT NULL,
    FOREIGN KEY (points_start_id) REFERENCES points(id),
    FOREIGN KEY (points_end_id) REFERENCES points(id)
);
