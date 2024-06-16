import pandas as pd
from tqdm import tqdm
import pickle
import networkx as nx
from typing import Tuple

from app.helpers.transform_coord_to_grid import search_coord
from app.helpers.connector_pgsql import PostgresConnector
from app.helpers.find_route import get_route
from app.helpers.speed_map import compute_speed_by_date_for_ship
from scripts.load_data_from_local_file import load_table_lat_lon


def search_new_point(time_grid_without_icebreaker: pd.DataFrame, coords_point_edges: dict, path: list):
    start_index_point = 0
    time_add = 0
    while start_index_point < len(path) - 2:
        start_point_id = path[start_index_point]
        end_point_id = path[start_index_point + 1]
        start_coords, end_coords = coords_point_edges[(start_point_id, end_point_id)]
        route, time_required = get_route(time_grid_without_icebreaker, start_coords=start_coords, end_coords=end_coords)
        if route is None:
            return start_index_point, time_add
        start_index_point += 1
        time_add += time_required
    return start_index_point + 1, time_add


def make_clean_orders(dates_start, orders, edges, points, excel, lat, lon, d_points, d_name_points) -> Tuple:
    result = []
    paths_orders = []
    for order in tqdm(orders):
        date_start_swim = pd.to_datetime(order["date_start_swim"])
        send_hours = round((date_start_swim - dates_start).total_seconds() / 3600)
        time_grid_with_icebreaker = compute_speed_by_date_for_ship(
            dataframe=excel,
            date=date_start_swim.strftime("%d-%m-%Y"),
            name_ship=order['name_ship'],
            class_ship=order['class_ship'],
            speed_ship=order['speed'],
            icebreaker=True
        )
        time_grid_without_icebreaker = compute_speed_by_date_for_ship(
            dataframe=excel,
            date=date_start_swim.strftime("%d-%m-%Y"),
            name_ship=order['name_ship'],
            class_ship=order['class_ship'],
            speed_ship=order['speed'],
            icebreaker=False
        )
        up_route_graph = nx.Graph()
        up_route_graph.add_nodes_from(range(len(points)))
        up_route_matrix_edges = []
        coords_point_edges = {}
        for edge in edges:
            start_point, end_point = edge["start_point_id"], edge["end_point_id"]
            start_coords = search_coord(time_grid_with_icebreaker, lat, lon, d_points, edge['start_point_id'])
            end_coords = search_coord(time_grid_with_icebreaker, lat, lon, d_points, edge['end_point_id'])
            route, time_required = get_route(time_grid_with_icebreaker, start_coords=start_coords, end_coords=end_coords)
            if route is None:
                continue
            up_route_matrix_edges.append((start_point, end_point, time_required))
            coords_point_edges[(start_point, end_point)] = (start_coords, end_coords)
            coords_point_edges[(end_point, start_point)] = (end_coords, start_coords)
        up_route_graph.add_weighted_edges_from(up_route_matrix_edges)
        try:
            path = nx.astar_path(up_route_graph, d_name_points[order["point_start"]], d_name_points[order["point_end"]])
        except nx.NetworkXNoPath:
            print("nx.NetworkXNoPath", order["id"])
            continue
        except nx.NodeNotFound:
            print("nx.NodeNotFound", order["id"])
            continue

        index_start_new_point, time_add = search_new_point(time_grid_without_icebreaker, coords_point_edges, path)
        start_point_id = path[index_start_new_point]
        send_hours += time_add

        reverse_path = path[::-1]
        index_end_new_point, time_minus = search_new_point(time_grid_without_icebreaker, coords_point_edges, reverse_path)
        end_point_id = reverse_path[index_end_new_point]
        index_end_point_id = path.index(end_point_id)

        if index_end_point_id > index_start_new_point:
            result.append([start_point_id, end_point_id, send_hours, order["id"]])
        else:
            print("index_end_point_id < index_start_new_point", order["id"])
        paths_orders.append(
            {
                "order_id": order["id"],
                "time_add": time_add,
                "time_minus": time_minus,
                "with_icebreaker": path,
                "start_point_id": start_point_id,
                "end_point_id": end_point_id,
                "start_without_icebreaker": path[:index_start_new_point],
                "end_without_icebreaker": path[index_end_point_id:]
            }
        )
    return result, paths_orders


async def main():

    path_excel = 'data/IntegrVelocity.xlsx'
    excel, lat, lon = load_table_lat_lon(path_excel, return_excel=True)
    dates_start = pd.to_datetime("2022-02-27")  # дата начала отсчета

    conn = PostgresConnector(
        host="localhost", user="test", password="test",
        # host="msk3tis13.vniizht.lan", user="ss", password="ZkJgf68GdPUedVz",
        dbname="ship_tracking", port=5432
    )
    conn.connect()
    orders = await conn.get_data_async("select * from orders order by id")
    edges = await conn.get_data_async("select * from edges")
    points = await conn.get_data_async("select * from points")
    d_points = {p['id']: (p['latitude'], p['longitude']) for p in points}
    d_name_points = {p['point_name']: p['id'] for p in points}
    conn.close()

    result_dict, paths_orders = make_clean_orders(dates_start, orders, edges, points, excel, lat, lon, d_points, d_name_points)
    with open('data/clean_orders.pickle', 'wb') as f:
        pickle.dump(result_dict, f)

    with open('data/paths_orders.pickle', 'wb') as f:
        pickle.dump(paths_orders, f)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
