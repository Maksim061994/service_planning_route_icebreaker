from typing import List, Dict, Tuple
import pandas as pd
import networkx as nx
from loguru import logger
from tqdm import tqdm
import itertools

from app.helpers.connector_pgsql import PostgresConnector
from app.helpers.speed_map import find_ship_speed_map
from app.helpers.find_route import get_route
from app.helpers.transform_coord_to_grid import search_coord


class AddOrder:
    def __init__(self, settings):
        self.settings = settings
        self.connector = PostgresConnector(
            host=settings.db_host,
            user=settings.db_user,
            password=settings.db_password,
            dbname=settings.db_name_database,
            port=settings.db_port
        )

    def add_new_order_to_db(self, order_id):
        points = self.__get_points()
        edges = self.__get_edges()
        order = self.__get_order(order_id)
        dates_ices = self.__get_dates_ices()
        params = self.__get_params()
        d_points = {p['id']: (p['latitude'], p['longitude']) for p in points}
        d_name_points = {p['point_name']: p['id'] for p in points}
        date_start_swim = pd.to_datetime(order["date_start_swim"])
        ice_matrix, lat, lon = self.__get_ice_matrix(date_start_swim)
        time_grid_with_icebreaker = find_ship_speed_map(
            df=ice_matrix, name_ship=order["name_ship"], class_ship=order["class_ship"],
            speed_ship=order["speed"], icebreaker=True
        )
        time_grid_without_icebreaker = find_ship_speed_map(
            df=ice_matrix, name_ship=order["name_ship"], class_ship=order["class_ship"],
            speed_ship=order["speed"], icebreaker=False
        )

        up_route_graph = nx.Graph()
        up_route_graph.add_nodes_from(range(len(points)))
        up_route_matrix_edges = []
        coords_point_edges = {}
        for edge in tqdm(edges):
            start_point, end_point = edge["start_point_id"], edge["end_point_id"]
            start_coords = search_coord(time_grid_with_icebreaker, lat, lon, d_points, edge['start_point_id'])
            end_coords = search_coord(time_grid_with_icebreaker, lat, lon, d_points, edge['end_point_id'])
            route, time_required = get_route(time_grid_with_icebreaker, start_coords=start_coords,
                                             end_coords=end_coords)
            if route is None:
                continue
            up_route_matrix_edges.append((start_point, end_point, time_required))
            coords_point_edges[(start_point, end_point)] = (start_coords, end_coords)
            coords_point_edges[(end_point, start_point)] = (end_coords, start_coords)
        up_route_graph.add_weighted_edges_from(up_route_matrix_edges)
        path = []
        try:
            path = nx.astar_path(up_route_graph, d_name_points[order["point_start"]], d_name_points[order["point_end"]])
        except nx.NetworkXNoPath:
            logger.warning(f"nx.NetworkXNoPath - {order['id']}")
        except nx.NodeNotFound:
            logger.warning(f"nx.NodeNotFound - {order['id']}")
        start_point_id = None
        end_point_id = None
        path_start_route_clean_water = None
        path_end_route_clean_water = None
        time_swim_self = None
        time_swim_icebreaker = None
        time_all_order = None
        full_path = None
        new_date_start_swim = date_start_swim.strftime("%Y-%m-%d")
        status = 1
        if len(path) > 0:
            index_start_new_point, time_add = self.__search_new_point(
                time_grid_without_icebreaker, coords_point_edges, path
            )
            start_point_id = path[index_start_new_point]
            reverse_path = path[::-1]
            index_end_new_point, time_minus = self.__search_new_point(
                time_grid_without_icebreaker, coords_point_edges, reverse_path
            )
            end_point_id = reverse_path[index_end_new_point]
            index_end_point_id = path.index(end_point_id)

            path_start_route_clean_water = path[:index_start_new_point]
            path_start_route_clean_water = '{' + ','.join(map(str, path_start_route_clean_water)) + '}'

            path_end_route_clean_water = path[index_end_point_id:]
            path_end_route_clean_water = '{' + ','.join(map(str, path_end_route_clean_water)) + '}'

            full_path = '{' + ','.join(map(str, path)) + '}'
            new_date_start_swim = (date_start_swim + pd.Timedelta(hours=time_add)).strftime("%Y-%m-%d")
            time_swim_self = time_add + time_minus
            time_swim_icebreaker = nx.path_weight(up_route_graph, path[index_start_new_point:index_end_point_id+1], weight='weight')
            time_all_order = time_swim_self + time_swim_icebreaker
        self.__save_order_to_db(
            order_id, new_date_start_swim, start_point_id, end_point_id, full_path,
            path_start_route_clean_water, path_end_route_clean_water,
            time_swim_self, time_swim_icebreaker, time_all_order,
            status
        )
        if self.__not_exist_order_id_in_ice_map(order_id):
            result_graph = self.__make_data_for_graph(
                dates_ships_state_ice=dates_ices, dates_start=params["date_start"], order=order,
                points=points, edges=edges, d_points=d_points
            )
            self.__save_order_to_graph(result_graph)
        return time_all_order

    def add_new_icebreaker_to_db(self, icebreaker_id):
        if not self.__not_exist_icebreaker_id_in_ice_map(icebreaker_id):
            points = self.__get_points()
            edges = self.__get_edges()
            icebreaker = self.__get_icebreaker(icebreaker_id)
            dates_ices = self.__get_dates_ices()
            d_points = {p['id']: (p['latitude'], p['longitude']) for p in points}
            result_graph = self.__make_data_for_graph_icebreaker(
                dates_ships_state_ice=dates_ices, icebreaker=icebreaker,
                points=points, edges=edges, d_points=d_points
            )
            self.__save_order_to_graph(result_graph)

    def __get_icebreaker(self, icebreaker_id: int) -> Dict:
        self.connector.connect()
        icebreakers= self.connector.get_data_sync(f"select * from icebreakers where id = {icebreaker_id}")
        self.connector.close()
        if len(icebreakers) == 0:
            raise Exception("Icebreaker not found")
        return icebreakers[0]

    def __not_exist_icebreaker_id_in_ice_map(self, icebreaker_id):
        query = f"""
            SELECT COUNT(*) as count FROM graph_ships WHERE order_id = {icebreaker_id} and type = 1;
        """
        self.connector.connect()
        count = self.connector.get_data_sync(query)
        self.connector.close()
        return count[0]["count"] == 0

    def __not_exist_order_id_in_ice_map(self, order_id: int) -> bool:
        query = f"""
            SELECT COUNT(*) as count FROM graph_ships WHERE order_id = {order_id} and type = 0;
        """
        self.connector.connect()
        count = self.connector.get_data_sync(query)
        self.connector.close()
        return count[0]["count"] == 0

    def __make_data_for_graph_icebreaker(self, dates_ships_state_ice, icebreaker, points, edges, d_points):
        result_list = []
        for date_ships_state_ice in tqdm(dates_ships_state_ice):
            ice_matrix, lat, lon = self.__get_ice_matrix(date_ships_state_ice)
            speed_grid = find_ship_speed_map(
                df=ice_matrix, name_ship=icebreaker["name_icebreaker"], class_ship=icebreaker["class_icebreaker"],
                speed_ship=icebreaker["speed"], icebreaker=True
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
                result_list.append((icebreaker["id"], combinations[0], combinations[1], date_ships_state_ice, 1, total_time))
        return result_list

    def __save_order_to_graph(self, result_graph):
        self.connector.connect()
        for k in result_graph:
            order_id = k[0]
            points_start_id = k[1]
            points_end_id = k[2]
            datetime = k[3]
            type_ship = k[4]
            time_swim = k[5]
            query = f"""
                    INSERT INTO graph_ships (order_id, points_start_id, points_end_id, datetime, type, time_swim)
                    VALUES ({order_id}, {points_start_id}, {points_end_id}, '{datetime}', {type_ship}, {time_swim})
                """
            self.connector.execute_query(query)
        self.connector.close()

    def __make_data_for_graph(self, dates_ships_state_ice, dates_start, order, points, edges, d_points):
        result_list = []
        for date_ships_state_ice in tqdm(dates_ships_state_ice):
            ice_matrix, lat, lon = self.__get_ice_matrix(date_ships_state_ice)
            speed_grid = find_ship_speed_map(
                df=ice_matrix, name_ship=order["name_ship"], class_ship=order["class_ship"],
                speed_ship=order["speed"], icebreaker=True
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
                result_list.append((order["id"], combinations[0], combinations[1], date_ships_state_ice, 0, total_time))
        return result_list

    def __save_order_to_db(
            self, order_id, date_start_swim, start_point_id, end_point_id, path,
            path_start_route_clean_water, path_end_route_clean_water,
            time_swim_self, time_swim_icebreaker, time_all_order,
            status
    ):
        query = f"""
            UPDATE route_orders
            SET 
            point_start_id_icebreaker = {start_point_id}, 
            date_start_swim = '{date_start_swim}',
            point_end_id_icebreaker = {end_point_id},
            time_swim_self = {time_swim_self},
            time_swim_with_icebreaker = {time_swim_icebreaker},
            time_all_order = {time_all_order},
            full_route = '{path}',
            part_start_route_clean_water = '{path_start_route_clean_water}',
            part_end_route_clean_water = '{path_end_route_clean_water}',
            status = {status}
            WHERE order_id = {order_id};
        """
        self.connector.connect()
        self.connector.execute_query(query)
        self.connector.close()

    def __get_dates_ices(self) -> List:
        query_table = f"""
            SELECT DISTINCT date FROM ice_map;
        """
        self.connector.connect()
        dates_ices = self.connector.get_data_sync(query_table)
        self.connector.close()
        return [d["date"] for d in dates_ices]

    @staticmethod
    def __search_new_point(time_grid_without_icebreaker: pd.DataFrame, coords_point_edges: dict, path: list):
        start_index_point = 0
        time_add = 0
        while start_index_point < len(path) - 2:
            start_point_id = path[start_index_point]
            end_point_id = path[start_index_point + 1]
            start_coords, end_coords = coords_point_edges[(start_point_id, end_point_id)]
            route, time_required = get_route(time_grid_without_icebreaker, start_coords=start_coords,
                                             end_coords=end_coords)
            if route is None:
                return start_index_point, time_add
            start_index_point += 1
            time_add += time_required
        return start_index_point + 1, time_add

    def __get_ice_matrix(self, date_start: pd.Timestamp) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        lat_table = self.__get_coord_df("lat")
        lon_table = self.__get_coord_df("lon")
        date_for_search = self.__get_date_for_search(date_start)
        ice_map = self.__get_ice_matrix_by_date(date_for_search)
        return ice_map, lat_table, lon_table

    def __get_ice_matrix_by_date(self, date: pd.Timestamp) -> pd.DataFrame:
        query_table = f"""
            SELECT row_index, column_index, value FROM ice_map WHERE date = TIMESTAMP '{date}';
        """
        self.connector.connect()
        ice_matrix = self.connector.get_data_sync(query_table)
        self.connector.close()
        ice_matrix = pd.DataFrame(ice_matrix)
        unique_row_index = ice_matrix["row_index"].unique()
        values = list()
        for i, row_index in enumerate(unique_row_index):
            data_row = (
                ice_matrix[ice_matrix["row_index"] == row_index]
                .sort_values(by="column_index")["value"]
                .values
            )
            values.append(data_row)
        return pd.DataFrame(values)

    def __get_date_for_search(self, date_start: pd.Timestamp) -> pd.Timestamp:
        query_table = f"""
            SELECT MAX(date) as max FROM ice_map WHERE date <= TIMESTAMP '{date_start}';
        """
        self.connector.connect()
        date_for_search = self.connector.get_data_sync(query_table)
        self.connector.close()
        dt = date_for_search[0]["max"]
        if dt is None:
            query_table = f"SELECT MIN(date) as min FROM ice_map;"
            self.connector.connect()
            date_for_search = self.connector.get_data_sync(query_table)
            self.connector.close()
            dt = date_for_search[0]["min"]
        return pd.to_datetime(dt)

    def __get_coord_df(self, name_col):
        query_table = f"""
            SELECT row_index, column_index, {name_col} FROM ice_map
            WHERE date = (SELECT MIN(date) FROM ice_map)
            ORDER BY row_index, column_index;
        """
        self.connector.connect()
        ice_matrix = self.connector.get_data_sync(query_table)
        self.connector.close()
        ice_matrix = pd.DataFrame(ice_matrix)
        unique_row_index = ice_matrix["row_index"].unique()
        values = list()
        for i, row_index in enumerate(unique_row_index):
            data_row = (
                ice_matrix[ice_matrix["row_index"] == row_index]
                .sort_values(by="column_index")[name_col]
                .values
            )
            values.append(data_row)
        return pd.DataFrame(values)

    def __get_points(self) -> List:
        self.connector.connect()
        points = self.connector.get_data_sync("select * from points")
        self.connector.close()
        return points

    def __get_edges(self) -> List:
        self.connector.connect()
        edges = self.connector.get_data_sync("select * from edges")
        self.connector.close()
        return edges

    def __get_params(self) -> Dict:
        self.connector.connect()
        params = self.connector.get_data_sync("select * from parameters")
        self.connector.close()
        p = dict()
        for r in params:
            if r['type'] == 'date':
                p[r['name']] = pd.to_datetime(r['value'])
            else:
                f = eval(r['type'])
                p[r['name']] = f(r['value'])
        return p

    def __get_order(self, order_id: int) -> Dict:
        self.connector.connect()
        order = self.connector.get_data_sync(f"select * from orders where id = {order_id}")
        self.connector.close()
        if len(order) == 0:
            raise Exception("Order not found")
        return order[0]
