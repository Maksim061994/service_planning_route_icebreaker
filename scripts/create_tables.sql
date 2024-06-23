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


create table route_orders
(
    id  integer generated always as identity
        constraint route_orders_id
            unique,
    order_id                     integer
        constraint orders_id_fk
            references orders (id),
    point_start_id               integer
        constraint orders_points_point_id_fk
            references points (id),
    point_end_id                 integer
        constraint orders_points_point_id_fk_2
            references points (id),
    point_start_id_icebreaker    integer
        constraint orders_points_point_id_fk_3
            references points (id),
    point_end_id_icebreaker      integer
        constraint orders_points_point_id_fk_4
            references points (id),
    date_start_swim              date,
    full_route                   integer[],
    part_start_route_clean_water integer[],
    part_end_route_clean_water   integer[],
    time_swim_self               integer,
    time_swim_with_icebreaker    integer,
    time_all_order               integer,
    status                       integer
        constraint route_orders_status_check
            check (status = ANY (ARRAY [0, 1])),
    type_route                       integer
        constraint route_orders_type_route_check
            check (status = ANY (ARRAY [0, 1]))
);


create table route_icebreakers
(
    id                  integer generated always as identity
        constraint route_icebreakers_id
            unique,
    icebreaker_id       integer          not null
        references icebreakers (id),
    action_type         integer
        constraint route_icebreakers_action_type_check
            check (action_type = ANY (ARRAY [0, 1])),
    nested_array_orders numeric[][],
    points_start_id     integer          not null
        references points (id),
    points_end_id       integer          not null
        references points (id),
    datetime_start      timestamp        not null,
    datetime_end        timestamp        not null,
    duration_hours      double precision not null,
    order_ids           numeric[]
);

comment on column route_icebreakers.action_type is 'Статус исполнения заявки (0-плывет за заявкой; 1-плывет с заявкой)';


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

create table route_icebreakers_detail
(
    id                  integer generated always as identity
        constraint route_icebreakers_detail_id
            unique,
    icebreaker_id       integer          not null
        references icebreakers (id),
    action_type         integer
        constraint route_icebreakers_detail_action_type_check
            check (action_type = ANY (ARRAY [0, 1])),
    nested_array_orders numeric[][],
    points_start_id     integer          not null
        references points (id),
    points_end_id       integer          not null
        references points (id),
    datetime_work      timestamp        not null,
    datetime_start      timestamp        not null,
    datetime_end        timestamp        not null,
    count_ships      integer          not null
);

comment on column route_icebreakers_detail.action_type is 'Статус исполнения заявки (0-плывет за заявкой; 1-плывет с заявкой)';

create table time_process_orders
(
    id  integer generated always as identity
        constraint time_process_orders_id
            unique,
    order_id                     integer
        constraint orders_id_fk
            references orders (id),
    time_swim_self               float,
    time_swim_with_icebreaker    float,
    time_wait_icebreaker         float
);