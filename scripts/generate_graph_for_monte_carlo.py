from tqdm import tqdm
import pickle

from app.helpers.transform_coord_to_grid import search_coord
from app.helpers.connector_pgsql import PostgresConnector
from app.helpers.find_route import get_route
from app.helpers.speed_map import compute_speed_by_date_for_ship
from scripts.load_data_from_local_file import load_table_lat_lon



def info_by_ships(orders, edges, excel, lat, lon, d_points) -> dict:
    result_dict = {}
    for order in tqdm(orders):
        speed_grid = compute_speed_by_date_for_ship(
            dataframe=excel,
            date=order['date_start_swim'].strftime("%d-%m-%Y"),
            name_ship=order['name_ship'],
            class_ship=order['class_ship'],
            speed_ship=order['speed'],
            icebreaker=True
        )
        for edge in edges:
            start_coords = search_coord(speed_grid, lat, lon, d_points, edge['start_point_id'])
            if start_coords is None:
                continue
            end_coords = search_coord(speed_grid, lat, lon, d_points, edge['end_point_id'])
            if end_coords is None:
                continue
            route, time_required = get_route(speed_grid, start_coords=start_coords, end_coords=end_coords)
            if route is None:
                continue
            result_dict[(order['name_ship'], order['id'], edge['id'])] = [route, time_required]
    return result_dict


def info_by_icebreakers(icebreakers, edges, excel, lat, lon, d_points) -> dict:
    result_dict = {}
    for icebreaker in tqdm(icebreakers):
        speed_grid = compute_speed_by_date_for_ship(
            dataframe=excel,
            date="03.03.2020",
            name_ship=icebreaker['name_icebreaker'],
            class_ship=icebreaker['class_icebreaker'],
            speed_ship=icebreaker['speed'],
            icebreaker=True
        )
        for edge in edges:
            start_coords = search_coord(speed_grid, lat, lon, d_points, edge['start_point_id'])
            if start_coords is None:
                continue
            end_coords = search_coord(speed_grid, lat, lon, d_points, edge['end_point_id'])
            if end_coords is None:
                continue
            route, time_required = get_route(speed_grid, start_coords=start_coords, end_coords=end_coords)
            if route == 0:
                continue
            result_dict[(icebreaker['name_icebreaker'], icebreaker['id'], edge['id'])] = [route, time_required]
    return result_dict

async def compute_graph_for_monte_carlo():
    path_excel = 'data/IntegrVelocity.xlsx'
    excel, lat, lon = load_table_lat_lon(path_excel, return_excel=True)
    conn = PostgresConnector(
        host="localhost", user="test", password="test", dbname="ship_tracking", port=5432
    )
    conn.connect()
    orders = await conn.get_data_async("select * from orders")
    icebreakers = await conn.get_data_async("select * from icebreakers")
    edges = await conn.get_data_async("select * from edges")
    points = await conn.get_data_async("select * from points")
    conn.close()
    d_points = {p['id']: (p['latitude'], p['longitude']) for p in points}
    d_by_ships = info_by_ships(orders, edges, excel, lat, lon, d_points)
    print("result_dict_ships", len(d_by_ships))
    with open('data/result_dict_ships.pickle', 'wb') as f:
        pickle.dump(d_by_ships, f)

    d_by_icebreakers = info_by_icebreakers(icebreakers, edges, excel, lat, lon, d_points)
    print("result_dict_icebreakers", len(d_by_icebreakers))
    with open('data/result_dict_icebreakers.pickle', 'wb') as f:
        pickle.dump(d_by_icebreakers, f)


if __name__ == '__main__':
    import asyncio
    asyncio.run(compute_graph_for_monte_carlo())