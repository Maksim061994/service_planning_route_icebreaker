import pandas as pd
import numpy as np
from tqdm import tqdm
import pickle
import networkx as nx
import itertools

from app.helpers.transform_coord_to_grid import search_coord
from app.helpers.connector_pgsql import PostgresConnector
from app.helpers.find_route import get_route
from app.helpers.speed_map import compute_speed_by_date_for_ship
from scripts.load_data_from_local_file import load_table_lat_lon, get_dates_from_xls


def info_by_ships(dates_ships_state_ice, dates_start, orders, edges, points, excel, lat, lon, d_points) -> dict:
    result_dict = {}
    for date_ships_state_ice in tqdm(dates_ships_state_ice):
        send_hours = round((date_ships_state_ice - dates_start).total_seconds() / 3600)
        for order in tqdm(orders):
            speed_grid = compute_speed_by_date_for_ship(
                dataframe=excel,
                date=date_ships_state_ice.strftime("%d-%m-%Y"),
                name_ship=order['name_ship'],
                class_ship=order['class_ship'],
                speed_ship=order['speed'],
                icebreaker=True
            )
            up_route_graph = nx.Graph()
            up_route_graph.add_nodes_from(range(len(points)))
            up_route_matrix_edges = []
            unique_ids = set()
            for edge in edges:
                start_point, end_point = edge["start_point_id"], edge["end_point_id"]
                start_coords = search_coord(speed_grid, lat, lon, d_points, edge['start_point_id'])
                end_coords = search_coord(speed_grid, lat, lon, d_points, edge['end_point_id'])
                route, time_required = get_route(speed_grid, start_coords=start_coords, end_coords=end_coords)
                if route is None:
                    continue
                up_route_matrix_edges.append((start_point, end_point, time_required))
                unique_ids.add(start_point)
                unique_ids.add(end_point)
            up_route_graph.add_weighted_edges_from(up_route_matrix_edges)
            combinations_edges_for_search = list(itertools.combinations(unique_ids, 2))
            for combinations in combinations_edges_for_search:
                try:
                    path = nx.astar_path(up_route_graph, combinations[0], combinations[1])
                except nx.NetworkXNoPath:
                    continue
                except nx.NodeNotFound:
                    continue
                total_time = nx.path_weight(up_route_graph, path, weight='weight')
                result_dict[(order["id"], combinations[0], combinations[1], send_hours, 0)] = total_time
    return result_dict


def info_by_icebreakers(dates_ships_state_ice, dates_start, icebreakers, edges, points, excel, lat, lon, d_points) -> dict:
    result_dict = {}
    for date_ships_state_ice in tqdm(dates_ships_state_ice):
        send_hours = round((date_ships_state_ice - dates_start).total_seconds() / 3600)
        for icebreaker in tqdm(icebreakers):
            speed_grid = compute_speed_by_date_for_ship(
                dataframe=excel,
                date=date_ships_state_ice.strftime("%d-%m-%Y"),
                name_ship=icebreaker['name_icebreaker'],
                class_ship=icebreaker['class_icebreaker'],
                speed_ship=icebreaker['speed'],
                icebreaker=False
            )
            up_route_graph = nx.Graph()
            up_route_graph.add_nodes_from(range(len(points)))
            up_route_matrix_edges = []
            unique_ids = set()
            for edge in edges:
                start_point, end_point = edge["start_point_id"], edge["end_point_id"]
                start_coords = search_coord(speed_grid, lat, lon, d_points, edge['start_point_id'])
                end_coords = search_coord(speed_grid, lat, lon, d_points, edge['end_point_id'])
                route, time_required = get_route(speed_grid, start_coords=start_coords, end_coords=end_coords)
                if route is None:
                    continue
                up_route_matrix_edges.append((start_point, end_point, time_required))
                unique_ids.add(start_point)
                unique_ids.add(end_point)
            up_route_graph.add_weighted_edges_from(up_route_matrix_edges)
            combinations_edges_for_search = list(itertools.combinations(unique_ids, 2))
            for combinations in combinations_edges_for_search:
                try:
                    path = nx.astar_path(up_route_graph, combinations[0], combinations[1])
                except nx.NetworkXNoPath:
                    continue
                except nx.NodeNotFound:
                    continue
                total_time = nx.path_weight(up_route_graph, path, weight='weight')
                result_dict[(icebreaker["id"], combinations[0], combinations[1], send_hours, 1)] = total_time
    return result_dict


async def main():
    # with open("data/result_dict_ships_new.pickle", "rb") as f:
    #     d = pickle.load(f)

    path_excel = 'data/IntegrVelocity.xlsx'
    excel, lat, lon = load_table_lat_lon(path_excel, return_excel=True)
    dates_real_state_ice, dates_ships_state_ice = get_dates_from_xls(excel)
    dates_start = pd.to_datetime("2022-02-27")  # дата начала отсчета

    conn = PostgresConnector(
        host="msk3tis13.vniizht.lan", user="ss", password="ZkJgf68GdPUedVz", dbname="ship_tracking", port=5446
    )
    conn.connect()
    orders = await conn.get_data_async("select * from orders")
    icebreakers = await conn.get_data_async("select * from icebreakers")
    edges = await conn.get_data_async("select * from edges")
    points = await conn.get_data_async("select * from points")
    d_points = {p['id']: (p['latitude'], p['longitude']) for p in points}
    conn.close()

    result_dict = info_by_ships(dates_ships_state_ice, dates_start, orders, edges, points, excel, lat, lon, d_points)
    with open('data/result_dict_ships_new.pickle', 'wb') as f:
        pickle.dump(result_dict, f)

    result_dict = info_by_icebreakers(dates_ships_state_ice, dates_start, icebreakers, edges, points, excel, lat, lon, d_points)
    with open('data/result_dict_icebreakers_new.pickle', 'wb') as f:
        pickle.dump(result_dict, f)


def concat_two_dict():
    with open('data/result_dict_ships_new.pickle', 'rb') as f:
        result_s = pickle.load(f)
    with open('data/result_dict_icebreakers_new.pickle', 'rb') as f:
        result_ib = pickle.load(f)
    result_s.update(result_ib)
    with open('data/result_dict_full.pickle', 'wb') as f:
        pickle.dump(result_s, f)


if __name__ == '__main__':
    concat_two_dict()
    # import asyncio
    # asyncio.run(main())
