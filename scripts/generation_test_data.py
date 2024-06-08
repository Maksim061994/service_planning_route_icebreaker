from app.helpers.connector_pgsql import PostgresConnector
from app.helpers.transform_coord_to_grid import grid_to_coord
from scripts.load_data_from_local_file import load_table_lat_lon


def repeat_tuples(tuples_list, repeat_count=60):
    return [list(t) for t in tuples_list for _ in range(repeat_count)]


def generate_test_data_route_orders(lan, lot):
    """
    Generate test data for table route_orders
    struct
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
    :return:
    """
    test_grid_coords_one_order = [
        (58, 77), (58, 76), (59, 75), (60, 74), (61, 73), (61, 72), (61, 71), (61, 70), (61, 69), (61, 68), (61, 67),
        (61, 66), (62, 65), (63, 64), (64, 63), (65, 62), (66, 61), (67, 60), (68, 59), (69, 58), (70, 57), (71, 56),
        (71, 61)
    ]
    test_coord_grid_one_order = []
    for lat, lon in test_grid_coords_one_order:
        test_coord_grid_one_order.append(grid_to_coord(lan, lot, lat, lon))
    grid_coords = repeat_tuples(test_grid_coords_one_order, repeat_count=120)
    geo_coords = repeat_tuples(test_coord_grid_one_order, repeat_count=120)
    edge_id = 1
    status = 2
    speed = 10
    assigned_icebreaker = 1
    order_id = 1

    conn = PostgresConnector(
        host="localhost", user="test", password="test", dbname="ship_tracking", port=5432
    )
    conn.connect()
    for i in range(len(grid_coords)):
        query = f"""
            INSERT INTO route_orders (time, grid_coords, geo_coords, edge_id, status, speed, assigned_icebreaker, order_id)
            VALUES ({i}, ARRAY{grid_coords[i]}, ARRAY{geo_coords[i]}, {edge_id}, {status}, {speed}, {assigned_icebreaker}, {order_id})
        """
        conn.execute_query(query)
    conn.close()


if __name__ == "__main__":
    lan, lot = load_table_lat_lon('data/IntegrVelocity.xlsx')
    generate_test_data_route_orders(lan, lot)
