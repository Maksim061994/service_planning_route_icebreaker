create table edges
(
    id             integer,
    start_point_id integer,
    end_point_id   integer,
    length         double precision,
    rep_id         integer,
    status         integer
);
alter table edges add constraint edges_pk unique (id);
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
    id              integer generated always as identity,
    name_icebreaker name,
    speed           real,
    class           varchar,
    start_position  name
);
alter table icebreakers add constraint icebreakers_pk unique (id);
alter table icebreakers owner to ss;

create table orders
(
    id               integer generated always as identity,
    name_ship        name,
    class_ship       varchar,
    speed            real,
    point_start      name,
    point_end        name,
    date_start_swim  date
);

alter table orders add constraint orders_pk  unique (id);
alter table orders owner to ss;

create table points
(
    id         integer,
    latitude   double precision,
    longitude  double precision,
    point_name name,
    rep_id     integer
);

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


